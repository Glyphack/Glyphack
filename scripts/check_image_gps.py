# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow==12.2.0"]
# ///
"""Check every image tracked in the repository for GPS EXIF data and fail if any is found."""

import subprocess
import sys
from pathlib import Path

from PIL import ExifTags, Image, UnidentifiedImageError

ROOT = Path(__file__).resolve().parent.parent


def tracked_files():
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    paths = [ROOT / name for name in result.stdout.split("\0") if name]
    return [path for path in paths if path.is_file()]


def get_gps_tags(path):
    with Image.open(path) as img:
        exif = img.getexif()
        gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)

    return {
        ExifTags.GPSTAGS.get(tag, tag): value for tag, value in gps_ifd.items()
    }


def main():
    failed = False
    for path in tracked_files():
        try:
            gps_tags = get_gps_tags(path)
        except UnidentifiedImageError:
            continue
        if not gps_tags:
            continue
        failed = True
        print(
            f"{path.relative_to(ROOT)}: GPS data found: "
            f"{', '.join(str(t) for t in gps_tags)}"
        )

    if failed:
        print("Remove GPS data from the images above before committing.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
