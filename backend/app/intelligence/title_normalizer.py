import re

from app.intelligence.normalization import normalize_text

TITLE_FAMILIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Full Stack Engineer", ("full stack", "fullstack")),
    ("Backend Engineer", ("backend", "back end")),
    ("Frontend Engineer", ("frontend", "front end")),
    ("Mobile Engineer", ("mobile", "ios", "android")),
    ("DevOps Engineer", ("devops", "site reliability", "sre")),
    ("Data Engineer", ("data engineer",)),
    ("Data Scientist", ("data scientist", "ml engineer", "machine learning engineer")),
    ("Machine Learning Engineer", ("machine learning engineer", "ml engineer")),
    ("Product Manager", ("product manager", "pm")),
    ("Designer", ("designer", "ux", "ui")),
    ("QA Engineer", ("qa", "quality assurance", "test engineer")),
    ("Intern", ("intern", "internship")),
    ("Director", ("director",)),
    ("Vice President", ("vp", "vice president")),
    ("CEO", ("ceo", "chief executive officer"))
)


def normalize_title(raw_title: str) -> str:
    title = normalize_text(raw_title)

    for canonical, signals in TITLE_FAMILIES:
        if any(signal in title for signal in signals):
            return canonical

    software_pattern = r"\b(?:software|application)\s+(?:engineer|developer)\b"
    if re.search(software_pattern, title) or title == "developer":
        return "Software Engineer"

    return " ".join(word.capitalize() for word in title.split())
