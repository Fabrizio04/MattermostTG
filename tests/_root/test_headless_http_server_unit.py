from unittest.mock import mock_open
from unittest.mock import MagicMock, patch
from HeadlessHTTPServer import HeadlessHTTPServer

class MockSocket:
    def makefile(self, *args, **kwargs):
        return MagicMock()

def create_handler():
    handler = HeadlessHTTPServer.__new__(HeadlessHTTPServer)
    handler.request = MockSocket()
    handler.client_address = ("127.0.0.1", 12345)
    handler.server = MagicMock()
    handler.headers = MagicMock()
    handler.wfile = MagicMock()
    handler.rfile = MagicMock()
    return handler

def test_check_auth_no_creds():
    handler = create_handler()
    with patch("HeadlessHTTPServer.config") as mock_config:
        mock_config.get.return_value = ""
        assert handler._check_auth() is True

def test_check_auth_valid():
    handler = create_handler()
    handler.headers.get.return_value = "Basic dXNlcjpwYXNz"
    with patch("HeadlessHTTPServer.config") as mock_config:
        mock_config.get.side_effect = lambda key, default="": "user" if key == "HTTP_USER" else "pass"
        assert handler._check_auth() is True

def test_check_auth_invalid():
    handler = create_handler()
    handler.headers.get.return_value = "Basic d3Jvbmc="
    with patch("HeadlessHTTPServer.config") as mock_config:
        mock_config.get.side_effect = lambda key, default="": "user" if key == "HTTP_USER" else "pass"
        assert handler._check_auth() is False

def test_send_json():
    handler = create_handler()
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()
    
    handler._send_json({"status": "ok"}, status=200)
    handler.send_response.assert_called_once_with(200)
    handler.wfile.write.assert_called_once()

def test_send_unauthorized():
    handler = create_handler()
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()
    
    handler._send_unauthorized()
    handler.send_response.assert_called_once_with(401)
    handler.wfile.write.assert_called_once()

def test_do_get_public_path():
    handler = create_handler()
    handler.path = "/"
    handler._check_auth = MagicMock(return_value=True)
    
    with patch("HeadlessHTTPServer.resource_path", return_value="dummy_path"), \
         patch("builtins.open", mock_open(read_data="<html>doc</html>")):
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        
        handler.do_GET()
        handler.send_response.assert_called_with(200)