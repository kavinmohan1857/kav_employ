import hashlib


def build_duplicate_fingerprint(
    *, normalized_company: str, normalized_title: str, normalized_location: str
) -> str:
    candidate_key = "|".join((normalized_company, normalized_title, normalized_location))
    return hashlib.sha256(candidate_key.encode("utf-8")).hexdigest()
