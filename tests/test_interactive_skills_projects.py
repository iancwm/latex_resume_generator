import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import yaml
from typer.testing import CliRunner
from src.main import app

class TestInteractiveSkillsProjects(unittest.TestCase):
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
    def test_generate_interactive_skills_projects(self, mock_input, mock_menu):
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        
        # Menu indices need to be updated based on implementation
        # Main Menu: [Basics, Work, Education, Skills, Projects, Save, Exit]
        # Skills Menu: [Add, Edit, Remove, Back]
        # Projects Menu: [Add, Edit, Remove, Back]

        mock_instance.show.side_effect = [
            3, # 1. Main Menu -> Skills (index 3 if I follow logical order)
            0, # 2. Skills Menu -> Add Entry
            0, # 3. Skill Edit Menu -> Category
            1, # 4. Skill Edit Menu -> Keywords
            2, # 5. Skill Edit Menu -> Back
            3, # 6. Skills Menu -> Back
            4, # 7. Main Menu -> Projects
            0, # 8. Projects Menu -> Add Entry
            0, # 9. Project Edit Menu -> Name
            3, # 10. Project Edit Menu -> Highlights
            4, # 11. Project Edit Menu -> Back
            3, # 12. Projects Menu -> Back
            5  # 13. Main Menu -> Save and Exit
        ]

        mock_input.side_effect = [
            "Technical", # Category
            "Python", "LaTeX", "", # Keywords list
            "Resume Builder", # Project Name
            "Automated YAML parsing", "Interactive CLI", "" # Highlights list
        ]

        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)

        with open("drafts/public_anonymous.yaml", "r") as f:
            data = yaml.safe_load(f)
            self.assertEqual(data["skills"][0]["category"], "Technical")
            self.assertEqual(data["skills"][0]["keywords"], ["Python", "LaTeX"])
            self.assertEqual(data["projects"][0]["name"], "Resume Builder")
            self.assertEqual(data["projects"][0]["highlights"], ["Automated YAML parsing", "Interactive CLI"])

if __name__ == '__main__':
    unittest.main()
