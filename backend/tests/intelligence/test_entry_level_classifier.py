from app.intelligence.entry_level_classifier import classify_entry_level


def test_scores_clear_entry_level_signals_and_explains_them() -> None:
    result = classify_entry_level(
        raw_title="Software Engineer I",
        description="Bachelor's degree accepted.",
        minimum_years_experience=0,
        maximum_years_experience=2,
    )

    assert result.score == 100
    assert result.classification == "likely"
    assert {reason.rule for reason in result.reasons} >= {
        "title.level_one",
        "experience.zero_to_two",
        "education.bachelors",
        "title.no_senior_keywords",
    }


def test_senior_title_overrides_incidental_junior_language() -> None:
    result = classify_entry_level(
        raw_title="Senior Software Engineer",
        description="You will mentor junior engineers and lead projects. Requires 7+ years.",
    )

    assert result.score == 0
    assert result.classification == "unlikely"
    assert {reason.rule for reason in result.reasons} >= {
        "title.senior",
        "description.five_plus_years",
    }


def test_neutral_posting_is_uncertain() -> None:
    result = classify_entry_level(
        raw_title="Software Engineer",
        description="Build reliable web services with a collaborative product team.",
    )

    assert result.score == 45
    assert result.classification == "uncertain"


def test_scores_experience_above_two_as_negative() -> None:
    result = classify_entry_level(
        raw_title="Software Engineer",
        description="Build APIs.",
        minimum_years_experience=3,
        maximum_years_experience=4,
    )

    assert result.score == 15
    assert "experience.above_two" in {reason.rule for reason in result.reasons}


def test_detects_early_career_range_in_description() -> None:
    result = classify_entry_level(
        raw_title="Software Engineer",
        description="Candidates should have 0-2 years of professional experience.",
    )

    assert result.score == 70
    assert result.classification == "likely"
    assert "description.early_career_experience" in {reason.rule for reason in result.reasons}
