import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import yaml
from typer.testing import CliRunner
from src.main import app

class TestInteractiveProjectsManagement(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create initial public.yaml with a project
        self.initial_public = {
            "projects": [
                {
                    "name": "Old Project",
                    "description": "Old Description",
                    "url": "http://old.com",
                    "highlights": ["Old Highlight"]
                }
            ]
        }
        os.makedirs("inputs", exist_ok=True)
        with open("inputs/public.yaml", "w") as f:
            yaml.dump(self.initial_public, f)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)

    @patch('src.main.TerminalMenu')
    @patch('builtins.input')
    def test_edit_existing_project(self, mock_input, mock_menu):
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        
        # Main Menu: [Basics, Work, Education, Skills, Projects, Save, Exit]
        # Projects Menu: [Add Project, Edit Project, Remove Project, Back]
        # Edit Project Select Menu: [Old Project, Back]
        # Project Edit Menu: [Project Name, Description, URL, Highlights, Back]

        mock_instance.show.side_effect = [
            4, # 1. Main Menu -> Projects
            1, # 2. Projects Menu -> Edit Project
            0, # 3. Select Project -> "Old Project"
            0, # 4. Project Edit Menu -> Name
            3, # 5. Project Edit Menu -> Highlights
            4, # 6. Project Edit Menu -> Back
            3, # 7. Projects Menu -> Back
            5  # 8. Main Menu -> Save and Exit
        ]

        mock_input.side_effect = [
            "New Project", # New Name
            "New Highlight 1", "New Highlight 2", "" # New highlights list
        ]

        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        
        # Verify changes in draft_public.yaml
        with open("draft_public.yaml", "r") as f:
            data = yaml.safe_load(f)
            self.assertEqual(data["projects"][0]["name"], "New Project")
            self.assertEqual(data["projects"][0]["highlights"], ["New Highlight 1", "New Highlight 2"])
            self.assertEqual(data["projects"][0]["description"], "Old Description") # Should be unchanged

    @patch('src.main.TerminalMenu')
    def test_remove_existing_project(self, mock_menu):
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        
        # Main Menu: [Basics, Work, Education, Skills, Projects, Save, Exit]
        # Projects Menu: [Add Project, Edit Project, Remove Project, Back]
        # Remove Project Select Menu: [Old Project, Back]

        mock_instance.show.side_effect = [
            4, # 1. Main Menu -> Projects
            2, # 2. Projects Menu -> Remove Project
            0, # 3. Select Project -> "Old Project"
            3, # 4. Projects Menu -> Back
            5  # 5. Main Menu -> Save and Exit
        ]

        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        
        # Verify removal in draft_public.yaml
        with open("draft_public.yaml", "r") as f:
            data = yaml.safe_load(f)
            self.assertEqual(len(data["projects"]), 0)

if __name__ == '__main__':
    unittest.main()
