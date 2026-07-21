# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow==12.2.0"]
# ///
"""Check images for GPS EXIF data and fail if any is found."""

import sys

from PIL import ExifTags, Image


def get_gps_tags(path):
    with Image.open(path) as img:
        exif = img.getexif()
        gps_ifd = exif.get_ifd(ExifTags.IFD.GPSInfo)

    return {
        ExifTags.GPSTAGS.get(tag, tag): value for tag, value in gps_ifd.items()
    }


def main():
    failed = False
    for path in sys.argv[1:]:
        gps_tags = get_gps_tags(path)
        if not gps_tags:
            continue
        failed = True
        print(f"{path}: GPS data found: {', '.join(str(t) for t in gps_tags)}")

    if failed:
        print("Remove GPS data from the images above before committing.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
