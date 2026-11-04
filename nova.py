"""Shared Nova conversation and allowlisted tools."""

import json
import os
import re
from urllib.error import HTTPError
from urllib.request import Request

from features.news import headlines
from features.weather import current_weather
from network import read_json

DEFAULT_MODEL = "openai/gpt-oss-20b"
MAX_INPUT = 2_000
MAX_REPLY = 3_500
MAX_HISTORY = 8
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
SYSTEM_PROMPT = (
    "You are Nova, a practical personal assistant. Help with questions, explanations, writing, planning, "
    "and brainstorming. Follow the user's language and use the conversation for follow-ups. "
    "Write concise plain text with short paragraphs or lists. "
    "For current weather, use current_weather and ask for the city when it is unclear. "
    "For tech headlines, use tech_headlines. You cannot browse general web pages or control the user's device. "
    "Never claim to have opened a link, run an action, or checked live facts outside the supplied tools."
)
TOOLS = [
    {"type": "function", "function": {
        "name": "current_weather",
        "description": "Get current weather for a named city.",
        "parameters": {
            "type": "object", "properties": {"city": {"type": "string"}},
            "required": ["city"], "additionalProperties": False,
        },
    }},
    {"type": "function", "function": {
        "name": "tech_headlines",
        "description": "Get the top technology stories and discussions on Hacker News.",
        "parameters": {"type": "object", "properties": {}, "additionalProperties": False},
    }},
]


class NovaError(Exception):
    def __init__(self, message, status=502):
        super().__init__(message)
        self.status = status


def clean_history(history):
    if not isinstance(history, list) or len(history) > MAX_HISTORY or len(history) % 2:
        raise NovaError("Conversation history is invalid. Start a new chat.", 400)
    cleaned = []
    for index, entry in enumerate(history):
        role = "assistant" if index % 2 else "user"
        limit = MAX_REPLY if role == "assistant" else MAX_INPUT
        if not isinstance(entry, dict) or entry.get("role") != role:
            raise NovaError("Conversation history is invalid. Start a new chat.", 400)
        content = entry.get("content")
        if not isinstance(content, str) or not content.strip() or len(content) > limit:
            raise NovaError("Conversation history is invalid. Start a new chat.", 400)
        cleaned.append({"role": role, "content": content})
    return cleaned


def explicit_tool(message):
    command = message.strip().rstrip("?!")
    if re.fullmatch(r"(?:(?:show me|what is|what's) (?:the )?)?(?:current )?weather", command, re.I):
        return "current_weather", {"city": ""}
    city = re.fullmatch(r"(?:(?:what is|what's|show me) (?:the )?)?(?:current )?weather (?:in|for) (.+)", command, re.I)
    if city:
        return "current_weather", {"city": city[1]}
    if re.fullmatch(r"(?:(?:show me|read me) )?(?:the )?(?:(?:latest|top|today's) )?(?:tech |technology )?(?:news|headlines)", command, re.I):
        return "tech_headlines", {}
    return None


def run_tool(name, arguments):
    if name == "current_weather" and isinstance(arguments, dict) and set(arguments) == {"city"}:
        city = arguments["city"]
        if not isinstance(city, str) or not 2 <= len(city.strip()) <= 100:
            return {"text": "Which city? Try “weather in New Delhi”."}
        try:
            return current_weather(city.strip())
        except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError):
            raise NovaError("Open-Meteo is temporarily unavailable. Try again in a moment.") from None
    if name == "tech_headlines" and arguments == {}:
        try:
            return headlines()
        except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError):
            raise NovaError("Hacker News is temporarily unavailable. Try again in a moment.") from None
    raise NovaError("Nova could not complete that tool request.")


def groq_message(payload, api_key):
    request = Request(GROQ_URL, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    request.add_unredirected_header("Authorization", f"Bearer {api_key}")
    return read_json(request, timeout=12)["choices"][0]["message"]


def groq_error_code(error):
    try:
        with error:
            details = json.loads(error.read(16_384))["error"]
        return details.get("code")
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None


def groq_error(status, code):
    if status == 401:
        return NovaError("Groq rejected GROQ_API_KEY (HTTP 401). Check the key in Nova's deployment settings and redeploy.")
    if status == 403:
        return NovaError("Groq denied this request (HTTP 403). Check the key's project permissions and model access.")
    if status == 404 or code in ("model_not_found", "model_decommissioned"):
        return NovaError("Groq could not use the selected model. Check GROQ_MODEL or remove the override to use Nova's default.")
    if status == 429:
        return NovaError("Groq is rate limiting requests. Try again later.", 429)
    return NovaError(f"Groq rejected this request (HTTP {status}). Try a new chat or check the model settings.")


def answer(message, history, api_key):
    model = os.environ.get("GROQ_MODEL", "").strip() or DEFAULT_MODEL
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}, *history, {"role": "user", "content": message}],
        "tools": TOOLS,
        "max_completion_tokens": 900,
    }
    if model == DEFAULT_MODEL:
        payload["reasoning_effort"] = "low"
    for attempt in range(2):
        try:
            result = groq_message(payload, api_key)
            calls = result.get("tool_calls") or []
            if calls:
                if "tools" not in payload or len(calls) != 1:
                    raise ValueError("Unexpected tool response")
                function = calls[0]["function"]
                return run_tool(function["name"], json.loads(function["arguments"]))
            content = result.get("content")
            if isinstance(content, str) and content.strip():
                return {"text": content.strip()[:MAX_REPLY]}
        except HTTPError as error:
            status, code = error.code, groq_error_code(error)
            if attempt == 0 and status == 400 and code == "tool_use_failed":
                # Ordinary chat can continue if the model generated an invalid tool call.
                payload.pop("tools")
                payload["messages"][0]["content"] += (
                    " Live tools are unavailable for this answer. "
                    "For weather or tech headlines, suggest a built-in command without inventing results."
                )
                continue
            raise groq_error(status, code) from None
        except (OSError, ValueError, TypeError, KeyError, IndexError, AttributeError):
            pass
        break
    raise NovaError("Nova did not receive a usable response from Groq. Try again.")
