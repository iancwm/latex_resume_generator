import unittest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from src.main import app

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()

    @patch('src.main.engine_generate')
    def test_generate_resume_compile_flag(self, mock_generate):
        # We need to mock os.makedirs and resolve_template_path as well to avoid side effects
        with patch('os.makedirs'):
            with patch('src.main.resolve_template_path') as mock_resolve:
                mock_resolve.return_value = ("modern", "templates/resume/modern.tex")
                
                # Execute command
                result = self.runner.invoke(app, ["generate-resume", "--compile"])
                
                # Assertions
                self.assertEqual(result.exit_code, 0)
                # Check if compile=True was passed to engine_generate
                # The signature of engine_generate is (priv, pub, temp, out, redacted, compile)
                mock_generate.assert_called_with(
                    "inputs/private.yaml",
                    "inputs/public.yaml",
                    "templates/resume/modern.tex",
                    "dist/resume.tex",
                    False, # redacted
                    compile=True
                )

    @patch('src.main.engine_generate')
    def test_generate_cover_letter_compile_flag(self, mock_generate):
        with patch('os.makedirs'):
            with patch('src.main.resolve_template_path') as mock_resolve:
                mock_resolve.return_value = ("standard", "templates/cover_letter/standard.tex")
                
                # Execute command
                result = self.runner.invoke(app, ["generate-cover-letter", "--compile"])
                
                # Assertions
                self.assertEqual(result.exit_code, 0)
                mock_generate.assert_called_with(
                    "inputs/private.yaml",
                    "inputs/public.yaml",
                    "templates/cover_letter/standard.tex",
                    "dist/cover_letter.tex",
                    False, # redacted
                    compile=True
                )

    @patch('src.main.engine_generate')
    def test_generate_resume_financial_template(self, mock_generate):
        with patch('os.makedirs'):
            # Execute command
            result = self.runner.invoke(app, ["generate-resume", "--template-name", "financial"])
            
            # Assertions
            self.assertEqual(result.exit_code, 0)
            mock_generate.assert_called_with(
                "inputs/private.yaml",
                "inputs/public.yaml",
                "templates/resume/financial.tex",
                "dist/resume.tex",
                False, # redacted
                compile=False
            )

if __name__ == '__main__':
    unittest.main()
