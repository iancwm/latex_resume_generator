import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import yaml
from typer.testing import CliRunner
from src.main import app

class TestInteractiveWork(unittest.TestCase):
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
    def test_generate_interactive_work_entry(self, mock_input, mock_menu):
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        
        # Menu structure logic:
        # Main Menu: [Basics, Work Experience (Public), Education (Public), Save and Exit, Exit without Saving]
        # Choices: 0, 1, 2, 3, 4
        
        # Work Menu: [Add Entry, Edit Entry, Remove Entry, Back]
        # Choices: 0, 1, 2, 3
        
        # Entry Edit Menu: [Company, Position, Location, Start Date, End Date, Summary, Back]
        # Choices: 0, 1, 2, 3, 4, 5, 6

        mock_instance.show.side_effect = [
            1, # 1. Main Menu -> Work Experience
            0, # 2. Work Menu -> Add Entry
            0, # 3. Entry Edit Menu -> Company
            1, # 4. Entry Edit Menu -> Position
            5, # 5. Entry Edit Menu -> Summary
            6, # 6. Entry Edit Menu -> Back
            3, # 7. Work Menu -> Back (Wait, Work Menu has 4 options, Back is index 3)
            5  # 8. Main Menu -> Save and Exit
        ]

        mock_input.side_effect = [
            "New Corp", # For Company
            "Lead Dev", # For Position
            "Feature 1", # Summary item 1
            "Feature 2", # Summary item 2
            ""           # Sentinel to finish summary
        ]

        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Saved interactive drafts", result.stdout)

        with open("drafts/public_anonymous.yaml", "r") as f:
            data = yaml.safe_load(f)
            self.assertEqual(len(data["work"]), 1)
            self.assertEqual(data["work"][0]["company"], "New Corp")
            self.assertEqual(data["work"][0]["position"], "Lead Dev")
            self.assertEqual(data["work"][0]["summary"], ["Feature 1", "Feature 2"])

if __name__ == '__main__':
    unittest.main()
