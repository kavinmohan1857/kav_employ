from datetime import datetime

from fastapi.testclient import TestClient


def create_job(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/jobs",
        json={
            "raw_title": "Software Engineer I",
            "raw_company": "Example Company",
            "raw_location": "Chicago, IL",
            "description": "An entry-level engineering role.",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_creates_and_retrieves_saved_application(client: TestClient) -> None:
    job = create_job(client)

    create_response = client.put(
        f"/api/v1/jobs/{job['id']}/application",
        json={"status": "saved", "notes": "Strong fit", "referral": True},
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["job_id"] == job["id"]
    assert created["status"] == "saved"
    assert created["date_applied"] is None
    assert created["notes"] == "Strong fit"
    assert created["referral"] is True

    get_response = client.get(f"/api/v1/jobs/{job['id']}/application")
    assert get_response.status_code == 200
    assert get_response.json() == created


def test_updates_application_and_sets_first_applied_date(client: TestClient) -> None:
    job = create_job(client)
    client.put(f"/api/v1/jobs/{job['id']}/application", json={"status": "saved"})

    update_response = client.put(
        f"/api/v1/jobs/{job['id']}/application",
        json={"status": "interview", "interview_stage": "technical"},
    )

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["status"] == "interview"
    assert updated["interview_stage"] == "technical"
    assert updated["date_applied"] is not None

    second_update = client.put(
        f"/api/v1/jobs/{job['id']}/application",
        json={"status": "offer"},
    )
    assert second_update.status_code == 200
    assert second_update.json()["date_applied"] == updated["date_applied"]


def test_accepts_explicit_date_applied(client: TestClient) -> None:
    job = create_job(client)
    applied_at = "2026-09-10T15:30:00Z"

    response = client.put(
        f"/api/v1/jobs/{job['id']}/application",
        json={"status": "applied", "date_applied": applied_at},
    )

    assert response.status_code == 201
    actual = datetime.fromisoformat(response.json()["date_applied"].replace("Z", "+00:00"))
    expected = datetime.fromisoformat(applied_at.replace("Z", "+00:00"))
    assert actual.replace(tzinfo=None) == expected.replace(tzinfo=None)


def test_rejects_interview_stage_for_non_interview_status(client: TestClient) -> None:
    job = create_job(client)

    response = client.put(
        f"/api/v1/jobs/{job['id']}/application",
        json={"status": "applied", "interview_stage": "technical"},
    )

    assert response.status_code == 422


def test_application_requires_existing_job(client: TestClient) -> None:
    missing_job = "00000000-0000-0000-0000-000000000000"

    assert (
        client.put(f"/api/v1/jobs/{missing_job}/application", json={"status": "saved"}).status_code
        == 404
    )
    assert client.get(f"/api/v1/jobs/{missing_job}/application").status_code == 404
    assert client.delete(f"/api/v1/jobs/{missing_job}/application").status_code == 404


def test_missing_tracking_record_returns_404(client: TestClient) -> None:
    job = create_job(client)

    response = client.get(f"/api/v1/jobs/{job['id']}/application")

    assert response.status_code == 404
    assert response.json() == {"detail": "Application tracking not found"}


def test_deletes_application_without_deleting_job(client: TestClient) -> None:
    job = create_job(client)
    client.put(f"/api/v1/jobs/{job['id']}/application", json={"status": "saved"})

    response = client.delete(f"/api/v1/jobs/{job['id']}/application")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/api/v1/jobs/{job['id']}").status_code == 200
    assert client.get(f"/api/v1/jobs/{job['id']}/application").status_code == 404


def test_deleting_job_removes_application_tracking(client: TestClient) -> None:
    job = create_job(client)
    client.put(f"/api/v1/jobs/{job['id']}/application", json={"status": "saved"})

    assert client.delete(f"/api/v1/jobs/{job['id']}").status_code == 204
    assert client.get(f"/api/v1/jobs/{job['id']}/application").status_code == 404
