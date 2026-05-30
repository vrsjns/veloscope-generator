"""Tests for get_zodiac_sign, which expects ISO YYYY-MM-DD birth dates."""
import pytest
from batch_prepare_input import get_zodiac_sign


@pytest.mark.parametrize(
    "birthdate,expected",
    [
        ("2001-09-03", "Virgo"),    # Blanka Vas
        ("1998-09-21", "Virgo"),    # Tadej Pogačar
        ("1986-05-25", "Gemini"),   # Geraint Thomas (day > 12)
        ("2002-01-13", "Capricorn"),
        # Cusp boundaries
        ("2000-01-20", "Aquarius"),  # first day of Aquarius
        ("2000-01-19", "Capricorn"),  # last day of Capricorn
        ("2000-12-22", "Capricorn"),  # first day of Capricorn
        ("2000-12-21", "Sagittarius"),  # last day of Sagittarius
    ],
)
def test_returns_correct_sign(birthdate: str, expected: str) -> None:
    """A valid ISO birthdate maps to the correct zodiac sign."""
    assert get_zodiac_sign(birthdate) == expected


@pytest.mark.parametrize(
    "bad",
    [
        "garbage",
        "03.09.2001",   # old DD.MM.YYYY format is no longer accepted
        "2001/09/03",
        "",
    ],
)
def test_unparseable_returns_unknown(bad: str) -> None:
    """An unparseable birthdate string yields "Unknown"."""
    assert get_zodiac_sign(bad) == "Unknown"
