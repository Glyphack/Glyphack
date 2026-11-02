# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "feedparser>=6.0.14",
#     "httpx2>=2.16.0",
# ]
# ///
"""Downloads the latest blog posts."""

import asyncio
import json
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import feedparser
import httpx2

ROOT = Path(__file__).resolve().parent.parent
OPML_FILE = ROOT / "static" / "blogroll.opml"
OUTPUT_FILE = ROOT / "data" / "blogroll.json"

POSTS_PER_FEED = 3
TIMEOUT_SECONDS = 20
USER_AGENT = "glyphack.com blogroll (+https://glyphack.com/blogroll/)"


@dataclass
class Feed:
    title: str
    url: str


@dataclass
class Post:
    title: str
    url: str
    date: str
    site: str


def read_opml(path: Path) -> list[Feed]:
    tree = ET.parse(path)
    feeds = []
    for outline in tree.iter("outline"):
        url = outline.get("xmlUrl")
        if not url:
            continue
        title = outline.get("title") or outline.get("text") or ""
        feeds.append(Feed(title=title.strip(), url=url.strip()))
    return feeds


def entry_date(entry) -> datetime | None:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime(*parsed[:6], tzinfo=timezone.utc)


async def fetch_posts(client: httpx2.AsyncClient, feed: Feed) -> list[Post]:
    try:
        response = await client.get(feed.url)
        response.raise_for_status()
    except httpx2.HTTPError as e:
        print(f"WARNING: could not download {feed.url}: {e!r}")
        return []
    parsed = feedparser.parse(response.content)
    if not parsed.entries:
        print(f"WARNING: no posts found in {feed.url}")
        return []

    site = feed.title or parsed.feed.get("title") or urlparse(feed.url).netloc
    dated = []
    for entry in parsed.entries:
        date = entry_date(entry)
        link = entry.get("link")
        if date is None or not link:
            continue
        title = entry.get("title") or link
        dated.append(
            (date, Post(title=title, url=link, date=date.isoformat(), site=site))
        )

    dated.sort(key=lambda pair: pair[0], reverse=True)
    return [post for _, post in dated[:POSTS_PER_FEED]]


async def fetch_all_posts(feeds: list[Feed]) -> list[Post]:
    """Downloads every feed at the same time."""
    async with httpx2.AsyncClient(
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT_SECONDS,
        follow_redirects=True,
    ) as client:
        results = await asyncio.gather(*(fetch_posts(client, feed) for feed in feeds))
    posts = [post for feed_posts in results for post in feed_posts]
    posts.sort(key=lambda post: post.date, reverse=True)
    return posts


def main() -> None:
    posts = asyncio.run(fetch_all_posts(read_opml(OPML_FILE)))
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps([asdict(post) for post in posts], indent=2) + "\n"
    )
    print(f"Wrote {len(posts)} posts to {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
