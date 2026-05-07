cd ~/workspace/devtracker

# Cria o venv com o Python do sistema (ignora o pyenv)
/usr/bin/python3 -m venv .venv

# Instala o Django
.venv/bin/pip install django

# Cria o banco
.venv/bin/python manage.py migrate

# Instala os comandos globais
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
for CMD in new-project start-session run-server stop-server end-session; do
  cat > "$BIN_DIR/$CMD" << WRAPPER
#!/usr/bin/env bash
export DEVTRACKER_DIR="$HOME/devtracker"
export DEVTRACKER_URL="\${DEVTRACKER_URL:-http://127.0.0.1:8000}"
exec "$HOME/devtracker/commands/$CMD" "\$@"
WRAPPER
  chmod +x "$BIN_DIR/$CMD"
  echo "✓ $CMD"
done

echo "✅ Instalação concluída!"