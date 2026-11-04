# Nova AI Assistant

Nova is a personal assistant for the browser and desktop. Ask it to explain a concept, draft a message, plan a task, or refine an answer with a follow-up. Use typing or voice input and listen to replies when speech output is available.

| Capability | Example |
| --- | --- |
| Conversation with Groq | “Explain binary search simply.” Then ask “Can you show an example?” |
| Current weather | “Weather in New Delhi” |
| Technology headlines | “Tech headlines” |
| Search | “Search Wikipedia for machine learning” or “Search for Python tutorials” |
| Local commands | “What time is it?”, “Tell me a joke”, “System info”, or “Play jazz” |

Weather comes from [Open-Meteo](https://open-meteo.com/) and headlines link to [Hacker News](https://news.ycombinator.com/) discussions. The browser opens a link only when you click it. Desktop commands can open a browser tab. System info reads basic OS details on desktop and browser language and time zone on the web.

## Run the browser assistant locally

```bash
python serve.py
```

Open <http://127.0.0.1:8000>. The web server uses the Python standard library. Time, date, jokes, and search links run in the browser. Weather and technology headlines require internet access and work without a Groq key. Open-Meteo's free API is for non-commercial use.

To enable conversations, export the following values before starting the server. The Groq key stays on the server.

| Variable | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Required for model replies. |
| `GROQ_MODEL` | Optional. Defaults to `openai/gpt-oss-20b`. Choose a model that supports local function calling. |

Generate a code with `python -c 'import secrets; print(secrets.token_urlsafe(32))'`. Nova sends the current question and up to four previous turns to Groq. The conversation stays in memory until you start a new chat or reload the page. Microphone support depends on the browser, and speech recognition may use the browser's remote speech service.

## Run the desktop assistant

For text input, run `python main.py --text`. For voice, install the desktop dependencies and run the regular entry point.

```bash
python -m pip install -r requirements.txt
python main.py
```

On Linux, install PortAudio and an eSpeak-compatible speech engine. On macOS, allow microphone access for the terminal or editor. Desktop voice recognition sends recorded audio to Google for transcription. Export `GROQ_API_KEY` to enable desktop conversations. Say or type **new chat** to reset context, or **goodbye** to exit.

## Deploy to Vercel

Import the repository or redeploy an existing Nova project with the root set to the repository root. Use the **Other** preset if prompted. The checked-in configuration serves `web/` and exposes the Python function at `/api/chat`. Set `GROQ_API_KEY` in the Vercel Production environment for live conversations. After deployment, test a typed question and a follow-up, weather, headlines, and microphone input over HTTPS.

## Author

Priti Kumari
