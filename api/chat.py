"""Same-origin API for Nova's browser assistant."""

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler

from nova import MAX_INPUT, NovaError, answer, clean_history, explicit_tool, run_tool


def credentials():
    key = os.environ.get("GROQ_API_KEY", "").strip()
    code = os.environ.get("NOVA_ACCESS_CODE", "").strip()
    if not key or not 24 <= len(code) <= 128 or not code.isascii():
        return "", ""
    return key, code


class handler(BaseHTTPRequestHandler):
    def respond(self, status, value):
        body = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        key, _ = credentials()
        self.respond(200, {"conversation_enabled": bool(key)})

    def do_POST(self):
        try:
            result = self.handle_message()
        except NovaError as error:
            self.respond(error.status, {"error": str(error)})
        else:
            self.respond(200, result)

    def handle_message(self):
        if self.headers.get_content_type() != "application/json":
            raise NovaError("Send an application/json request.", 415)
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            length = 0
        if not 0 < length <= 144_000:
            raise NovaError("Request size is invalid.", 413)
        try:
            body = json.loads(self.rfile.read(length))
        except ValueError:
            raise NovaError("Request JSON is invalid.", 400) from None
        message = body.get("message") if isinstance(body, dict) else None
        if not isinstance(message, str) or not 0 < len(message.strip()) <= MAX_INPUT:
            raise NovaError(f"Enter a message of 1–{MAX_INPUT} characters.", 400)
        message = message.strip()
        tool = explicit_tool(message)
        if tool:
            return run_tool(*tool)

        key, code = credentials()
        if not key:
            raise NovaError("AI chat is disabled on this deployment. Try a built-in command.", 503)
        supplied = self.headers.get("X-Nova-Access-Code", "")
        if not hmac.compare_digest(supplied.encode(), code.encode()):
            raise NovaError("Enter a valid Nova access code to use AI chat.", 403)
        return answer(message, clean_history(body.get("history", [])), key)
