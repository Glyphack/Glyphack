# /// script
# requires-python = ">=3.11"
# dependencies = ["requests", "Pillow"]
# ///

import re
import sys
from pathlib import Path

import requests
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


def download_cover(isbn: str) -> None:
    url = OPENLIBRARY_URL.format(isbn=isbn)
    response = requests.get(url, timeout=15)
    if response.status_code == 404:
        print(f"ERROR: No cover found for ISBN {isbn} (404)")
        sys.exit(1)
    response.raise_for_status()

    import io
    img = Image.open(io.BytesIO(response.content))
    dest = COVERS_DIR / f"{isbn}.webp"
    img.save(dest, "WEBP")
    print(f"Downloaded: {isbn}")


def main() -> None:
    COVERS_DIR.mkdir(parents=True, exist_ok=True)

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


if __name__ == "__main__":
    main()
