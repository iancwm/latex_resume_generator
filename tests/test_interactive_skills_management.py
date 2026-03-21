import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import yaml
from typer.testing import CliRunner
from src.main import app

class TestInteractiveSkillsManagement(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create initial public.yaml with a skill
        self.initial_public = {
            "skills": [
                {"category": "Programming", "keywords": ["Python", "Rust"]}
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
    def test_edit_existing_skill(self, mock_input, mock_menu):
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        
        # Main Menu: [Basics, Work, Education, Skills, Projects, Save, Exit]
        # Skills Menu: [Add Category, Edit Category, Remove Category, Back]
        # Edit Category Select Menu: [Programming, Back]
        # Skill Edit Menu: [Category Name, Keywords, Back]

        mock_instance.show.side_effect = [
            3, # 1. Main Menu -> Skills
            1, # 2. Skills Menu -> Edit Category
            0, # 3. Select Category -> "Programming"
            1, # 4. Skill Edit Menu -> Keywords
            2, # 5. Skill Edit Menu -> Back
            3, # 6. Skills Menu -> Back
            5  # 7. Main Menu -> Save and Exit
        ]

        mock_input.side_effect = [
            "Python", "Rust", "Go", "" # New keywords list
        ]

        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        
        # Verify changes in draft_public.yaml
        with open("drafts/public_anonymous.yaml", "r") as f:
            data = yaml.safe_load(f)
            self.assertEqual(data["skills"][0]["keywords"], ["Python", "Rust", "Go"])

    @patch('src.main.TerminalMenu')
    def test_remove_existing_skill(self, mock_menu):
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        
        # Main Menu: [Basics, Work, Education, Skills, Projects, Save, Exit]
        # Skills Menu: [Add Category, Edit Category, Remove Category, Back]
        # Remove Category Select Menu: [Programming, Back]

        mock_instance.show.side_effect = [
            3, # 1. Main Menu -> Skills
            2, # 2. Skills Menu -> Remove Category
            0, # 3. Select Category -> "Programming"
            3, # 4. Skills Menu -> Back
            5  # 5. Main Menu -> Save and Exit
        ]

        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        
        # Verify removal in draft_public.yaml
        with open("drafts/public_anonymous.yaml", "r") as f:
            data = yaml.safe_load(f)
            self.assertEqual(len(data["skills"]), 0)

    @patch('src.main.TerminalMenu')
    def test_edit_non_existent_skill(self, mock_menu):
        """Test editing when no skill categories exist."""
        # Start with empty public.yaml
        with open("inputs/public.yaml", "w") as f:
            yaml.dump({"skills": []}, f)
            
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        
        # 1. Main Menu -> Skills (3)
        # 2. Skills Menu -> Edit Category (1) -> Shows "No skill categories to edit."
        # 3. Skills Menu -> Back (3)
        # 4. Main Menu -> Exit (6)
        mock_instance.show.side_effect = [3, 1, 3, 6]
        
        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("No skill categories to edit.", result.stdout)

    @patch('src.main.TerminalMenu')
    def test_remove_non_existent_skill(self, mock_menu):
        """Test removing when no skill categories exist."""
        with open("inputs/public.yaml", "w") as f:
            yaml.dump({"skills": []}, f)
            
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        
        # 1. Main Menu -> Skills (3)
        # 2. Skills Menu -> Remove Category (2) -> Shows "No skill categories to remove."
        # 3. Skills Menu -> Back (3)
        # 4. Main Menu -> Exit (6)
        mock_instance.show.side_effect = [3, 2, 3, 6]
        
        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("No skill categories to remove.", result.stdout)

if __name__ == '__main__':
    unittest.main()
