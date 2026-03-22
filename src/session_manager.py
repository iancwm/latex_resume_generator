import os
import tempfile
import yaml
import stat


def atomic_write(file_path, content):
    """
    Atomically write content to a file using temp+rename pattern.
    Sets file permissions to 0600 (owner read/write only).
    
    Args:
        file_path: Path to the file to write
        content: String content to write
    """
    dir_path = os.path.dirname(file_path)
    
    # Create directory if it doesn't exist
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, mode=0o700)
    
    # Write to temp file first
    fd, temp_path = tempfile.mkstemp(dir=dir_path if dir_path else None)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        
        # Set permissions before rename
        os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)  # 0600
        
        # Atomic rename
        os.rename(temp_path, file_path)
    except Exception:
        # Clean up temp file on failure
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


class SessionManager:
    """
    Manages session state for the TUI editor.
    Handles saving and loading session data to/from YAML files.
    """
    
    def __init__(self, sessions_dir=".sessions"):
        """
        Initialize SessionManager.
        
        Args:
            sessions_dir: Directory to store session files (default: ".sessions")
        """
        self.sessions_dir = sessions_dir
        
        # Ensure sessions directory exists
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir, mode=0o700)
    
    def _session_path(self, session_id):
        """Get the file path for a session."""
        return os.path.join(self.sessions_dir, f"{session_id}.yaml")
    
    def save(self, session_id, data):
        """
        Save session data to a YAML file.
        
        Args:
            session_id: Unique identifier for the session
            data: Dictionary of session data to save
        """
        file_path = self._session_path(session_id)
        content = yaml.dump(data, default_flow_style=False)
        atomic_write(file_path, content)
    
    def load(self, session_id):
        """
        Load session data from a YAML file.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Dictionary of session data, or None if session doesn't exist
        """
        file_path = self._session_path(session_id)
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    
    def exists(self, session_id):
        """
        Check if a session exists.
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            True if session exists, False otherwise
        """
        file_path = self._session_path(session_id)
        return os.path.exists(file_path)
