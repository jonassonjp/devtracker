#!/usr/bin/env bash
DEVTRACKER_DIR="$HOME/workspace/devtracker"
VENV_DIR="$DEVTRACKER_DIR/.venv"
[ ! -f "$VENV_DIR/bin/python" ] && echo "❌  Execute ./install_fix.sh primeiro." && exit 1
echo "⬡  DevTracker em http://localhost:8000  (Ctrl+C para encerrar)"
echo ""
cd "$DEVTRACKER_DIR"
"$VENV_DIR/bin/python" manage.py runserver 127.0.0.1:7000
