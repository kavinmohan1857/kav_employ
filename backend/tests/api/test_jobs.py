from fastapi.testclient import TestClient


def create_job(
    client: TestClient,
    *,
    title: str = "Software Engineer",
    company: str = "Example Company",
    location: str = "Chicago, IL",
    description: str = "Build software.",
    **overrides: object,
) -> dict:
    payload = {
        "raw_title": title,
        "raw_company": company,
        "raw_location": location,
        "description": description,
        **overrides,
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_and_retrieve_job(client: TestClient) -> None:
    payload = {
        "raw_title": "Associate Software Developer",
        "raw_company": "Example Corp.",
        "raw_location": "Chicago, IL",
        "description": "Entry-level role. Bachelor's degree and 0-2 years of experience.",
        "employment_type": "full_time",
        "minimum_years_experience": 0,
        "maximum_years_experience": 2,
        "salary_min": 75000,
        "salary_max": 90000,
        "salary_currency": "usd",
    }

    create_response = client.post("/api/v1/jobs", json=payload)

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["raw_title"] == payload["raw_title"]
    assert created["normalized_title"] == "Software Engineer"
    assert created["normalized_company"] == "example"
    assert created["normalized_location"] == "chicago il"
    assert created["entry_level_classification"] == "likely"
    assert created["salary_currency"] == "USD"
    assert len(created["duplicate_fingerprint"]) == 64

    get_response = client.get(f"/api/v1/jobs/{created['id']}")

    assert get_response.status_code == 200
    assert get_response.json() == created


def test_get_missing_job_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/jobs/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found"}


def test_rejects_invalid_ranges(client: TestClient) -> None:
    response = client.post(
        "/api/v1/jobs",
        json={
            "raw_title": "Software Engineer",
            "raw_company": "Example",
            "raw_location": "Chicago",
            "description": "Build software.",
            "minimum_years_experience": 3,
            "maximum_years_experience": 1,
        },
    )

    assert response.status_code == 422


def test_rejects_whitespace_only_required_fields(client: TestClient) -> None:
    response = client.post(
        "/api/v1/jobs",
        json={
            "raw_title": "   ",
            "raw_company": "Example",
            "raw_location": "Chicago",
            "description": "Build software.",
        },
    )

    assert response.status_code == 422


def test_lists_jobs_with_pagination(client: TestClient) -> None:
    create_job(client, title="Junior Software Engineer")
    create_job(client, title="Senior Software Engineer")
    create_job(client, title="Backend Engineer")

    response = client.get("/api/v1/jobs", params={"limit": 2, "offset": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["limit"] == 2
    assert body["offset"] == 1
    assert len(body["items"]) == 2


def test_filters_jobs_by_normalized_fields_and_suitability(client: TestClient) -> None:
    matching = create_job(
        client,
        title="Associate Software Developer",
        company="Acme Corp.",
        location="Chicago, IL",
        minimum_years_experience=0,
        maximum_years_experience=2,
    )
    create_job(
        client,
        title="Senior Software Engineer",
        company="Other Company",
        location="New York, NY",
        minimum_years_experience=7,
    )

    response = client.get(
        "/api/v1/jobs",
        params={
            "company": "ACME INC",
            "title": "software developer",
            "location": "Chicago",
            "suitability": "likely",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == matching["id"]


def test_sorts_jobs_by_entry_level_score(client: TestClient) -> None:
    create_job(client, title="Senior Software Engineer", minimum_years_experience=7)
    create_job(
        client,
        title="Junior Software Engineer",
        minimum_years_experience=0,
        maximum_years_experience=2,
    )

    response = client.get(
        "/api/v1/jobs",
        params={"sort_by": "entry_level_score", "sort_order": "desc"},
    )

    scores = [job["entry_level_score"] for job in response.json()["items"]]
    assert scores == sorted(scores, reverse=True)


def test_rejects_invalid_list_parameters(client: TestClient) -> None:
    assert client.get("/api/v1/jobs", params={"limit": 101}).status_code == 422
    assert client.get("/api/v1/jobs", params={"offset": -1}).status_code == 422
    assert client.get("/api/v1/jobs", params={"sort_by": "company"}).status_code == 422


def test_updates_job_and_recalculates_derived_fields(client: TestClient) -> None:
    created = create_job(
        client,
        title="Senior Software Engineer",
        company="Example Corp.",
        minimum_years_experience=7,
    )

    response = client.patch(
        f"/api/v1/jobs/{created['id']}",
        json={
            "raw_title": "Junior Backend Engineer",
            "raw_company": "Renamed LLC",
            "minimum_years_experience": 0,
            "maximum_years_experience": 2,
        },
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["normalized_title"] == "Backend Engineer"
    assert updated["normalized_company"] == "renamed"
    assert updated["entry_level_classification"] == "likely"
    assert updated["duplicate_fingerprint"] != created["duplicate_fingerprint"]
    assert updated["first_seen_at"] == created["first_seen_at"]


def test_update_can_clear_optional_fields(client: TestClient) -> None:
    created = create_job(client, source_url="https://example.com/job")

    response = client.patch(f"/api/v1/jobs/{created['id']}", json={"source_url": None})

    assert response.status_code == 200
    assert response.json()["source_url"] is None


def test_update_rejects_null_required_field(client: TestClient) -> None:
    created = create_job(client)

    response = client.patch(f"/api/v1/jobs/{created['id']}", json={"raw_title": None})

    assert response.status_code == 422


def test_update_rejects_range_conflicting_with_stored_value(client: TestClient) -> None:
    created = create_job(client, salary_min=80_000, salary_max=100_000)

    response = client.patch(f"/api/v1/jobs/{created['id']}", json={"salary_max": 70_000})

    assert response.status_code == 422
    assert response.json() == {"detail": "The update creates an invalid job"}


def test_update_missing_job_returns_404(client: TestClient) -> None:
    response = client.patch(
        "/api/v1/jobs/00000000-0000-0000-0000-000000000000",
        json={"raw_title": "Junior Software Engineer"},
    )

    assert response.status_code == 404


def test_deletes_job(client: TestClient) -> None:
    created = create_job(client)

    delete_response = client.delete(f"/api/v1/jobs/{created['id']}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert client.get(f"/api/v1/jobs/{created['id']}").status_code == 404


def test_delete_missing_job_returns_404(client: TestClient) -> None:
    response = client.delete("/api/v1/jobs/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
