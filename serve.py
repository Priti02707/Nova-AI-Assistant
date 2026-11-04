"""Run Nova's browser app and API locally."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from api.chat import handler


class LocalHandler(handler, SimpleHTTPRequestHandler):
    def do_GET(self):
        if urlsplit(self.path).path == "/api/chat":
            super().do_GET()
        else:
            SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if urlsplit(self.path).path == "/api/chat":
            super().do_POST()
        else:
            self.respond(404, {"error": "Unknown endpoint."})


if __name__ == "__main__":
    web = Path(__file__).resolve().parent / "web"
    with ThreadingHTTPServer(("127.0.0.1", 8000), partial(LocalHandler, directory=web)) as server:
        print("Nova is available at http://127.0.0.1:8000")
        server.serve_forever()
