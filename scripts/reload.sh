#!/usr/bin/env bash
# Push this repo into the installed plugin, after editing it.
#
# The repo is the source. `claude plugin install` copies it into the plugin
# cache, so an edit here is not live until that copy is refreshed. Run this.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$ROOT/plugins/positive-psychology/skills/learn-optimism/app"

# A local-path install copies the working tree as it stands rather than as git
# sees it, so anything left in frontend/ rides along into the plugin cache.
# run.sh puts the real packages in your cache directory and leaves a symlink
# here, and a copied symlink pointing into someone else's cache is worse than
# no symlink at all. The venv needs no cleaning: it has lived outside the
# plugin since the artifacts moved, and run.sh owns where.
rm -rf "$APP/frontend/node_modules"

# The dev server holds open handles inside node_modules, and the cache cannot
# be replaced underneath it.
bash "$APP/run.sh" stop >/dev/null 2>&1 || true

claude plugin marketplace update positive-psychology

# Uninstall first. `install` no-ops on an installed plugin, and `update`
# compares version numbers, so neither picks up an edit made at the same
# version -- which is every edit during development.
claude plugin uninstall positive-psychology >/dev/null 2>&1 || true
rm -rf "$HOME/.claude/plugins/cache/positive-psychology"
claude plugin install positive-psychology@positive-psychology
echo "reloaded from $ROOT"
