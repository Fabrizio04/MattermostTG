import json
import pytest
import threading
import urllib.request
import urllib.error

from unittest.mock import patch
from HeadlessHTTPServer import HeadlessHTTPServer

@pytest.fixture(scope="module", autouse=True)
def server_fixture():
    fake_config = {
        "PORT": 8090,
        "HTTP_USER": "",
        "HTTP_PASS": "",
        "THEME": "light"
    }
    
    with patch("HeadlessHTTPServer.config", fake_config):
        server_thread = threading.Thread(target=HeadlessHTTPServer.run_http_server, daemon=True)
        server_thread.start()
        
        import time
        time.sleep(0.5)
        
        yield
        
        try:
            HeadlessHTTPServer.stop_http_server()
        except Exception:
            pass

def test_integration_status_endpoint():
    url = "http://127.0.0.1:8090/status"
    try:
        req = urllib.request.urlopen(url)
        assert req.status == 200
        data = json.loads(req.read().decode("utf-8"))
        assert "notify_service" in data
        assert "ws_mattermost" in data
    except urllib.error.HTTPError as e:
        pytest.fail(f"HTTP Error: {e.code}")

def test_integration_config_endpoint():
    url = "http://127.0.0.1:8090/config"
    try:
        req = urllib.request.urlopen(url)
        assert req.status == 200
        data = json.loads(req.read().decode("utf-8"))
        assert "PORT" in data
    except urllib.error.HTTPError as e:
        pytest.fail(f"HTTP Error: {e.code}")

def test_integration_not_found():
    url = "http://127.0.0.1:8090/nonexistent-endpoint"
    with pytest.raises(urllib.error.HTTPError) as excinfo:
        urllib.request.urlopen(url)
    assert excinfo.value.code == 404