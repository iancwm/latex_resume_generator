import unittest
from src.validators import validate_required, validate_date, validate_bullet_consistency


class TestValidateRequired(unittest.TestCase):
    """Tests for validate_required function."""

    def test_valid_non_empty_string(self):
        """Test that non-empty strings return True."""
        self.assertTrue(validate_required("John Doe", "Name"))
        self.assertTrue(validate_required("  Content  ", "Field"))

    def test_empty_string_returns_false(self):
        """Test that empty strings return False."""
        self.assertFalse(validate_required("", "Name"))

    def test_whitespace_only_returns_false(self):
        """Test that whitespace-only strings return False."""
        self.assertFalse(validate_required("   ", "Name"))
        self.assertFalse(validate_required("\t\n", "Field"))

    def test_none_returns_false(self):
        """Test that None values return False."""
        self.assertFalse(validate_required(None, "Name"))


class TestValidateDate(unittest.TestCase):
    """Tests for validate_date function."""

    def test_valid_yyyy_mm_format(self):
        """Test valid YYYY-MM date formats."""
        self.assertTrue(validate_date("2023-01"))
        self.assertTrue(validate_date("2024-12"))
        self.assertTrue(validate_date("2020-06"))

    def test_valid_present_keyword(self):
        """Test that 'Present' is accepted (case-insensitive)."""
        self.assertTrue(validate_date("Present"))
        self.assertTrue(validate_date("present"))
        self.assertTrue(validate_date("PRESENT"))

    def test_invalid_date_formats(self):
        """Test invalid date formats return False."""
        self.assertFalse(validate_date("2023"))
        self.assertFalse(validate_date("01-2023"))
        self.assertFalse(validate_date("2023/01"))
        self.assertFalse(validate_date("Jan 2023"))
        self.assertFalse(validate_date("2023-1"))
        self.assertFalse(validate_date("23-01"))

    def test_invalid_month_values(self):
        """Test that invalid month values return False."""
        self.assertFalse(validate_date("2023-00"))
        self.assertFalse(validate_date("2023-13"))
        self.assertFalse(validate_date("2023-99"))

    def test_empty_string_returns_false(self):
        """Test that empty strings return False."""
        self.assertFalse(validate_date(""))

    def test_none_returns_false(self):
        """Test that None values return False."""
        self.assertFalse(validate_date(None))


class TestValidateBulletConsistency(unittest.TestCase):
    """Tests for validate_bullet_consistency function."""

    def test_all_with_periods_returns_valid(self):
        """Test that all bullets ending with periods are consistent."""
        bullets = ["First item.", "Second item.", "Third item."]
        is_valid, message = validate_bullet_consistency(bullets)
        self.assertTrue(is_valid)
        self.assertIsNone(message)

    def test_all_without_periods_returns_valid(self):
        """Test that all bullets without periods are consistent."""
        bullets = ["First item", "Second item", "Third item"]
        is_valid, message = validate_bullet_consistency(bullets)
        self.assertTrue(is_valid)
        self.assertIsNone(message)

    def test_empty_list_returns_valid(self):
        """Test that empty bullet lists are valid."""
        is_valid, message = validate_bullet_consistency([])
        self.assertTrue(is_valid)
        self.assertIsNone(message)

    def test_single_bullet_returns_valid(self):
        """Test that a single bullet is always valid."""
        is_valid, message = validate_bullet_consistency(["Single item."])
        self.assertTrue(is_valid)
        self.assertIsNone(message)

        is_valid, message = validate_bullet_consistency(["Single item"])
        self.assertTrue(is_valid)
        self.assertIsNone(message)

    def test_mixed_periods_returns_invalid(self):
        """Test that mixed period usage returns invalid with message."""
        bullets = ["First item.", "Second item", "Third item."]
        is_valid, message = validate_bullet_consistency(bullets)
        self.assertFalse(is_valid)
        self.assertIsNotNone(message)
        self.assertIn("inconsistent", message.lower())

    def test_mixed_periods_alternating_returns_invalid(self):
        """Test alternating period pattern returns invalid."""
        bullets = ["Item 1.", "Item 2", "Item 3.", "Item 4"]
        is_valid, message = validate_bullet_consistency(bullets)
        self.assertFalse(is_valid)
        self.assertIsNotNone(message)

    def test_whitespace_handling(self):
        """Test that trailing whitespace is handled correctly."""
        bullets = ["First item.  ", "Second item ."]
        is_valid, message = validate_bullet_consistency(bullets)
        self.assertTrue(is_valid)
        self.assertIsNone(message)

    def test_empty_strings_in_list(self):
        """Test that empty strings in bullet list are handled."""
        bullets = ["Valid item.", "", "Another item."]
        is_valid, message = validate_bullet_consistency(bullets)
        # Empty strings should be ignored in consistency check
        self.assertTrue(is_valid)
        self.assertIsNone(message)


if __name__ == "__main__":
    unittest.main()
