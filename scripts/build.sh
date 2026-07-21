#!/bin/sh
# Builds the site with the Hugo version pinned in mise.toml.
# Installs mise first if it is not already available.
set -eu

cd "$(dirname "$0")/.."

# Ignore .tool-versions files from the environment, such as the one the
# Cloudflare build image keeps in the build home directory. Tool versions
# come only from mise.toml and mise.lock.
export MISE_OVERRIDE_TOOL_VERSIONS_FILENAMES=none

if ! command -v mise >/dev/null 2>&1; then
  curl -fsSL https://mise.run | sh
  PATH="$HOME/.local/bin:$PATH"
fi

mise trust --quiet || true
mise install
exec mise exec -- hugo
