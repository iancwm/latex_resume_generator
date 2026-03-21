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
            ['xelatex', '-interaction=nonstopmode', '-output-directory=dist', 'dist/resume.tex'],
            check=True,
            capture_output=True,
            text=True
        )

    @patch('src.engine.compile_pdf')
    @patch('src.engine.render_template')
    @patch('src.engine.sanitize_data')
    @patch('src.engine.load_yaml')
    def test_generate_with_compile(self, mock_load, mock_sanitize, mock_render, mock_compile_pdf):
        # Setup mocks
        mock_load.return_value = {}
        mock_sanitize.return_value = {}
        
        # Call function
        from src.engine import generate
        generate("priv.yaml", "pub.yaml", "temp.tex", "dist/out.tex", compile=True)
        
        # Assertions
        mock_compile_pdf.assert_called_once_with("dist/out.tex", "dist")

if __name__ == '__main__':
    unittest.main()
