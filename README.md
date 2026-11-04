# Nova AI Assistant

Nova is a Python desktop voice assistant. It can tell the time or date, open Google or YouTube, play a YouTube search result, read a Wikipedia summary, and tell a joke.

## Run locally

Use a desktop session with a working microphone, speakers, and internet access. On Linux, install PortAudio and an eSpeak-compatible speech engine through your package manager. On macOS, grant microphone access to the terminal or editor that starts Python. On Windows, speech uses the system voice.

```bash
python -m pip install -r requirements.txt
python main.py
```

Speak after the “Listening…” prompt. Try “what time is it”, “open YouTube”, or “tell me a joke”. Say “goodbye” to exit, or press Ctrl+C. Voice recognition sends recorded audio to Google for transcription.

Weather, news, and operating-system commands are planned. The `features/` files are placeholders.

## Author

Priti Kumari

## Browser demo and deployment

From the repository root, run `python -m http.server 8000 --bind 127.0.0.1 --directory web` and open <http://127.0.0.1:8000>.

Import this GitHub repository into Vercel with the root directory set to the repository root. The checked-in configuration serves `web/` as a static site. It needs no API key or Python dependencies. After deployment, check the command examples and test the microphone over HTTPS in a browser that supports speech recognition. Typed commands work when the browser lacks voice support or the visitor declines microphone permission. Nova gives the visitor links for Wikipedia and YouTube searches.
