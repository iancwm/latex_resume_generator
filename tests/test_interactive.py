import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import yaml
from typer.testing import CliRunner
from src.main import app

class TestInteractiveCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()
        # Change current working directory to test_dir to avoid polluting project root
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.old_cwd)
        shutil.rmtree(self.test_dir)

    @patch('src.main.TerminalMenu')
    @patch('builtins.input')
    def test_generate_interactive_success(self, mock_input, mock_menu):
        # Setup mocks for simple-term-menu
        mock_instance = MagicMock()
        mock_menu.return_value = mock_instance
        # Mocking menu selections:
        # Loop 1:
        #   Main menu: 0 (Basics)
        #     Basics menu: 0 (Name) -> input()
        #     Basics menu: 5 (Back)
        # Loop 2:
        #   Main menu: 3 (Save and Exit)
        mock_instance.show.side_effect = [0, 0, 5, 3] 
        
        # Mocking user input for "Name"
        mock_input.return_value = "John Doe"

        # Execute command
        # Note: We might need to ensure src is in PYTHONPATH or use relative imports
        result = self.runner.invoke(app, ["generate-interactive"], catch_exceptions=False)

        if result.exit_code != 0:
            print(result.stdout)
            print(result.stderr)
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Saved interactive drafts", result.stdout)

        # Check if draft files were created
        self.assertTrue(os.path.exists("draft_public.yaml"))
        self.assertTrue(os.path.exists("draft_private.yaml"))

        # Verify content
        with open("draft_private.yaml", "r") as f:
            data = yaml.safe_load(f)
            self.assertEqual(data["basics"]["name"], "John Doe")

if __name__ == '__main__':
    unittest.main()
