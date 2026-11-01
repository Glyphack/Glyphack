# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow==12.2.0"]
# ///
"""Make sure every book in content/synced has a .webp cover in assets/book-covers.

For each ISBN found in the markdown files:
1. If <isbn>.webp exists, nothing to do.
2. Else if <isbn>.jpg / .jpeg / .png / ... exists, convert it to .webp (quality 80).
3. Else download the cover from Open Library and save it as .webp.
4. If none of that produced a .webp, the ISBN is reported as an error.

The script never stops in the middle: it processes every ISBN, prints a summary,
and exits with code 1 if any ISBN failed.

Usage:
    download-covers.py                  sync all covers
    download-covers.py import <url> <isbn>   download one cover from a custom url
"""

import io
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content" / "synced"
COVERS_DIR = REPO_ROOT / "assets" / "book-covers"
OPENLIBRARY_URL = "https://covers.openlibrary.org/b/isbn/{isbn}.jpg?default=false"

OTHER_FORMATS = (".jpg", ".jpeg", ".png", ".gif", ".tif", ".tiff", ".bmp")
WEBP_QUALITY = 80
MIN_COVER_SIZE = 50  # anything smaller is a placeholder, not a real cover
RETRIES = 3
TIMEOUT_SECONDS = 20

ISBN_LINE = re.compile(r"^isbn13:\s*(.+?)\s*$", re.MULTILINE)


class CoverError(Exception):
    """A problem with one single cover. Never stops the whole run."""


def log(message: str) -> None:
    print(message, flush=True)


# ---------- finding books ----------


def normalize_isbn(raw: str) -> str | None:
    """Turn '978-0-7356-0916-7' or '"9780735609167"' into '9780735609167'."""
    isbn = re.sub(r"[^0-9Xx]", "", raw).upper()
    if len(isbn) not in (10, 13):
        return None
    return isbn


def collect_isbns() -> list[str]:
    if not CONTENT_DIR.is_dir():
        log(f"ERROR: content folder not found: {CONTENT_DIR}")
        sys.exit(2)

    isbns: list[str] = []
    for md_file in sorted(CONTENT_DIR.glob("**/*.md")):
        try:
            text = md_file.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            log(f"WARNING: could not read {md_file}: {e}")
            continue

        match = ISBN_LINE.search(text)
        if not match:
            continue

        isbn = normalize_isbn(match.group(1))
        if isbn is None:
            log(
                f"WARNING: bad isbn13 value {match.group(1)!r} in {md_file.relative_to(REPO_ROOT)}"
            )
            continue

        if isbn not in isbns:
            isbns.append(isbn)
    return isbns


# ---------- writing covers ----------


def webp_path(isbn: str) -> Path:
    return COVERS_DIR / f"{isbn}.webp"


def find_other_format(isbn: str) -> Path | None:
    for ext in OTHER_FORMATS:
        for candidate in (
            COVERS_DIR / f"{isbn}{ext}",
            COVERS_DIR / f"{isbn}{ext.upper()}",
        ):
            if candidate.is_file():
                return candidate
    return None


def write_webp(img: Image.Image, isbn: str) -> None:
    """Save as .webp. Write to a temp file first so a crash never leaves a half file."""
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA" if "A" in img.getbands() else "RGB")

    dest = webp_path(isbn)
    tmp = dest.with_name(dest.name + ".tmp")
    try:
        img.save(tmp, "WEBP", quality=WEBP_QUALITY)
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)


def open_image(data: bytes) -> Image.Image:
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except Exception as e:
        raise CoverError(f"data is not a valid image: {e}") from e
    if img.width < MIN_COVER_SIZE or img.height < MIN_COVER_SIZE:
        raise CoverError(
            f"image is only {img.width}x{img.height}, looks like a placeholder"
        )
    return img


def convert_cover(src: Path, isbn: str) -> None:
    try:
        with Image.open(src) as img:
            img.load()
            write_webp(img, isbn)
    except CoverError:
        raise
    except Exception as e:
        raise CoverError(f"could not convert {src.name}: {e}") from e


# ---------- downloading ----------


def fetch(url: str) -> bytes:
    """GET with retries. 404 is returned immediately, other errors are retried."""
    last_error: Exception | None = None
    for attempt in range(1, RETRIES + 1):
        request = urllib.request.Request(url, headers={"User-Agent": "download-covers"})
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return response.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise CoverError("no cover found (404)") from e
            last_error = CoverError(f"HTTP {e.code} from server")
        except (urllib.error.URLError, OSError) as e:
            last_error = CoverError(f"network error: {e}")

        if attempt < RETRIES:
            time.sleep(attempt)  # 1s, then 2s

    assert last_error is not None
    raise last_error


def download_cover(isbn: str, url: str | None = None) -> None:
    url = url or OPENLIBRARY_URL.format(isbn=isbn)
    data = fetch(url)
    img = open_image(data)
    write_webp(img, isbn)


# ---------- commands ----------


def sync() -> int:
    isbns = collect_isbns()
    if not isbns:
        log(f"No ISBNs found under {CONTENT_DIR}")
        return 0

    present = converted = downloaded = 0
    errors: list[tuple[str, str]] = []

    for isbn in isbns:
        if webp_path(isbn).is_file():
            present += 1
            continue

        try:
            other = find_other_format(isbn)
            if other is not None:
                try:
                    convert_cover(other, isbn)
                    converted += 1
                    log(f"Converted:  {other.name} -> {isbn}.webp")
                except CoverError as e:
                    log(f"WARNING: {isbn}: {e}. Trying download instead.")
                    download_cover(isbn)
                    downloaded += 1
                    log(f"Downloaded: {isbn}")
            else:
                download_cover(isbn)
                downloaded += 1
                log(f"Downloaded: {isbn}")

            if not webp_path(isbn).is_file():
                raise CoverError("webp file is still missing after processing")

        except CoverError as e:
            errors.append((isbn, str(e)))
        except Exception as e:  # anything unexpected: record it, keep going
            errors.append((isbn, f"unexpected {type(e).__name__}: {e}"))

    log("")
    log(
        f"Summary: {len(isbns)} books, {present} already present, "
        f"{converted} converted, {downloaded} downloaded, {len(errors)} failed"
    )
    for isbn, message in errors:
        log(f"ERROR {isbn}: {message}")

    return 1 if errors else 0


def import_cover(url: str, raw_isbn: str) -> int:
    isbn = normalize_isbn(raw_isbn)
    if isbn is None:
        log(f"ERROR: {raw_isbn!r} is not a valid ISBN")
        return 1
    try:
        download_cover(isbn, url)
    except CoverError as e:
        log(f"ERROR {isbn}: {e}")
        return 1
    log(f"Imported: {isbn}")
    return 0


def main() -> int:
    COVERS_DIR.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 1 and sys.argv[1] == "import":
        if len(sys.argv) != 4:
            log("Usage: download-covers.py import <url> <isbn>")
            return 2
        return import_cover(sys.argv[2], sys.argv[3])

    if len(sys.argv) > 1:
        log(f"Unknown command: {sys.argv[1]}")
        log(__doc__)
        return 2

    return sync()


if __name__ == "__main__":
    sys.exit(main())
