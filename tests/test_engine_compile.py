import unittest
from unittest.mock import patch, MagicMock
import os
from src.engine import compile_pdf

class TestEngineCompile(unittest.TestCase):
    @patch('subprocess.run')
    def test_compile_pdf_success(self, mock_run):
        # Setup mock
        mock_run.return_value = MagicMock(returncode=0)
        
        # Call function
        tex_path = "dist/resume.tex"
        output_dir = "dist"
        result = compile_pdf(tex_path, output_dir)
        
        # Assertions
        self.assertTrue(result)
        # Verify xelatex was called twice (as per build.sh logic)
        self.assertEqual(mock_run.call_count, 2)
        mock_run.assert_any_call(
            ['xelatex', '-output-directory=dist', 'dist/resume.tex'],
            check=True,
            capture_output=True,
            text=True
        )

    @patch('subprocess.run')
    def test_compile_pdf_failure(self, mock_run):
        import subprocess
        # Setup mock to raise error
        mock_run.side_effect = subprocess.CalledProcessError(1, 'xelatex')
        
        # Call function
        tex_path = "dist/resume.tex"
        output_dir = "dist"
        with self.assertRaises(RuntimeError):
            compile_pdf(tex_path, output_dir)

if __name__ == '__main__':
    unittest.main()
