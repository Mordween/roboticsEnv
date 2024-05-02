import webbrowser as wb 
import websockets 
import threading
import socketserver 


import json
from functools import cached_property
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse
from pathlib import Path
from queue import Queue


class myServer(): 
    def __init__(self, outq = Queue(), inq = Queue()):         #, outq, inq, socket_port, run, verbose=False, custom_root=None
        server_port = 52000
        self.inq = inq
        # self.run = run

        # root_dir = Path(sw.__file__).parent / "out"

        class WebRequestHandler(BaseHTTPRequestHandler):
            @cached_property
            def url(self):
                return urlparse(self.path)

            @cached_property
            def query_data(self) -> dict[str, str]:
                return dict(parse_qsl(self.url.query))

            @cached_property
            def post_data(self) -> bytes:
                content_length = int(self.headers.get("Content-Length", 0))
                return self.rfile.read(content_length)

            @cached_property
            def form_data(self):
                return dict(parse_qsl(self.post_data.decode("utf-8")))

            @cached_property
            def cookies(self):
                return SimpleCookie(self.headers.get("Cookie"))

            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(self.get_response().encode("utf-8"))

            def do_POST(self):
                self.do_GET()

            def get_response(self):
                return json.dumps(
                    {
                        "path": self.url.path,
                        "query_data": self.query_data,
                        "post_data": self.post_data.decode("utf-8"),
                        "form_data": self.form_data,
                        "cookies": {
                            name: cookie.value for name, cookie in self.cookies.items()
                        },
                    }
                )
            
            
        Handler = WebRequestHandler 
        
        connected = False

        while not connected and server_port < 62000:
            try:
                with socketserver.TCPServer(("", server_port), Handler) as httpd:
                    self.inq.put(item = server_port)
                    connected = True

                    threading.Thread(target=self.open_browser, args=(server_port,)).start()  # Démarrer un thread pour ouvrir le navigateur 
                    httpd.serve_forever()
            except OSError:
                server_port += 1

    def open_browser(self, port):
        wb.open(f"http://localhost:{port}")


if __name__ == '__main__': 
    myServer()
