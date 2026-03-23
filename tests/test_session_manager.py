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

    def test_list_sessions_empty(self):
        """Test listing sessions when none exist."""
        sessions = self.manager.list_sessions()
        self.assertEqual(sessions, [])

    def test_list_sessions_returns_sorted_names(self):
        """Test that list_sessions returns sorted session names."""
        # Create sessions in non-alphabetical order
        self.manager.save("charlie", {"data": 1})
        self.manager.save("alpha", {"data": 2})
        self.manager.save("bravo", {"data": 3})

        sessions = self.manager.list_sessions()

        self.assertEqual(sessions, ["alpha", "bravo", "charlie"])

    def test_list_sessions_skips_tmp_files(self):
        """Test that list_sessions skips .tmp.* files."""
        # Create regular sessions
        self.manager.save("session1", {"data": 1})
        self.manager.save("session2", {"data": 2})

        # Create a temp file manually (simulating incomplete save)
        tmp_file = os.path.join(self.sessions_dir, ".tmp.session1")
        with open(tmp_file, 'w') as f:
            f.write("temp content")

        sessions = self.manager.list_sessions()

        self.assertEqual(sessions, ["session1", "session2"])

    def test_delete_session(self):
        """Test deleting an existing session."""
        session_id = "test_session"
        self.manager.save(session_id, {"data": "test"})

        # Verify it exists
        self.assertTrue(self.manager.exists(session_id))

        # Delete it
        self.manager.delete(session_id)

        # Verify it no longer exists
        self.assertFalse(self.manager.exists(session_id))

    def test_delete_nonexistent_session(self):
        """Test deleting a non-existent session does not raise."""
        # Should not raise an exception
        self.manager.delete("nonexistent")

    def test_get_recent_sessions_empty(self):
        """Test getting recent sessions when none exist."""
        recent = self.manager.get_recent_sessions()
        self.assertEqual(recent, [])

    def test_get_recent_sessions_returns_sorted_by_mtime(self):
        """Test that get_recent_sessions returns sessions sorted by mtime descending."""
        import time

        # Create sessions with slight delays to ensure different mtimes
        self.manager.save("first", {"data": 1})
        time.sleep(0.01)
        self.manager.save("second", {"data": 2})
        time.sleep(0.01)
        self.manager.save("third", {"data": 3})

        recent = self.manager.get_recent_sessions(hours=24)

        # Should return all sessions, sorted by mtime descending (most recent first)
        self.assertEqual(len(recent), 3)
        self.assertEqual(recent[0][0], "third")
        self.assertEqual(recent[1][0], "second")
        self.assertEqual(recent[2][0], "first")

        # Verify each entry is (name, mtime) tuple
        for name, mtime in recent:
            self.assertIsInstance(name, str)
            self.assertIsInstance(mtime, float)

    def test_get_recent_sessions_filters_by_hours(self):
        """Test that get_recent_sessions filters by hours parameter."""
        import time

        # Create an old session by modifying its mtime
        self.manager.save("old_session", {"data": 1})
        old_file = os.path.join(self.sessions_dir, "old_session.yaml")
        old_time = time.time() - (25 * 3600)  # 25 hours ago
        os.utime(old_file, (old_time, old_time))

        # Create a recent session
        self.manager.save("recent_session", {"data": 2})

        recent = self.manager.get_recent_sessions(hours=24)

        # Should only return the recent session
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0][0], "recent_session")


if __name__ == "__main__":
    unittest.main()
