from fastapi.testclient import TestClient


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
