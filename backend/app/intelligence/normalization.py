import re
import unicodedata


def normalize_text(value: str) -> str:
    """Create a stable comparison value without changing the source text."""
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", ascii_value.lower()).split())


def normalize_company(company: str) -> str:
    normalized = normalize_text(company)
    suffix_pattern = r"\b(?:incorporated|inc|llc|ltd|limited|corporation|corp)\b$"
    return re.sub(suffix_pattern, "", normalized).strip()


def normalize_location(location: str) -> str:
    return normalize_text(location)
