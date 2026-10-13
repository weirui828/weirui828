"""Fetch the latest Medium posts and write them to posts.json for index.html."""
import json
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED_URL = "https://medium.com/feed/@wei.rui828"
MAX_POSTS = 5

req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=30) as resp:
    root = ET.fromstring(resp.read())

posts = []
for item in root.iter("item"):
    posts.append({
        "title": item.findtext("title").strip(),
        "link": item.findtext("link").split("?")[0],
        "date": parsedate_to_datetime(item.findtext("pubDate")).strftime("%Y-%m-%d"),
    })

with open("posts.json", "w", encoding="utf-8") as f:
    json.dump(posts[:MAX_POSTS], f, ensure_ascii=False, indent=2)
    f.write("\n")
