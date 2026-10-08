import re
from dataclasses import dataclass

CLASSIFIER_VERSION = "rules-v1"


@dataclass(frozen=True)
class ClassificationReason:
    rule: str
    contribution: int
    message: str


@dataclass(frozen=True)
class ClassificationResult:
    score: int
    classification: str
    reasons: tuple[ClassificationReason, ...]
    version: str = CLASSIFIER_VERSION


POSITIVE_TITLE_RULES: tuple[tuple[str, str, int, str], ...] = (
    (r"\bnew grad(?:uate)?\b", "title.new_grad", 35, "Title identifies a new-graduate role"),
    (r"\bentry[ -]level\b", "title.entry_level", 30, "Title identifies an entry-level role"),
    (r"\bjunior\b", "title.junior", 25, "Title contains a junior-level indicator"),
    (r"\bassociate\b", "title.associate", 20, "Title contains an associate-level indicator"),
    (
        r"\bsoftware (?:engineer|developer) (?:i|1)\b",
        "title.level_one",
        25,
        "Title identifies a level-one software engineering role",
    ),
)

NEGATIVE_TITLE_RULES: tuple[tuple[str, str, int, str], ...] = (
    (r"\bprincipal\b", "title.principal", -70, "Title contains a principal-level indicator"),
    (r"\bstaff\b", "title.staff", -65, "Title contains a staff-level indicator"),
    (r"\bsenior\b|\bsr\.?\b", "title.senior", -60, "Title contains a senior-level indicator"),
    (r"\blead\b", "title.lead", -50, "Title contains a lead-level indicator"),
    (r"\bmanager\b", "title.manager", -60, "Title contains a management-level indicator"),
    (r"\bdirector\b", "title.director", -55, "Title contains a director-level indicator"),
    (r"\bvp\b|\bvice president\b", "title.vice_president", -50, "Title contains a vice president-level indicator"),
    (r"\bceo\b|\bchief executive officer\b", "title.ceo", -80, "Title contains a CEO-level indicator"),
    (r"\bintern\b", "title.intern", -20, "Title contains an intern-level indicator"),
    (r"\bjunior\b", "title.junior", -10, "Title contains a junior-level indicator")

)


def classification_band(score: int) -> str:
    if score >= 70:
        return "likely"
    if score >= 40:
        return "uncertain"
    return "unlikely"


def classify_entry_level(
    *,
    raw_title: str,
    description: str,
    minimum_years_experience: float | None = None,
    maximum_years_experience: float | None = None,
) -> ClassificationResult:
    """Score early-career suitability and return every contributing rule."""
    title = raw_title.lower()
    combined = f"{raw_title}\n{description}".lower()
    reasons: list[ClassificationReason] = []
    score = 45

    for pattern, rule, contribution, message in POSITIVE_TITLE_RULES:
        if re.search(pattern, title):
            reasons.append(ClassificationReason(rule, contribution, message))
            score += contribution

    negative_title_found = False
    for pattern, rule, contribution, message in NEGATIVE_TITLE_RULES:
        if re.search(pattern, title):
            negative_title_found = True
            reasons.append(ClassificationReason(rule, contribution, message))
            score += contribution

    minimum = minimum_years_experience
    maximum = maximum_years_experience
    if minimum is not None or maximum is not None:
        upper_bound = maximum if maximum is not None else minimum
        lower_bound = minimum if minimum is not None else 0
        if upper_bound is not None and upper_bound <= 2:
            contribution = 30
            message = f"Experience range ({lower_bound:g}–{upper_bound:g} years) fits 0–2 years"
            reasons.append(ClassificationReason("experience.zero_to_two", contribution, message))
            score += contribution
        elif lower_bound is not None and lower_bound >= 5:
            contribution = -60
            message = f"Minimum experience requirement is {lower_bound:g} years"
            reasons.append(ClassificationReason("experience.five_plus", contribution, message))
            score += contribution
        elif lower_bound is not None and lower_bound > 2:
            contribution = -30
            message = f"Minimum experience requirement is {lower_bound:g} years"
            reasons.append(ClassificationReason("experience.above_two", contribution, message))
            score += contribution
    else:
        years = [int(value) for value in re.findall(r"\b(\d{1,2})\s*\+?\s*years?", combined)]
        if years and max(years) >= 5:
            contribution = -50
            reasons.append(
                ClassificationReason(
                    "description.five_plus_years",
                    contribution,
                    "Description contains a requirement of at least 5 years",
                )
            )
            score += contribution
        elif re.search(r"\b(?:0\s*[-–]\s*[12]|1\+)\s*years?", combined):
            contribution = 25
            reasons.append(
                ClassificationReason(
                    "description.early_career_experience",
                    contribution,
                    "Description contains an early-career experience range",
                )
            )
            score += contribution

    if re.search(r"\bbachelor(?:'s)?(?: degree)?\b", combined):
        contribution = 5
        reasons.append(
            ClassificationReason(
                "education.bachelors",
                contribution,
                "Description accepts a bachelor's-level qualification",
            )
        )
        score += contribution

    if not negative_title_found:
        reasons.append(
            ClassificationReason(
                "title.no_senior_keywords",
                0,
                "No senior-level keywords were detected in the title",
            )
        )

    score = max(0, min(100, score))
    return ClassificationResult(score, classification_band(score), tuple(reasons))
