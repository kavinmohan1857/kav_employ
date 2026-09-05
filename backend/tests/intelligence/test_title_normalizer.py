import pytest

from app.intelligence.title_normalizer import normalize_title


@pytest.mark.parametrize(
    ("raw_title", "expected"),
    [
        ("Software Engineer I", "Software Engineer"),
        ("Associate Software Developer", "Software Engineer"),
        ("Junior Backend Engineer", "Backend Engineer"),
        ("Graduate Full-Stack Engineer", "Full Stack Engineer"),
        ("iOS Engineer", "Mobile Engineer"),
    ],
)
def test_normalizes_common_title_variants(raw_title: str, expected: str) -> None:
    assert normalize_title(raw_title) == expected
