"""Technology headlines and discussions from Hacker News."""

from concurrent.futures import ThreadPoolExecutor

from network import read_json

API = "https://hacker-news.firebaseio.com/v0/"


def story_link(item_id):
    if type(item_id) is not int or item_id <= 0:
        return None
    try:
        story = read_json(f"{API}item/{item_id}.json")
    except (OSError, ValueError):
        return None
    if not isinstance(story, dict) or story.get("dead") or story.get("deleted"):
        return None
    title = story.get("title")
    if not isinstance(title, str) or not title.strip():
        return None
    return {"label": title.strip()[:240], "url": f"https://news.ycombinator.com/item?id={item_id}"}


def headlines():
    ids = read_json(API + "topstories.json")[:5]
    with ThreadPoolExecutor(max_workers=5) as pool:
        links = [link for link in pool.map(story_link, ids) if link]
    if not links:
        return {"text": "Hacker News headlines are temporarily unavailable."}
    return {"text": "Top technology stories and discussions from Hacker News.", "links": links}
