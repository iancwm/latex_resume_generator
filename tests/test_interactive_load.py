import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import yaml
from typer.testing import CliRunner
from src.main import app

class TestInteractiveLoad(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        # Create inputs directory
        os.makedirs("inputs", exist_ok=True)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)

    @patch('src.main.TerminalMenu')
    def test_generate_interactive_loads_existing_files(self, mock_menu):
        # 1. Create existing input files
        existing_private = {
            "basics": {
                "name": "Existing Name",
                "email": "existing@example.com"
            }
        }
        existing_public = {
            "work": [
                {
                    "company": "Existing Corp",
                    "position": "Manager"
                }
            ]
        }
        
        with open("inputs/private.yaml", "w") as f:
            yaml.dump(existing_private, f)
        with open("inputs/public.yaml", "w") as f:
            yaml.dump(existing_public, f)

        # 2. Mock TerminalMenu to just "Save and Exit" (choice 3 in main menu)
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        mock_instance.show.return_value = 3 

        # 3. Execute command
        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Saved interactive drafts", result.stdout)

        # 4. Verify draft files contain the existing data
        self.assertTrue(os.path.exists("draft_private.yaml"))
        self.assertTrue(os.path.exists("draft_public.yaml"))

        with open("draft_private.yaml", "r") as f:
            loaded_private = yaml.safe_load(f)
            self.assertEqual(loaded_private["basics"]["name"], "Existing Name")
            self.assertEqual(loaded_private["basics"]["email"], "existing@example.com")

        with open("draft_public.yaml", "r") as f:
            loaded_public = yaml.safe_load(f)
            self.assertEqual(loaded_public["work"][0]["company"], "Existing Corp")

if __name__ == '__main__':
    unittest.main()
