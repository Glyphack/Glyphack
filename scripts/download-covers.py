# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow==12.2.0"]
# ///

import io
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).parent.parent
CONTENT_DIR = REPO_ROOT / "content" / "synced"
COVERS_DIR = REPO_ROOT / "assets" / "book-covers"
OPENLIBRARY_URL = "https://covers.openlibrary.org/b/isbn/{isbn}.jpg?default=false"


def collect_isbns() -> list[str]:
    isbns = []
    for md_file in CONTENT_DIR.glob("*.md"):
        text = md_file.read_text()
        match = re.search(r"^isbn13:\s*(.+)$", text, re.MULTILINE)
        if match:
            isbn = match.group(1).strip().replace("-", "")
            isbns.append(isbn)
    return isbns


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "download-covers"})
    with urllib.request.urlopen(request, timeout=15) as response:
        return response.read()


def save_as_webp(data: bytes, isbn: str) -> None:
    img = Image.open(io.BytesIO(data))
    dest = COVERS_DIR / f"{isbn}.webp"
    img.save(dest, "WEBP")


def download_cover(isbn: str) -> None:
    url = OPENLIBRARY_URL.format(isbn=isbn)
    try:
        data = fetch(url)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"ERROR: No cover found for ISBN {isbn} (404)")
            sys.exit(1)
        raise
    save_as_webp(data, isbn)
    print(f"Downloaded: {isbn}")


def import_cover(url: str, isbn: str) -> None:
    isbn = isbn.replace("-", "")
    data = fetch(url)
    save_as_webp(data, isbn)
    print(f"Imported: {isbn}")


def sync() -> None:
    isbns = collect_isbns()
    missing = [isbn for isbn in isbns if not (COVERS_DIR / f"{isbn}.webp").exists()]
    already_present = len(isbns) - len(missing)

    errors = []
    for isbn in missing:
        try:
            download_cover(isbn)
        except Exception as e:
            errors.append((isbn, str(e)))

    print(f"\nSummary: {already_present} already present, {len(missing) - len(errors)} downloaded")
    if errors:
        for isbn, msg in errors:
            print(f"ERROR {isbn}: {msg}")
        sys.exit(1)


def main() -> None:
    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1 and sys.argv[1] == "import":
        if len(sys.argv) != 4:
            print("Usage: download-covers.py import <url> <isbn>")
            sys.exit(1)
        import_cover(sys.argv[2], sys.argv[3])
        return

    sync()


if __name__ == "__main__":
    main()
