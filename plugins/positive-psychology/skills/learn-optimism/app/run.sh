#!/usr/bin/env bash
# Bring the page up, idempotently. Safe to call on every invocation -- when
# both halves are already running it says so, prints the URL, and still opens
# the browser unless --no-open asks it not to.
#
#   ./run.sh            start whatever is missing, then open the browser
#   ./run.sh --no-open  same, without opening a browser
#   ./run.sh status     what is up
#   ./run.sh stop       shut both down

set -euo pipefail

APP="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_PORT=8787
WEB_PORT=5173
API_URL="http://127.0.0.1:${API_PORT}/api/health"
WEB_URL="http://localhost:${WEB_PORT}"
LOG_DIR="${TMPDIR:-/tmp}/learn-optimism"
mkdir -p "$LOG_DIR"

# The venv and node_modules live outside the plugin. A plugin update replaces
# the installed folder wholesale, and 122MB of frontend dependencies should not
# be downloaded again every time it does.
#
# They are this app's own business, so this script resolves them rather than
# asking the store module. The store lives in the platform's data directory
# and belongs to the skill; these are build artifacts, they belong here, and
# the two answer to nobody in common. Cache is the right home for them because
# every byte can be rebuilt from package-lock.json and pip.
# Windows gets no branch of its own here, deliberately. This script already
# needs lsof, curl and nohup, so it runs under WSL or Git Bash rather than
# cmd.exe, and WSL reports Linux and wants ~/.cache anyway. The store is the
# one that has a real Windows home, and optimism_db.py handles that.
if [ -n "${XDG_CACHE_HOME:-}" ]; then
  CACHE="$XDG_CACHE_HOME"
elif [ "$(uname -s)" = "Darwin" ]; then
  CACHE="$HOME/Library/Caches"
else
  CACHE="$HOME/.cache"
fi
DEPS="$CACHE/positive-psychology/deps"
VENV="$DEPS/backend-venv"
mkdir -p "$DEPS"

# npm resolves node_modules next to package.json, so the real folder sits in
# DEPS and the app gets a link to it. Install writes through the link.
link_node_modules() {
  local target="$DEPS/node_modules" link="$APP/frontend/node_modules"
  [ -d "$link" ] && [ ! -L "$link" ] && return 0   # a real folder already there, leave it
  mkdir -p "$target"
  [ -L "$link" ] && [ "$(readlink "$link")" = "$target" ] && return 0
  rm -f "$link"
  ln -s "$target" "$link"
}

up() { curl -sf -o /dev/null --max-time 1 "$1" 2>/dev/null; }

wait_for() { # url, seconds
  local i=0
  until up "$1"; do
    i=$((i + 1))
    [ "$i" -gt "$(( $2 * 4 ))" ] && return 1
    sleep 0.25
  done
}

case "${1:-start}" in
  status)
    up "$API_URL" && echo "backend  up   :${API_PORT}" || echo "backend  down"
    up "$WEB_URL" && echo "frontend up   :${WEB_PORT}" || echo "frontend down"
    echo "deps     $DEPS"
    exit 0
    ;;
  stop)
    # by port, not by command line -- the process may have been launched with a
    # relative path, from another cwd, or by something other than this script
    for spec in "backend ${API_PORT}" "frontend ${WEB_PORT}"; do
      name="${spec%% *}"; port="${spec##* }"
      pids="$(lsof -ti "tcp:${port}" -sTCP:LISTEN 2>/dev/null || true)"
      if [ -n "$pids" ]; then
        echo "$pids" | xargs kill 2>/dev/null || true
        echo "${name} stopped"
      else
        echo "${name} was not running"
      fi
    done
    exit 0
    ;;
esac

# --- backend -------------------------------------------------------------
if up "$API_URL"; then
  echo "backend already up"
else
  if [ ! -x "$VENV/bin/python" ]; then
    echo "first run: creating backend venv"
    rm -rf "$VENV"
    python3 -m venv "$VENV"
    # -m pip, not bin/pip: a shebang line breaks at the first space, so the
    # generated pip script would not run from a path containing one.
    "$VENV/bin/python" -m pip install -q fastapi uvicorn
  fi
  nohup "$VENV/bin/python" "$APP/backend/server.py" \
    > "$LOG_DIR/api.log" 2>&1 &
  wait_for "$API_URL" 15 || { echo "backend failed to start; see $LOG_DIR/api.log"; exit 1; }
  echo "backend started"
fi

# --- frontend ------------------------------------------------------------
if up "$WEB_URL"; then
  echo "frontend already up"
else
  link_node_modules
  if [ ! -d "$APP/frontend/node_modules/vite" ]; then
    echo "first run: installing frontend deps"
    (cd "$APP/frontend" && npm install --silent)
  fi
  (cd "$APP/frontend" && nohup npm run dev > "$LOG_DIR/web.log" 2>&1 &)
  wait_for "$WEB_URL" 25 || { echo "frontend failed to start; see $LOG_DIR/web.log"; exit 1; }
  echo "frontend started"
fi

echo "$WEB_URL"

if [ "${1:-}" != "--no-open" ] && command -v open >/dev/null 2>&1; then
  open "$WEB_URL"
fi
