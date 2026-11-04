"""Desktop Nova interaction loop for voice and terminal use."""

import os
import webbrowser

from command import local_command
from nova import MAX_HISTORY, MAX_INPUT, MAX_REPLY, NovaError, answer, explicit_tool, run_tool


def desktop_reply(message, history):
    local = local_command(message)
    if local:
        return local
    tool = explicit_tool(message)
    if tool:
        return run_tool(*tool)
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        raise NovaError("Set GROQ_API_KEY to chat, or try a built-in command.", 503)
    return answer(message, history, api_key)


def start_assistant(text_only=False):
    if text_only:
        def listen():
            return input("You: ")

        def speak(text):
            print(f"Nova: {text}")
    else:
        from speech import listen, speak

    history = []
    speak("Hello, I am Nova. How can I help you?")
    while True:
        try:
            message = listen().strip()
        except (EOFError, KeyboardInterrupt):
            break
        except OSError:
            print("Microphone unavailable. Run python main.py --text to type instead.")
            break
        if not message:
            continue
        command = message.lower().rstrip(".?!")
        if command in {"exit", "goodbye", "stop"}:
            speak("Goodbye.")
            break
        if command == "new chat":
            history.clear()
            speak("New conversation started.")
            continue
        if len(message) > MAX_INPUT:
            speak(f"Please keep your message to {MAX_INPUT} characters.")
            continue
        try:
            result = desktop_reply(message, history)
        except NovaError as error:
            speak(str(error))
            continue

        if url := result.get("open_url"):
            webbrowser.open(url)
        text = result["text"][:MAX_REPLY]
        speak(text)
        links = result.get("links", [])
        for link in links:
            print(f"{link['label']} — {link['url']}")
        if links and not text_only:
            speak(" ".join(link["label"] for link in links))
        history.extend([{"role": "user", "content": message}, {"role": "assistant", "content": text}])
        del history[:-MAX_HISTORY]
