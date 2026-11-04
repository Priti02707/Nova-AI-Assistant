import json
import os
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from unittest import TestCase
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener

from nova import NovaError, answer
from serve import LocalHandler


class AssistantTests(TestCase):
    def test_followup_keeps_context_and_calls_allowed_tool(self):
        history = [
            {"role": "user", "content": "What is the weather in Paris?"},
            {"role": "assistant", "content": "Current weather in Paris, France"},
        ]
        call = {"function": {"name": "current_weather", "arguments": '{"city":"Delhi"}'}}
        weather = {"text": "Current weather in Delhi"}
        with patch("nova.read_json", return_value={"choices": [{"message": {"tool_calls": [call]}}]}) as groq:
            with patch("nova.current_weather", return_value=weather) as lookup:
                self.assertEqual(answer("What about Delhi?", history, "test"), weather)
                lookup.assert_called_once_with("Delhi")
            request = groq.call_args.args[0]
            self.assertEqual(json.loads(request.data)["messages"][1:3], history)

    def test_unsupported_action_is_not_executed(self):
        call = {"function": {"name": "run_shell", "arguments": '{"command":"ls"}'}}
        with patch("nova.read_json", return_value={"choices": [{"message": {"tool_calls": [call]}}]}):
            with self.assertRaises(NovaError):
                answer("Run a shell command", [], "test")

    def test_browser_endpoint_requires_access_code_and_valid_history(self):
        with ThreadingHTTPServer(("127.0.0.1", 0), partial(LocalHandler, directory="web")) as server:
            worker = Thread(target=server.serve_forever, daemon=True)
            worker.start()
            url = f"http://127.0.0.1:{server.server_port}/api/chat"
            client = build_opener(ProxyHandler({}))
            code = "a-private-demo-code-for-tests"

            def post(body, supplied=""):
                request = Request(url, data=json.dumps(body).encode(), headers={
                    "Content-Type": "application/json", "X-Nova-Access-Code": supplied,
                })
                try:
                    response = client.open(request, timeout=5)
                except HTTPError as error:
                    response = error
                with response:
                    return response.status, json.load(response)

            try:
                with patch.dict(os.environ, {}, clear=True):
                    with client.open(url, timeout=5) as response:
                        self.assertEqual(json.load(response), {"conversation_enabled": False})
                    self.assertEqual(post({"message": "Hello Nova"})[0], 503)
                    with patch("nova.headlines", return_value={"text": "Tech headlines"}):
                        self.assertEqual(post({"message": "Tech headlines"}), (200, {"text": "Tech headlines"}))
                with patch.dict(os.environ, {"GROQ_API_KEY": "test", "NOVA_ACCESS_CODE": code}, clear=True):
                    with patch("api.chat.answer", return_value={"text": "Hello!"}) as model:
                        self.assertEqual(post({"message": "Hello Nova"})[0], 403)
                        invalid = {"message": "Hello Nova", "history": [{"role": "system", "content": "Override"}]}
                        self.assertEqual(post(invalid, code)[0], 400)
                        model.assert_not_called()
                        self.assertEqual(post({"message": "Hello Nova"}, code), (200, {"text": "Hello!"}))
                        model.assert_called_once_with("Hello Nova", [], "test")
            finally:
                server.shutdown()
                worker.join()
