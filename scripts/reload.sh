#!/usr/bin/env bash
# Push this repo into the installed plugin, after editing it.
#
# The repo is the source. `claude plugin install` copies it into the plugin
# cache, so an edit here is not live until that copy is refreshed. Run this.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$ROOT/plugins/positive-psychology/skills/learn-optimism/app"

# Artifacts are gitignored, but a local-path install copies the working tree as
# it stands, not as git sees it. Left in place they are copied into the cache on
# every install, which is exactly the duplication run.sh exists to avoid.
rm -rf "$APP/frontend/node_modules" "$APP/backend/.venv"

# The dev server holds open handles inside node_modules, and the cache cannot
# be replaced underneath it.
bash "$APP/run.sh" stop >/dev/null 2>&1 || true

claude plugin marketplace update positive-psychology
# `install` is a no-op once installed, so a refresh has to go through update.
claude plugin update positive-psychology
echo "reloaded from $ROOT"
