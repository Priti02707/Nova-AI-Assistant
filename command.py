"""Recognize explicit desktop commands and produce a reply."""

from datetime import datetime
import re
from urllib.parse import urlencode

from features.system import desktop_info


def local_command(message):
    command = message.strip().rstrip("?!")
    now = datetime.now()
    if re.fullmatch(r"(?:(?:what(?: is|'s) (?:the )?)?(?:current )?time|what time is it)", command, re.I):
        return {"text": "The time is " + now.strftime("%I:%M %p") + "."}
    if re.fullmatch(r"(?:what(?: is|'s) (?:the )?)?(?:today's |current )?date(?: today)?", command, re.I):
        return {"text": "Today is " + now.strftime("%d %B %Y") + "."}
    if re.fullmatch(r"(?:show (?:my )?)?system info", command, re.I):
        return {"text": desktop_info()}
    if re.fullmatch(r"(?:tell me )?(?:a )?joke", command, re.I):
        return {"text": "Why did the developer go broke? Because they used up all their cache."}
    if command.lower() in {"open google", "open youtube"}:
        site = command.split()[-1].lower()
        return {"text": f"Opening {site.title()}.", "open_url": f"https://www.{site}.com/"}

    video = re.fullmatch(r"(?:play|search youtube for)\s+(.+)", command, re.I)
    if video:
        url = "https://www.youtube.com/results?" + urlencode({"search_query": video[1]})
        if command.lower().startswith("play "):
            try:
                import pywhatkit

                pywhatkit.playonyt(video[1])
                return {"text": f"Opening a YouTube video for {video[1]}."}
            except Exception:
                pass
        return {"text": f"Opening YouTube search results for {video[1]}.", "open_url": url}

    topic = re.fullmatch(r"(?:search wikipedia for|wikipedia)\s+(.+)", command, re.I)
    if topic:
        try:
            import wikipedia

            wikipedia.set_lang("en")
            return {"text": wikipedia.summary(topic[1], sentences=1)}
        except Exception:
            url = "https://en.wikipedia.org/w/index.php?" + urlencode({"search": topic[1]})
            return {"text": "The summary is unavailable. Opening Wikipedia search results.", "open_url": url}

    search = re.fullmatch(r"search(?: the web)? for\s+(.+)", command, re.I)
    if search:
        url = "https://www.google.com/search?" + urlencode({"q": search[1]})
        return {"text": f"Opening Google search results for {search[1]}.", "open_url": url}
    return None
