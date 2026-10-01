from fastapi.testclient import TestClient


def create_job(client: TestClient, *, title: str, minimum_years: int) -> dict:
    response = client.post(
        "/api/v1/jobs",
        json={
            "raw_title": title,
            "raw_company": "Example Company",
            "raw_location": "Chicago, IL",
            "description": "Build software.",
            "minimum_years_experience": minimum_years,
            "maximum_years_experience": minimum_years,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_dashboard_summarizes_jobs_and_submitted_applications(client: TestClient) -> None:
    likely_job = create_job(client, title="Junior Software Engineer", minimum_years=1)
    senior_job = create_job(client, title="Senior Software Engineer", minimum_years=7)
    saved_job = create_job(client, title="Backend Engineer", minimum_years=3)

    client.put(
        f"/api/v1/jobs/{likely_job['id']}/application",
        json={"status": "applied"},
    )
    client.put(
        f"/api/v1/jobs/{senior_job['id']}/application",
        json={"status": "rejected"},
    )
    client.put(
        f"/api/v1/jobs/{saved_job['id']}/application",
        json={"status": "saved"},
    )

    response = client.get("/api/v1/dashboard/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_jobs": 3,
        "likely_entry_level_jobs": 1,
        "jobs_added_this_week": 3,
        "applications_submitted": 2,
    }


def test_empty_dashboard_returns_zeroes(client: TestClient) -> None:
    response = client.get("/api/v1/dashboard/summary")

    assert response.status_code == 200
    assert response.json() == {
        "total_jobs": 0,
        "likely_entry_level_jobs": 0,
        "jobs_added_this_week": 0,
        "applications_submitted": 0,
    }
