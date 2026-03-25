import pytest
import time
import threading
import requests
import socket
from src.preview_server import PreviewServer


def find_free_port():
    """Find a free port for testing."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


@pytest.fixture
def test_server():
    """Start a test server on a free port."""
    port = find_free_port()
    server = PreviewServer(
        port=port,
        auto_open=False,
        sessions_dir=".sessions_test",
        inputs_dir="inputs_test",
        dist_dir="dist_test"
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    time.sleep(1)  # Wait for startup
    yield server, port
    server.stop()
    time.sleep(0.5)  # Wait for cleanup


def test_health_endpoint(test_server):
    server, port = test_server
    resp = requests.get(f"http://localhost:{port}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "server_id" in data
    assert "pid" in data
    assert "started_at" in data


def test_compile_endpoint(test_server):
    """Test POST /compile endpoint accepts payload and returns success/error."""
    server, port = test_server
    payload = {
        "private": {
            "name": "Test User",
            "email": "test @example.com",
            "phone": "123-456-7890"
        },
        "public": {
            "summary": "Test summary"
        }
    }
    resp = requests.post(f"http://localhost:{port}/compile", json=payload)
    # Accept 200 (success) or 500 (LaTeX not installed - acceptable)
    assert resp.status_code in [200, 500]
    data = resp.json()
    assert "success" in data or "error" in data


def test_error_endpoint(test_server):
    """Test GET /error endpoint returns last error."""
    server, port = test_server
    resp = requests.get(f"http://localhost:{port}/error")
    assert resp.status_code == 200
    data = resp.json()
    assert "last_error" in data


def test_sse_endpoint(test_server):
    """Test GET /events endpoint returns text/event-stream content-type."""
    server, port = test_server
    resp = requests.get(f"http://localhost:{port}/events", stream=True, timeout=2)
    assert resp.status_code == 200
    assert "text/event-stream" in resp.headers.get("content-type", "")
    assert resp.headers.get("cache-control") == "no-cache"
    assert resp.headers.get("connection") == "keep-alive"
