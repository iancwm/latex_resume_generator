"""
Validators for TUI Editor input validation.

Pure functions for validating form inputs in the resume generator.
"""

import re
from typing import Tuple, Optional


def validate_required(value: str, field_name: str) -> bool:
    """
    Check if a required field is not empty.

    Args:
        value: The value to validate
        field_name: Name of the field (for error messages)

    Returns:
        True if value is a non-empty string, False otherwise
    """
    if value is None:
        return False
    if not isinstance(value, str):
        return False
    return bool(value.strip())


def validate_date(value: str) -> bool:
    """
    Validate date format for resume dates.

    Accepts:
        - YYYY-MM format (e.g., "2023-01", "2024-12")
        - "Present" (case-insensitive)

    Args:
        value: The date string to validate

    Returns:
        True if valid date format, False otherwise
    """
    if value is None:
        return False
    if not isinstance(value, str):
        return False

    # Check for "Present" keyword (case-insensitive)
    if value.strip().lower() == "present":
        return True

    # Check for YYYY-MM format
    pattern = r"^\d{4}-(0[1-9]|1[0-2])$"
    return bool(re.match(pattern, value.strip()))


def validate_bullet_consistency(
    bullets: list[str],
) -> Tuple[bool, Optional[str]]:
    """
    Check if bullet points have consistent punctuation.

    All bullets should either:
    - All end with periods
    - All not end with periods

    Args:
        bullets: List of bullet point strings

    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if consistent or empty
        - (False, "error message") if inconsistent
    """
    if not bullets:
        return True, None

    # Filter out empty strings and strip whitespace
    cleaned_bullets = [b.strip() for b in bullets if b and b.strip()]

    if len(cleaned_bullets) <= 1:
        return True, None

    # Check if each bullet ends with a period
    ends_with_period = [b.endswith(".") for b in cleaned_bullets]

    # Check for consistency
    all_with_periods = all(ends_with_period)
    all_without_periods = all(not p for p in ends_with_period)

    if all_with_periods or all_without_periods:
        return True, None

    return False, "Bullet points have inconsistent punctuation"
