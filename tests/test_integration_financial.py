import os
import shutil
import tempfile
import unittest
from typer.testing import CliRunner
from src.main import app

class TestIntegrationFinancial(unittest.TestCase):
    def setUp(self):
        self.runner = CliRunner()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_financial_redacted_compile(self):
        """
        Test generating a financial resume with redaction and PDF compilation.
        """
        output_tex = os.path.join(self.test_dir, "resume.tex")
        output_pdf = os.path.join(self.test_dir, "resume.pdf")
        
        # Run the generate-resume command
        # We need to ensure we point to existing inputs or mock them.
        # Since this is an integration test, we use the real files if possible.
        result = self.runner.invoke(app, [
            "generate-resume",
            "--template-name", "financial",
            "--redacted",
            "--compile",
            "--output", output_tex
        ])
        
        if result.exit_code != 0:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Resume generated successfully.", result.stdout)
        
        # Check if .tex exists
        self.assertTrue(os.path.exists(output_tex))
        
        # Check if .pdf exists (requires xelatex to be installed on the system)
        # In a CI/CD or controlled environment, we expect xelatex to be available.
        # We checked earlier that /home/iancwm/bin/xelatex exists.
        self.assertTrue(os.path.exists(output_pdf))

if __name__ == "__main__":
    unittest.main()
