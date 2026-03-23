import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tui_app import ResumeEditorApp


class TestResumeEditorAppSave(unittest.TestCase):
    """Test save and compile functionality in ResumeEditorApp."""

    def setUp(self):
        """Set up test fixtures."""
        self.app = ResumeEditorApp(session_name="test_session")
        self.app.current_data = {
            "basics": {"name": "Test User"},
            "work": [{"company": "Test Corp", "position": "Developer"}]
        }

    def test_save_session_method_exists(self):
        """Test that save_session method exists on ResumeEditorApp."""
        self.assertTrue(hasattr(self.app, 'save_session'))
        self.assertTrue(callable(getattr(self.app, 'save_session')))

    @patch('src.tui_app.SessionManager')
    def test_save_session_calls_session_manager_save(self, mock_session_manager_class):
        """Test that save_session calls SessionManager.save with correct data."""
        mock_manager = MagicMock()
        mock_session_manager_class.return_value = mock_manager
        self.app.session_manager = mock_manager

        self.app.save_session()

        mock_manager.save.assert_called_once_with(
            "test_session",
            self.app.current_data
        )

    def test_compile_resume_method_exists(self):
        """Test that compile_resume method exists on ResumeEditorApp."""
        self.assertTrue(hasattr(self.app, 'compile_resume'))
        self.assertTrue(callable(getattr(self.app, 'compile_resume')))

    @patch('src.tui_app.requests.post')
    def test_compile_resume_posts_to_server(self, mock_post):
        """Test that compile_resume POSTs to preview server with correct data."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        self.app.compile_resume()

        mock_post.assert_called_once_with(
            "http://localhost:8000/compile",
            json={
                "private": {"basics": {"name": "Test User"}},
                "public": {"work": [{"company": "Test Corp", "position": "Developer"}]}
            },
            timeout=5
        )

    @patch('src.tui_app.requests.post')
    def test_compile_resume_updates_status_on_success(self, mock_post):
        """Test that compile_resume updates sub_title on successful compile."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        self.app.compile_resume()

        self.assertIn("Compiled", self.app.sub_title)

    @patch('src.tui_app.requests.post')
    def test_compile_resume_updates_status_on_failure(self, mock_post):
        """Test that compile_resume updates sub_title on compile failure."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        self.app.compile_resume()

        self.assertIn("failed", self.app.sub_title)

    @patch('src.tui_app.requests.post')
    def test_compile_resume_handles_server_unavailable(self, mock_post):
        """Test that compile_resume handles server unavailable gracefully."""
        mock_post.side_effect = Exception("Connection refused")

        self.app.compile_resume()

        self.assertIn("unavailable", self.app.sub_title)

    def test_action_save_method_exists(self):
        """Test that action_save method exists for Ctrl+S binding."""
        self.assertTrue(hasattr(self.app, 'action_save'))
        self.assertTrue(callable(getattr(self.app, 'action_save')))

    @patch.object(ResumeEditorApp, 'save_session')
    @patch.object(ResumeEditorApp, '_trigger_compile')
    def test_action_save_calls_save_and_compile(self, mock_trigger_compile, mock_save_session):
        """Test that action_save calls both save_session and _trigger_compile."""
        self.app.action_save()

        mock_save_session.assert_called_once()
        mock_trigger_compile.assert_called_once()

    def test_trigger_compile_method_exists(self):
        """Test that _trigger_compile method exists."""
        self.assertTrue(hasattr(self.app, '_trigger_compile'))
        self.assertTrue(callable(getattr(self.app, '_trigger_compile')))

    def test_ctrl_s_binding_exists(self):
        """Test that Ctrl+S binding is defined in BINDINGS."""
        bindings = getattr(self.app, 'BINDINGS', [])
        binding_keys = [b[0] for b in bindings]
        self.assertIn("ctrl+s", binding_keys)


if __name__ == "__main__":
    unittest.main()
