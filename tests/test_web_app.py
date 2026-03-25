"""
Tests for the Web-Based Resume Editor.
"""

import json
import pytest
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient

from src.web_app import app, session_manager
from src.session_manager import SessionManager


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def temp_sessions_dir():
    """Create a temporary directory for test sessions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def clean_session(temp_sessions_dir, monkeypatch):
    """Clean up test session before and after test."""
    # Create a session manager using the temp directory
    test_session_manager = SessionManager(sessions_dir=str(temp_sessions_dir))
    test_session_name = "test_web_session"
    
    # Patch the web_app's session_manager to use our temp one
    import src.web_app as web_app_module
    original_session_manager = web_app_module.session_manager
    web_app_module.session_manager = test_session_manager
    
    yield test_session_name
    
    # Restore original session manager
    web_app_module.session_manager = original_session_manager


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, client):
        """Test health endpoint returns OK status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "resume-editor"


class TestIndexPage:
    """Test main editor page."""
    
    def test_index_loads(self, client):
        """Test index page loads successfully."""
        response = client.get("/")
        assert response.status_code == 200
        assert b"Resume Editor" in response.content
        assert b"Personal Information" in response.content
    
    def test_index_with_session(self, client):
        """Test index page with custom session."""
        response = client.get("/?session=my-session")
        assert response.status_code == 200
        assert b"Session: my-session" in response.content
    
    def test_index_with_message(self, client):
        """Test index page displays messages."""
        response = client.get("/?message=Test+message&message_type=success")
        assert response.status_code == 200
        assert b"Test message" in response.content


class TestSaveEndpoint:
    """Test save session endpoint."""

    def test_save_basic_info(self, client, clean_session, temp_sessions_dir):
        """Test saving basic information."""
        # Pass session as query parameter
        response = client.post(f"/save?session={clean_session}", data={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1-555-123-4567",
            "city": "San Francisco",
            "region": "CA",
            "work_entries": "[]",
            "education_entries": "[]",
            "skills_entries": "[]",
            "projects_entries": "[]"
        })

        assert response.status_code == 200
        assert b"saved successfully" in response.content
        assert clean_session.encode() in response.content

        # Verify data was saved using the patched session manager
        import src.web_app as web_app_module
        saved_data = web_app_module.session_manager.load(clean_session)
        assert saved_data is not None
        assert saved_data["basics"]["name"] == "John Doe"
        assert saved_data["basics"]["email"] == "john@example.com"

    def test_save_with_work_entry(self, client, clean_session):
        """Test saving with work experience."""
        work_entry = {
            "company": "Tech Corp",
            "position": "Software Engineer",
            "location": "San Francisco, CA",
            "start_date": "2023-01",
            "end_date": "Present",
            "summary": ["Led development", "Improved performance"]
        }

        response = client.post(f"/save?session={clean_session}", data={
            "name": "John Doe",
            "email": "john@example.com",
            "work_entries": json.dumps([work_entry]),
            "education_entries": "[]",
            "skills_entries": "[]",
            "projects_entries": "[]"
        })

        assert response.status_code == 200

        import src.web_app as web_app_module
        saved_data = web_app_module.session_manager.load(clean_session)
        assert len(saved_data["work"]) == 1
        assert saved_data["work"][0]["company"] == "Tech Corp"
    
    def test_save_validation_missing_name(self, client, clean_session):
        """Test validation fails with missing name."""
        response = client.post("/save", data={
            "session": clean_session,
            "name": "",
            "email": "john@example.com",
            "work_entries": "[]",
            "education_entries": "[]",
            "skills_entries": "[]",
            "projects_entries": "[]"
        })
        
        assert response.status_code == 200
        assert b"Name is required" in response.content
    
    def test_save_validation_missing_email(self, client, clean_session):
        """Test validation fails with missing email."""
        response = client.post("/save", data={
            "session": clean_session,
            "name": "John Doe",
            "email": "",
            "work_entries": "[]",
            "education_entries": "[]",
            "skills_entries": "[]",
            "projects_entries": "[]"
        })
        
        assert response.status_code == 200
        assert b"Email is required" in response.content
    
    def test_save_validation_invalid_email(self, client, clean_session):
        """Test validation fails with invalid email."""
        response = client.post("/save", data={
            "session": clean_session,
            "name": "John Doe",
            "email": "not-an-email",
            "work_entries": "[]",
            "education_entries": "[]",
            "skills_entries": "[]",
            "projects_entries": "[]"
        })
        
        assert response.status_code == 200
        assert b"Invalid email format" in response.content


class TestExportEndpoint:
    """Test export session endpoint."""
    
    def test_export_creates_files(self, client, clean_session, tmp_path, monkeypatch):
        """Test export creates YAML files."""
        # First save some data
        client.post("/save", data={
            "session": clean_session,
            "name": "John Doe",
            "email": "john@example.com",
            "work_entries": "[]",
            "education_entries": "[]",
            "skills_entries": "[]",
            "projects_entries": "[]"
        })
        
        # Mock the BASE_DIR to use temp path
        import src.web_app as web_app_module
        original_base_dir = web_app_module.BASE_DIR
        web_app_module.BASE_DIR = tmp_path
        
        try:
            response = client.post("/export", data={"session": clean_session})
            
            assert response.status_code == 200
            assert b"Exported to inputs" in response.content
            
            # Verify files were created
            inputs_dir = tmp_path / "inputs"
            assert (inputs_dir / "private.yaml").exists()
            assert (inputs_dir / "public.yaml").exists()
        finally:
            web_app_module.BASE_DIR = original_base_dir
    
    def test_export_empty_session(self, client, clean_session):
        """Test export with no data shows error."""
        response = client.post("/export", data={"session": clean_session})
        
        assert response.status_code == 200
        assert b"No data to export" in response.content


class TestPreviewEndpoint:
    """Test preview PDF endpoint."""
    
    def test_preview_redirects(self, client):
        """Test preview endpoint redirects."""
        response = client.get("/preview")
        # Should redirect back to index with message
        assert response.status_code in [200, 307]


class TestFormRendering:
    """Test form rendering on index page."""

    def test_rendisters_existing_data(self, client, clean_session):
        """Test index page renders existing session data."""
        # Save data first using the patched session manager
        import src.web_app as web_app_module
        web_app_module.session_manager.save(clean_session, {
            "basics": {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "location": {"city": "Boston", "region": "MA"}
            }
        })

        response = client.get(f"/?session={clean_session}")

        assert response.status_code == 200
        assert b"Jane Doe" in response.content
        assert b"jane@example.com" in response.content
        assert b"Boston" in response.content

    def test_renders_work_entries(self, client, clean_session):
        """Test work entries are rendered."""
        import src.web_app as web_app_module
        web_app_module.session_manager.save(clean_session, {
            "basics": {"name": "Test", "email": "test@example.com"},
            "work": [
                {"company": "Company A", "position": "Role A"},
                {"company": "Company B", "position": "Role B"}
            ]
        })

        response = client.get(f"/?session={clean_session}")

        assert response.status_code == 200
        assert b"Company A" in response.content
        assert b"Company B" in response.content


class TestValidation:
    """Test validation functions."""
    
    def test_validate_form_data_complete(self):
        """Test validation with complete data."""
        from src.web_app import validate_form_data
        
        data = {
            "basics": {
                "name": "John Doe",
                "email": "john@example.com"
            },
            "work": [],
            "education": []
        }
        
        errors = validate_form_data(data)
        assert len(errors) == 0
    
    def test_validate_form_data_missing_name(self):
        """Test validation catches missing name."""
        from src.web_app import validate_form_data
        
        data = {
            "basics": {
                "name": "",
                "email": "john@example.com"
            }
        }
        
        errors = validate_form_data(data)
        assert any(e["field"] == "basics.name" for e in errors)
    
    def test_validate_form_data_invalid_email(self):
        """Test validation catches invalid email."""
        from src.web_app import validate_form_data
        
        data = {
            "basics": {
                "name": "John Doe",
                "email": "not-valid"
            }
        }
        
        errors = validate_form_data(data)
        assert any(e["field"] == "basics.email" for e in errors)
