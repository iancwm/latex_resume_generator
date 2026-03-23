import pytest
import time
import threading
import requests
from src.preview_server import PreviewServer


@pytest.fixture
def test_server():
    """Start a test server on port 8765."""
    server = PreviewServer(
        port=8765,
        auto_open=False,
        sessions_dir=".sessions_test",
        inputs_dir="inputs_test",
        dist_dir="dist_test"
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1)  # Wait for startup
    yield server
    server.stop()


def test_health_endpoint(test_server):
    resp = requests.get("http://localhost:8765/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "server_id" in data
    assert "pid" in data
    assert "started_at" in data
