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

claude plugin marketplace update positive-psychology
claude plugin install positive-psychology@positive-psychology
echo "reloaded from $ROOT"
