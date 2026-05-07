#!/usr/bin/env bash
set -e
DEVTRACKER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
VENV_DIR="$DEVTRACKER_DIR/.venv"
echo ""; echo "⬡  DevTracker — Instalação"; echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦  Instalando dependências Python..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet django
echo "   ✓ Django instalado"
echo "🗄️   Configurando banco..."
cd "$DEVTRACKER_DIR"
"$VENV_DIR/bin/python" manage.py migrate --run-syncdb 2>/dev/null || "$VENV_DIR/bin/python" manage.py migrate
echo "   ✓ Banco criado"
echo "🔧  Instalando comandos globais em $BIN_DIR..."
mkdir -p "$BIN_DIR"
for CMD in new-project start-session run-server stop-server end-session; do
  cat > "$BIN_DIR/$CMD" << WRAPPER
#!/usr/bin/env bash
export DEVTRACKER_DIR="$DEVTRACKER_DIR"
export DEVTRACKER_URL="\${DEVTRACKER_URL:-http://127.0.0.1:8000}"
exec "$DEVTRACKER_DIR/commands/$CMD" "\$@"
WRAPPER
  chmod +x "$BIN_DIR/$CMD"; echo "   ✓ $CMD"
done
[[ ":$PATH:" != *":$BIN_DIR:"* ]] && echo -e "\n⚠️   Adicione ao ~/.bashrc:\n   export PATH=\"\$HOME/.local/bin:\$PATH\"\n   Depois: source ~/.bashrc"
echo ""; echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; echo "✅  Instalação concluída!"
echo "   1. Inicie: ./run.sh"; echo "   2. Dashboard: http://localhost:8000"; echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
