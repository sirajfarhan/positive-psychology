#!/usr/bin/env bash
# Bring the page up, idempotently. Safe to call on every invocation -- if it is
# already running this only prints the URL and exits.
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

# The venv and node_modules live beside the store, not inside the plugin.
# A plugin update replaces the installed folder wholesale, and 122MB of
# frontend dependencies should not be downloaded again every time it does.
STATE="${XDG_DATA_HOME:-$HOME/.local/share}/positive-psychology"
DEPS="$STATE/deps"
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
    "$VENV/bin/pip" install -q fastapi uvicorn
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
