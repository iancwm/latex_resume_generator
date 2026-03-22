import unittest
import os
import tempfile
import shutil
import stat
from src.session_manager import SessionManager, atomic_write


class TestAtomicWrite(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_atomic_write_creates_file(self):
        """Test that atomic_write creates a file with correct content."""
        file_path = os.path.join(self.test_dir, "test.txt")
        content = "test content"
        
        atomic_write(file_path, content)
        
        self.assertTrue(os.path.exists(file_path))
        with open(file_path, 'r') as f:
            self.assertEqual(f.read(), content)

    def test_atomic_write_sets_permissions(self):
        """Test that atomic_write sets file permissions to 0600."""
        file_path = os.path.join(self.test_dir, "test.txt")
        content = "test content"
        
        atomic_write(file_path, content)
        
        file_stat = os.stat(file_path)
        # Check that permissions are 0600 (owner read/write only)
        self.assertEqual(stat.S_IMODE(file_stat.st_mode), 0o600)

    def test_atomic_write_replaces_existing(self):
        """Test that atomic_write replaces existing file atomically."""
        file_path = os.path.join(self.test_dir, "test.txt")
        
        # Write initial content
        atomic_write(file_path, "initial content")
        
        # Overwrite with new content
        atomic_write(file_path, "new content")
        
        with open(file_path, 'r') as f:
            self.assertEqual(f.read(), "new content")


class TestSessionManager(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.sessions_dir = os.path.join(self.test_dir, ".sessions")
        self.manager = SessionManager(sessions_dir=self.sessions_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_save_session(self):
        """Test saving a session."""
        session_id = "test_session"
        data = {"resume": "content", "template": "modern"}
        
        self.manager.save(session_id, data)
        
        session_file = os.path.join(self.sessions_dir, f"{session_id}.yaml")
        self.assertTrue(os.path.exists(session_file))

    def test_load_session(self):
        """Test loading a session."""
        session_id = "test_session"
        data = {"resume": "content", "template": "modern"}
        
        # Save first
        self.manager.save(session_id, data)
        
        # Load and verify
        loaded = self.manager.load(session_id)
        self.assertEqual(loaded, data)

    def test_load_nonexistent_session(self):
        """Test loading a session that doesn't exist returns None."""
        loaded = self.manager.load("nonexistent")
        self.assertIsNone(loaded)

    def test_session_exists(self):
        """Test checking if a session exists."""
        session_id = "test_session"
        
        # Should not exist initially
        self.assertFalse(self.manager.exists(session_id))
        
        # Save and verify it exists
        self.manager.save(session_id, {"data": "test"})
        self.assertTrue(self.manager.exists(session_id))

    def test_session_does_not_exist(self):
        """Test checking if a non-existent session returns False."""
        self.assertFalse(self.manager.exists("nonexistent"))


if __name__ == "__main__":
    unittest.main()
