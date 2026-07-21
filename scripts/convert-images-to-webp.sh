#!/usr/bin/env bash
set -euo pipefail

# Convert JPEG and PNG images in Hugo page bundles to WebP, in place.
# JPEGs are re-encoded as high quality lossy WebP; PNGs become lossless
# WebP so diagrams and screenshots stay sharp. EXIF orientation is baked
# into the pixels so images always render upright. Each original file is
# removed after a successful conversion and every Markdown reference to it
# in the same bundle is repointed at the new .webp file.

usage() {
  cat <<'EOF'
Usage: scripts/convert-images-to-webp.sh [DIR]

  DIR   Directory to scan (default: content)

Environment:
  QUALITY   Lossy WebP quality for JPEGs, 1-100 (default: 90)
  DRY_RUN   Set to 1 to print planned actions without changing anything
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

ROOT="${1:-content}"
QUALITY="${QUALITY:-90}"
DRY_RUN="${DRY_RUN:-0}"

if [[ ! -d "$ROOT" ]]; then
  echo "error: '$ROOT' is not a directory" >&2
  exit 1
fi

if command -v magick >/dev/null 2>&1; then
  IM=(magick)
elif command -v convert >/dev/null 2>&1; then
  IM=(convert)
else
  echo "error: ImageMagick not found. Install it with: brew install imagemagick" >&2
  exit 1
fi

filesize() { wc -c < "$1" | tr -d ' '; }

repoint_references() {
  local dir="$1" old="$2" new="$3" md
  while IFS= read -r -d '' md; do
    OLD="$old" NEW="$new" perl -pi -e 's/\Q$ENV{OLD}\E/$ENV{NEW}/g' "$md"
  done < <(find "$dir" -maxdepth 1 -type f -name '*.md' -print0)
}

total_before=0
total_after=0
converted=0
skipped=0

while IFS= read -r -d '' src; do
  ext_lc="$(printf '%s' "${src##*.}" | tr '[:upper:]' '[:lower:]')"
  dst="${src%.*}.webp"

  if [[ -e "$dst" ]]; then
    echo "skip (target exists): $src" >&2
    skipped=$((skipped + 1))
    continue
  fi

  if [[ "$ext_lc" == "png" ]]; then
    encode=(-auto-orient -strip -define webp:lossless=true -define webp:method=6)
    mode="lossless"
  else
    encode=(-auto-orient -strip -quality "$QUALITY" -define webp:method=6)
    mode="q${QUALITY}"
  fi

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "would convert ($mode): $src -> $dst"
    continue
  fi

  before=$(filesize "$src")
  "${IM[@]}" "$src" "${encode[@]}" "$dst"
  after=$(filesize "$dst")
  rm -f "$src"
  repoint_references "$(dirname "$src")" "$(basename "$src")" "$(basename "$dst")"

  total_before=$((total_before + before))
  total_after=$((total_after + after))
  converted=$((converted + 1))
  echo "ok ($mode): ${src##*/} -> ${dst##*/}  (${before} -> ${after} bytes)"
done < <(find "$ROOT" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) -print0)

echo
if [[ "$DRY_RUN" == "1" ]]; then
  echo "dry run: no files changed"
  exit 0
fi

echo "converted ${converted} image(s), skipped ${skipped}"
awk -v b="$total_before" -v a="$total_after" 'BEGIN {
  saved = b - a
  pct = (b > 0) ? saved / b * 100 : 0
  printf "before: %.2f MB\nafter:  %.2f MB\nsaved:  %.2f MB (%.1f%%)\n", \
    b / 1048576, a / 1048576, saved / 1048576, pct
}'
