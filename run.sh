#!/usr/bin/env bash
DEVTRACKER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$DEVTRACKER_DIR/.venv"
[ ! -d "$VENV_DIR" ] && echo "❌  Execute ./install.sh primeiro." && exit 1
echo "⬡  DevTracker em http://localhost:8000  (Ctrl+C para encerrar)"; echo ""
cd "$DEVTRACKER_DIR"
"$VENV_DIR/bin/python" manage.py runserver 127.0.0.1:8000
