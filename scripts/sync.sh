#!/usr/bin/env bash
# Pull the live skill into the repo. The live copy at ~/.claude/skills is what
# Claude Code runs day to day; this repo is the canonical, versioned copy.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/plugins/positive-psychology/skills/learn-optimism"
rsync -a --delete \
  --exclude node_modules/ --exclude .venv/ --exclude __pycache__/ \
  ~/.claude/skills/learn-optimism/ "$DEST/"
echo "synced live -> $DEST"
