#!/usr/bin/env bash
# Sugestão de pre-commit hook — copie para .git/hooks/pre-commit e dê chmod +x
set -e
DEVTRACKER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$DEVTRACKER_DIR/.venv/bin/python" "$DEVTRACKER_DIR/manage.py" test tracker --verbosity=0
