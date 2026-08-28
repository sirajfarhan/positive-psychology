#!/usr/bin/env bash
# Pull the live skill into the repo (live copy at ~/.claude/skills is the one
# Claude Code runs; this repo is the canonical, versioned copy).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
rsync -a --delete \
  --exclude node_modules/ --exclude .venv/ --exclude __pycache__/ \
  ~/.claude/skills/learn-optimism/ "$HERE/learn-optimism/"
echo "synced live -> repo. review with: git -C $HERE/.. diff"
