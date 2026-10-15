"""Add new Medium posts to posts.json for index.html.

Run by hand from the repo root: python3 scripts/update_posts.py

posts.json is hand-picked: which posts appear, which one is "featured", and every summary.
This script only adds posts published after the newest one already listed, with the article's
opening as a placeholder summary worth rewriting. It never removes or changes existing entries.
"""
import html
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED_URL = "https://medium.com/feed/@wei.rui828"
SUMMARY_CHARS = 170
CONTENT = "{http://purl.org/rss/1.0/modules/content/}encoded"


def summary(body):
    """The article's opening paragraphs, trimmed at a word boundary."""
    paras = [html.unescape(re.sub(r"<[^>]+>", "", p)).strip() for p in re.findall(r"<p>(.*?)</p>", body, re.S)]
    text = ""
    for p in filter(None, paras):
        text = f"{text} {p}".strip()
        if len(text) >= 120:
            break
    if len(text) <= SUMMARY_CHARS:
        return text
    return text[:SUMMARY_CHARS].rsplit(" ", 1)[0].rstrip(",;:—-") + "…"


with open("posts.json", encoding="utf-8") as f:
    posts = json.load(f)
known = {p["link"] for p in posts}
newest = max((p["date"] for p in posts), default="")

req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    root = ET.fromstring(resp.read())

new = []
for item in root.iter("item"):
    link = item.findtext("link").split("?")[0]
    date = parsedate_to_datetime(item.findtext("pubDate")).strftime("%Y-%m-%d")
    if not link.startswith("https://medium.com/") or link in known or date <= newest:
        continue
    new.append({
        "title": item.findtext("title").strip(),
        "link": link,
        "date": date,
        "summary": summary(item.findtext(CONTENT) or ""),
    })

if new:
    with open("posts.json", "w", encoding="utf-8") as f:
        json.dump(new + posts, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Added (rewrite their summaries in posts.json):")
    for p in new:
        print(f"  {p['date']}  {p['title']}")
else:
    print("No new posts.")
