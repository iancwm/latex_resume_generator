import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import yaml
from typer.testing import CliRunner
from src.main import app

class TestInteractiveEducation(unittest.TestCase):
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
    def test_generate_interactive_education_entry(self, mock_input, mock_menu):
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        
        # Main Menu: [Basics, Work, Education, Save, Exit] -> Choice 2
        # Education Menu: [Add, Edit, Remove, Back] -> Choice 0
        # Entry Edit Menu: [Inst, Area, Loc, Start, End, Score, Honors, Courses, Back]
        
        mock_instance.show.side_effect = [
            2, # Main Menu -> Education
            0, # Education Menu -> Add Entry
            0, # Entry Edit Menu -> Institution
            6, # Entry Edit Menu -> Honors
            8, # Entry Edit Menu -> Back
            3, # Education Menu -> Back
            3  # Main Menu -> Save and Exit
        ]

        mock_input.side_effect = [
            "Harvard", # Institution
            "Dean's List", # Honor 1
            "Scholar",     # Honor 2
            ""             # Sentinel
        ]

        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)

        with open("draft_public.yaml", "r") as f:
            data = yaml.safe_load(f)
            self.assertEqual(len(data["education"]), 1)
            self.assertEqual(data["education"][0]["institution"], "Harvard")
            self.assertEqual(data["education"][0]["honors"], ["Dean's List", "Scholar"])

if __name__ == '__main__':
    unittest.main()
