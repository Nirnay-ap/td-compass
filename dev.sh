#!/usr/bin/env bash
# Convenience script: starts the TD Compass backend and frontend together.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Backend ---
cd "$ROOT/backend"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  ./.venv/bin/pip install -q -r requirements.txt
fi
[ -f .env ] && set -a && . ./.env && set +a
./.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACK_PID=$!

# --- Frontend ---
cd "$ROOT/frontend"
[ -d node_modules ] || npm install
BACKEND_URL="http://localhost:8000" npm run dev &
FRONT_PID=$!

trap 'kill $BACK_PID $FRONT_PID 2>/dev/null || true' EXIT
echo "TD Compass running — frontend http://localhost:3000  ·  backend http://localhost:8000"
wait
