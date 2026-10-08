import pytest

from app.intelligence.personal_fit import CandidateProfile, analyze_personal_fit


@pytest.mark.parametrize("description", [
    "Must graduate by May 2026.",
    "Must graduate on or before May 2026.",
    "Must graduate no earlier than May 2026.",
    "Must graduate between May 2026 and December 2026.",
    "Must graduate between January 2026 and May 2026.",
])
def test_graduation_boundaries_are_inclusive(description):
    result = analyze_personal_fit(description, CandidateProfile())
    assert result.eligibility == "likely_eligible"
    assert result.findings[0].contribution == 0


@pytest.mark.parametrize("description", [
    "Must graduate between December 2027 and May 2026.",
    "Preferred qualifications:\nMust graduate after December 2026.",
    "Must graduate in Spring 2027.",
])
def test_ambiguous_or_optional_dates_do_not_disqualify(description):
    result = analyze_personal_fit(description, CandidateProfile())
    assert result.eligibility == "needs_review"
    assert result.score == 50


def test_unknown_skills_are_not_treated_as_missing_experience():
    result = analyze_personal_fit("AWS and Docker required.", CandidateProfile())
    assert len(result.findings) == 2
    assert all(f.status == "unknown" and f.contribution == 0 for f in result.findings)
    assert result.score == 50


def test_graduation_conflict_remains_visible_despite_skill_matches():
    result = analyze_personal_fit(
        "Must graduate after December 2026. Python and Java required.",
        CandidateProfile(skills=["Python", "Java"]),
    )
    assert result.eligibility == "likely_ineligible"
    assert result.score == 20
    assert result.findings[0].evidence == "Must graduate after December 2026."


def test_responsibilities_do_not_inherit_required_section():
    result = analyze_personal_fit(
        "Requirements:\nPython\nResponsibilities:\nDocker",
        CandidateProfile(skills=["Python", "Docker"]),
    )
    assert [f.status for f in result.findings] == ["satisfied", "unknown"]


@pytest.mark.parametrize("profile", [
    {"graduation_date": "invalid"}, {"skills": "Python"},
])
def test_analysis_api_rejects_invalid_profiles(client, profile):
    response = client.post("/api/v1/intelligence/personal-fit", json={
        "description": "Python required.", "profile": profile,
    })
    assert response.status_code == 422


def test_existing_jobs_use_current_profile_and_updated_description(client, monkeypatch):
    from app.core.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "candidate_skills", [])
    job = client.post("/api/v1/jobs", json={
        "raw_title": "Engineer", "raw_company": "Example", "raw_location": "Chicago",
        "description": "Python required.",
    }).json()
    assert job["personal_fit"]["findings"][0]["status"] == "unknown"
    monkeypatch.setattr(settings, "candidate_skills", ["Python"])
    current = client.get(f"/api/v1/jobs/{job['id']}").json()
    assert current["personal_fit"]["findings"][0]["status"] == "satisfied"
    assert current["entry_level_score"] == job["entry_level_score"]
    updated = client.patch(f"/api/v1/jobs/{job['id']}", json={
        "description": "Must graduate after December 2026.",
    }).json()
    assert updated["personal_fit"]["eligibility"] == "likely_ineligible"
    assert all(f["category"] == "graduation" for f in updated["personal_fit"]["findings"])


@pytest.mark.parametrize(("text", "eligibility"), [
    ("Must graduate between December 2026 and June 2027.", "likely_ineligible"),
    ("Must have graduated by June 2027.", "likely_eligible"),
    ("Must graduate after May 2026.", "likely_ineligible"),
    ("Must graduate on or after May 2026.", "likely_eligible"),
    ("Graduation in 2027 preferred.", "needs_review"),
    ("Recent graduates encouraged.", "needs_review"),
])
def test_graduation(text, eligibility):
    result = analyze_personal_fit(text, CandidateProfile())
    assert result.eligibility == eligibility
    assert result.findings[0].evidence == text


def test_skills_alternatives_aliases_and_preference():
    profile = CandidateProfile(skills=["Postgres", "Python"])
    result = analyze_personal_fit(
        "Python, Java, or C++ required. PostgreSQL preferred. AWS required.", profile
    )
    assert [f.status for f in result.findings] == ["satisfied", "satisfied", "unknown"]
    assert [f.contribution for f in result.findings] == [5, 2, 0]


def test_no_false_java_match_or_learning_penalty():
    result = analyze_personal_fit(
        "JavaScript required. You will learn Kubernetes. Java not required.",
        CandidateProfile(skills=["Java"]),
    )
    assert all(f.status == "unknown" and f.contribution == 0 for f in result.findings)


def test_section_context_and_repetition():
    result = analyze_personal_fit(
        "Minimum qualifications:\nPython\nPython\nPreferred qualifications:\nDocker",
        CandidateProfile(skills=["Python", "Docker"]),
    )
    assert result.score == 57


def test_api_accepts_profile_and_job_responses_include_fit(client):
    response = client.post("/api/v1/intelligence/personal-fit", json={
        "description": "Python required.", "profile": {"skills": ["Python"]},
    })
    assert response.status_code == 200
    assert response.json()["score"] == 55
    job = client.post("/api/v1/jobs", json={
        "raw_title": "Engineer", "raw_company": "Example", "raw_location": "Chicago",
        "description": "Must graduate after December 2026.",
    })
    assert job.status_code == 201
    assert job.json()["personal_fit"]["eligibility"] == "likely_ineligible"
