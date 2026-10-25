import os
import json
import base64
import http.server
import socketserver
import urllib.parse
import mattermost_listener

from logger import log
from settings import config
from func.utils import resource_path
from func.decrypter import get_decrypter
from func.i18n import load_language, get
from func.openapi import get_openapi_spec

httpd = None

class HeadlessHTTPServer(http.server.BaseHTTPRequestHandler):
    
    def _check_auth(self):

        if not config.get("HTTP_USER","") or not config.get("HTTP_PASS",""):
            return True
            
        auth_header = self.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return False
            
        try:
            encoded_credentials = auth_header.split(" ")[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode("utf-8")
            username, password = decoded_credentials.split(":", 1)
            return username == config.get("HTTP_USER","") and password == config.get("HTTP_PASS","")
        except Exception:
            return False

    def _send_json(self, data, status=200):
        response = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def _send_unauthorized(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Mattermost Notifier"')
        self.end_headers()
        self.wfile.write(b"Unauthorized")

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        public_paths = ["", "/", "/docs", "/openapi.json", "/favicon.ico"]

        if path not in public_paths and not self._check_auth():
            self._send_unauthorized()
            return

        if path in ("/", ""):
            html_docs = ""
            docs_path = resource_path(os.path.join("web", "index.html"))
            with open(docs_path, "r", encoding="utf-8") as f:
                html_docs = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_docs.encode("utf-8"))

        elif path == "/favicon.ico":
            try:
                icon_path = resource_path(os.path.join("img", "icon_active.ico"))
                with open(icon_path, "rb") as f:
                    icon_data = f.read()
                
                self.send_response(200)
                self.send_header("Content-Type", "image/x-icon")
                self.send_header("Content-Length", str(len(icon_data)))
                self.end_headers()
                self.wfile.write(icon_data)
            except Exception as e:
                self.send_response(404)
                self.end_headers()

        elif path == "/status":

            notify_service = get("settings.ui.marker_srv.active") if mattermost_listener.service_active else get("settings.ui.marker_srv.inactive")
            ws_mattermost = get("settings.ui.marker_ws.connected") if mattermost_listener.is_websocket_connected() else get("settings.ui.marker_ws.disconnected")

            status_data = {
                "notify_service": notify_service,
                "ws_mattermost": ws_mattermost
            }

            self._send_json(status_data)

        elif path == "/config":            
            self._send_json(config)

        elif path == "/decrypter":
            
            include_key = query_params.get("includeKey", ["false"])[0].lower() == "true"
                        
            try:
                html_content = get_decrypter(include_key)

                if html_content == "NF":
                    raise Exception("decrypter.html")

                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html_content.encode("utf-8"))
            except Exception as e:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(f"Decrypter HTML not found: {e}".encode("utf-8"))

        elif path == "/openapi.json":
            spec = get_openapi_spec()

            if config.get("HTTP_USER","") and config.get("HTTP_PASS",""):
                spec["components"] = {
                    "securitySchemes": {
                        "basicAuth": {
                            "type": "http",
                            "scheme": "basic"
                        }
                    }
                }
                spec["security"] = [
                    {
                        "basicAuth": []
                    }
                ]

            self._send_json(spec)

        elif path == "/docs":
            html_docs = ""
            docs_path = resource_path(os.path.join("web", "docs.html"))
            with open(docs_path, "r", encoding="utf-8") as f:
                html_docs = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_docs.encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        if not self._check_auth():
            self._send_unauthorized()
            return

        if self.path == "/config":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                new_config_data = json.loads(body.decode("utf-8"))
                config.update(new_config_data)
                mattermost_listener.reconnect_websocket()
                load_language()
                self._send_json({"status": "success", "message": get("settings.save.message")})
            except Exception as e:
                self._send_json({"status": "error", "message": str(e)}, status=400)

        elif self.path == "/notify_service":
            mattermost_listener.service_active = not mattermost_listener.service_active
            
            self._send_json({
                "status": "success", 
                "service_active": mattermost_listener.service_active
            })

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, string_format, *args):
        log.debug(f"[HTTP] {string_format % args}")

    @staticmethod
    def run_http_server():
        global httpd
        port = config.get("PORT", 8080)
        server_address = ("", port)
        httpd = socketserver.TCPServer(server_address, HeadlessHTTPServer)
        log.info(get("log.http_server.start").format(port=port))
        httpd.serve_forever()

    @staticmethod
    def stop_http_server():
        global httpd
        httpd.shutdown()
        httpd.server_close()
        log.info(get("log.http_server.stop"))