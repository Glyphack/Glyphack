# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Downloads Readwise favorites."""

import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = ROOT / "data" / "favorites.json"

READWISE_LIST_URL = "https://readwise.io/api/v3/list/"
SHARE_TAG = "share"
KEYCHAIN_ACCOUNT = "glyphack"
KEYCHAIN_SERVICE = "readwise_api"
TIMEOUT_SECONDS = 30


def log(message: str) -> None:
    print(message, flush=True)


@dataclass
class Favorite:
    title: str
    url: str
    author: str
    date: str


def read_token() -> str | None:
    env_token = os.environ.get("READWISE_API_KEY")
    if env_token:
        return env_token.strip()

    result = subprocess.run(
        [
            "security",
            "find-generic-password",
            "-a",
            KEYCHAIN_ACCOUNT,
            "-s",
            KEYCHAIN_SERVICE,
            "-w",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def fetch_page(token: str, cursor: str | None) -> dict:
    """Fetch one page of shared documents, waiting when Readwise asks us to slow down."""
    params = {"tag": SHARE_TAG}
    if cursor:
        params["pageCursor"] = cursor
    url = f"{READWISE_LIST_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"Authorization": f"Token {token}"})

    while True:
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return json.load(response)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            delay = int(e.headers.get("Retry-After", "1"))
            log(f"Readwise rate limit hit, waiting {delay}s")
            time.sleep(delay)


def fetch_favorites(token: str) -> list[Favorite]:
    """Return every shared document once, keyed by its original url."""
    favorites: dict[str, Favorite] = {}
    cursor = None
    while True:
        page = fetch_page(token, cursor)
        for doc in page["results"]:
            url = doc.get("source_url")
            if not url or url in favorites:
                continue
            favorites[url] = Favorite(
                title=doc.get("title") or url,
                url=url,
                author=(doc.get("author") or "").strip(),
                date=doc["saved_at"],
            )
        cursor = page.get("nextPageCursor")
        if not cursor:
            break

    return sorted(favorites.values(), key=lambda favorite: favorite.date, reverse=True)


def main() -> None:
    token = read_token()
    if token is None:
        print("Skipped updating favorites because the token is not set")
        return
    favorites = fetch_favorites(token)
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps([asdict(f) for f in favorites], indent=2) + "\n")
    log(f"Wrote {len(favorites)} favorites to {OUTPUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
