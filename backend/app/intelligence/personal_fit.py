"""Conservative, evidence-based matching; no resume or external AI service needed."""

import re
from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    graduation_date: date = date(2026, 5, 1)
    skills: list[str] = Field(default_factory=list)


class FitFinding(BaseModel):
    category: Literal["graduation", "skills"]
    status: Literal["satisfied", "conflicting", "unknown"]
    contribution: int
    evidence: str
    message: str


class PersonalFit(BaseModel):
    version: str = "personal-fit-v1"
    eligibility: Literal["likely_eligible", "likely_ineligible", "needs_review"]
    score: int
    findings: list[FitFinding]


SKILLS = {
    "python": ("python",),
    "java": ("java",),
    "javascript": ("javascript", "js"),
    "typescript": ("typescript", "ts"),
    "sql": ("sql",),
    "postgresql": ("postgresql", "postgres"),
    "react": ("react", "react.js", "reactjs"),
    "node.js": ("node.js", "nodejs"),
    "aws": ("aws", "amazon web services"),
    "docker": ("docker",),
    "kubernetes": ("kubernetes", "k8s"),
    "c++": ("c++",),
    "c#": ("c#", "c sharp"),
    "git": ("git",),
}
MONTHS = {name.lower(): index for index, name in enumerate(
    ("January", "February", "March", "April", "May", "June", "July", "August",
     "September", "October", "November", "December"), 1
)}
DATE_PATTERN = re.compile(r"\b(" + "|".join(MONTHS) + r")\s+(20\d{2})\b", re.I)


def mentioned_skills(text: str) -> set[str]:
    return {name for name, aliases in SKILLS.items() if any(
        re.search(r"(?<![\w+#])" + re.escape(alias) + r"(?![\w+#])", text, re.I)
        for alias in aliases
    )}


def analyze_personal_fit(description: str, profile: CandidateProfile) -> PersonalFit:
    findings: list[FitFinding] = []
    known = mentioned_skills("\n".join(profile.skills))
    section = "unknown"
    # Keep punctuation in technology names such as Node.js and C++ intact.
    for raw in re.split(r"\n+|(?<=[.!?])\s+|;\s*", description):
        evidence = raw.strip(" \t-*•\r")
        if not evidence:
            continue
        text = evidence.lower()
        heading = text.rstrip(":")
        if heading in {"minimum qualifications", "required qualifications", "requirements",
                       "basic qualifications", "preferred qualifications", "nice to have",
                       "responsibilities", "benefits"}:
            section = ("preferred" if heading in {"preferred qualifications", "nice to have"}
                       else "required" if "qualifications" in heading or heading == "requirements"
                       else "unknown")
            continue

        if re.search(r"\bgraduat\w*\b", text):
            dates = [(int(m.group(2)), MONTHS[m.group(1).lower()])
                     for m in DATE_PATTERN.finditer(text)]
            candidate = (profile.graduation_date.year, profile.graduation_date.month)
            satisfied = None
            if len(dates) == 2 and re.search(r"\bbetween\b|\bto\b|[-–—]", text):
                if dates[0] <= dates[1]:
                    satisfied = dates[0] <= candidate <= dates[1]
            elif len(dates) == 1:
                if re.search(r"\bby\b|\bon or before\b|\bno later than\b", text):
                    satisfied = candidate <= dates[0]
                elif re.search(r"\bon or after\b|\bno earlier than\b", text):
                    satisfied = candidate >= dates[0]
                elif re.search(r"\bafter\b", text):
                    satisfied = candidate > dates[0]
                elif re.search(r"\bbefore\b", text):
                    satisfied = candidate < dates[0]
            optional = section == "preferred" or bool(
                re.search(r"\bpreferred\b|\bencouraged\b", text)
            )
            status = ("unknown" if satisfied is None or optional else
                      "satisfied" if satisfied else "conflicting")
            findings.append(FitFinding(
                category="graduation", status=status,
                contribution=-40 if status == "conflicting" else 0,
                evidence=evidence,
                message=(f"Graduation {profile.graduation_date:%B %Y}: " +
                         {"unknown": "review this graduation language manually",
                          "satisfied": "meets the stated date requirement",
                          "conflicting": "falls outside the stated date requirement"}[status]),
            ))

        skills = mentioned_skills(text)
        if not skills:
            continue
        learning = bool(re.search(r"\b(?:learn|teach|training|not required|no .*required)\b", text))
        preferred = bool(re.search(r"\bpreferred\b|\bnice to have\b|\ba plus\b", text))
        required = bool(re.search(r"\brequired\b|\bmust\b", text))
        strength = ("unknown" if learning else "preferred" if preferred else
                    "required" if required else section)
        groups = [skills] if re.search(r"\bor\b|\bany of\b|\bone of\b", text) else [
            {skill} for skill in sorted(skills)
        ]
        for group in groups:
            matched = sorted(group & known)
            status = "satisfied" if matched and strength != "unknown" else "unknown"
            contribution = (5 if strength == "required" else 2) if status == "satisfied" else 0
            findings.append(FitFinding(
                category="skills", status=status, contribution=contribution, evidence=evidence,
                message=(f"{strength.capitalize()} skills ({', '.join(sorted(group))}): " +
                         (f"profile records {', '.join(matched)}" if matched else
                          "not recorded in profile; experience is unknown")),
            ))
    graduation = [f.status for f in findings if f.category == "graduation"]
    eligibility = ("likely_ineligible" if "conflicting" in graduation else
                   "likely_eligible" if graduation and all(s == "satisfied" for s in graduation)
                   else "needs_review")
    # Repeated mentions must not inflate fit.
    unique = {(f.category, f.message): f.contribution for f in findings}
    score = max(0, min(100, 50 + sum(unique.values())))
    return PersonalFit(eligibility=eligibility, score=score, findings=findings)
