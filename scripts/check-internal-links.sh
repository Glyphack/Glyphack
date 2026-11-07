#!/bin/sh
# Checks the links inside the built site that point to the site's own pages
# and files. Links to other websites are skipped. Exits with an error when a
# link points to a page or file that does not exist.
set -eu

cd "$(dirname "$0")/.."

exec lychee --offline --root-dir "$PWD/public" --no-progress 'public/**/*.html'
