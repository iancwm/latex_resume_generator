import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import yaml
from typer.testing import CliRunner
from src.main import app

class TestInteractiveValidation(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)

    @patch('src.main.TerminalMenu')
    @patch('builtins.input')
    def test_validation_required_fields(self, mock_input, mock_menu):
        """Test that required fields like 'Name' cannot be empty."""
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        
        # Scenario:
        # 1. Main Menu -> Basics (0)
        # 2. Basics Menu -> Name (0)
        # 3. User inputs "" (empty - invalid)
        # 4. User inputs "Valid Name" (valid)
        # 5. Basics Menu -> Back (5)
        # 6. Main Menu -> Save and Exit (5)
        
        mock_instance.show.side_effect = [
            0, # 1. Main Menu -> Basics
            0, # 2. Basics Menu -> Name
            5, # 5. Basics Menu -> Back
            5  # 6. Main Menu -> Save and Exit
        ]

        mock_input.side_effect = [
            "",           # First attempt: empty (invalid)
            "Valid Name"  # Second attempt: valid
        ]

        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        # Expecting a validation error message in stdout (to be implemented)
        self.assertIn("cannot be empty", result.stdout.lower())

        with open("drafts/private_valid.yaml", "r") as f:
            data = yaml.safe_load(f)
            self.assertEqual(data["basics"]["name"], "Valid Name")

    @patch('src.main.TerminalMenu')
    @patch('builtins.input')
    def test_validation_date_format(self, mock_input, mock_menu):
        """Test that dates must be in YYYY-MM or 'Present' format."""
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        
        # Scenario:
        # 1. Main Menu -> Work Experience (1)
        # 2. Work Menu -> Add Entry (0)
        # 3. Entry Edit Menu -> Start Date (3)
        # 4. User inputs "2023" (invalid)
        # 5. User inputs "2023-13" (invalid month)
        # 6. User inputs "2023-01" (valid)
        # 7. Entry Edit Menu -> End Date (4)
        # 8. User inputs "not-a-date" (invalid)
        # 9. User inputs "Present" (valid)
        # 10. Entry Edit Menu -> Back (6)
        # 11. Work Menu -> Back (3)
        # 12. Main Menu -> Save and Exit (5)

        mock_instance.show.side_effect = [
            1, # 1. Main Menu -> Work Experience
            0, # 2. Work Menu -> Add Entry
            3, # 3. Entry Edit Menu -> Start Date
            4, # 7. Entry Edit Menu -> End Date
            6, # 10. Entry Edit Menu -> Back
            3, # 11. Work Menu -> Back
            5  # 12. Main Menu -> Save and Exit
        ]

        mock_input.side_effect = [
            "2023",       # Invalid start date
            "2023-13",    # Invalid month
            "2023-01",    # Valid start date
            "not-a-date", # Invalid end date
            "Present"     # Valid end date
        ]

        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        # Expecting validation error messages (to be implemented)
        self.assertIn("invalid date format", result.stdout.lower())

        with open("drafts/public_anonymous.yaml", "r") as f:
            data = yaml.safe_load(f)
            work_entry = data["work"][0]
            self.assertEqual(work_entry["startDate"], "2023-01")
            self.assertEqual(work_entry["endDate"], "Present")

    @patch('src.main.TerminalMenu')
    @patch('builtins.input')
    def test_validation_bullet_point_consistency(self, mock_input, mock_menu):
        """Test that bullet points within a list must have consistent punctuation."""
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        
        # Scenario:
        # 1. Main Menu -> Work Experience (1)
        # 2. Work Menu -> Add Entry (0)
        # 3. Entry Edit Menu -> Summary (5)
        # 4. User inputs "Item one." (has period)
        # 5. User inputs "Item two" (no period - inconsistent)
        # 6. User inputs "" (sentinel)
        # 7. System detects inconsistency and asks to fix.
        #    (Assuming we ask "Do you want to add periods to all? [y/n]" or similar)
        #    Let's say we prompt for a choice to fix it.
        # 8. User chooses to add periods to all (e.g. inputs 'y' or similar)
        # 9. Entry Edit Menu -> Back (6)
        # 10. Work Menu -> Back (3)
        # 11. Main Menu -> Save and Exit (5)

        mock_instance.show.side_effect = [
            1, # 1. Main Menu -> Work Experience
            0, # 2. Work Menu -> Add Entry
            5, # 3. Entry Edit Menu -> Summary
            6, # 9. Entry Edit Menu -> Back
            3, # 10. Work Menu -> Back
            5  # 11. Main Menu -> Save and Exit
        ]

        mock_input.side_effect = [
            "Item one.",   # Item 1 (period)
            "Item two",    # Item 2 (no period)
            "",            # Sentinel
            "y"            # Choose to fix by adding periods (hypothetical prompt)
        ]

        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertIn("inconsistent punctuation", result.stdout.lower())

        with open("drafts/public_anonymous.yaml", "r") as f:
            data = yaml.safe_load(f)
            summary = data["work"][0]["summary"]
            self.assertEqual(summary[0], "Item one.")
            self.assertEqual(summary[1], "Item two.")

    @patch('src.main.TerminalMenu')
    @patch('builtins.input')
    def test_validation_bullet_point_consistency_remove(self, mock_input, mock_menu):
        """Test that bullet points can be consistently unpunctuated."""
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        
        mock_instance.show.side_effect = [
            1, # 1. Main Menu -> Work Experience
            0, # 2. Work Menu -> Add Entry
            5, # 3. Entry Edit Menu -> Summary
            6, # 9. Entry Edit Menu -> Back
            3, # 10. Work Menu -> Back
            5  # 11. Main Menu -> Save and Exit
        ]

        mock_input.side_effect = [
            "Item one.",   # Item 1 (period)
            "Item two",    # Item 2 (no period)
            "",            # Sentinel
            "n",           # Choose NOT to add periods
            "y"            # Choose to remove periods
        ]

        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertIn("inconsistent punctuation", result.stdout.lower())

        with open("drafts/public_anonymous.yaml", "r") as f:
            data = yaml.safe_load(f)
            summary = data["work"][0]["summary"]
            self.assertEqual(summary[0], "Item one")
            self.assertEqual(summary[1], "Item two")

if __name__ == '__main__':
    unittest.main()
