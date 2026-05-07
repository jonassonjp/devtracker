#!/usr/bin/env bash
# install_fix.sh — Instalação corrigida para ~/workspace/devtracker
set -e

DEVTRACKER_DIR="$HOME/workspace/devtracker"
BIN_DIR="$HOME/.local/bin"
VENV_DIR="$DEVTRACKER_DIR/.venv"

echo ""
echo "⬡  DevTracker — Instalação"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$DEVTRACKER_DIR"

# 1. Instala pip no venv se não existir
if [ ! -f "$VENV_DIR/bin/pip" ]; then
  echo "📦  Instalando pip no venv..."
  curl -s https://bootstrap.pypa.io/get-pip.py | "$VENV_DIR/bin/python3"
  echo "   ✓ pip instalado"
fi

# 2. Instala Django
echo "📦  Instalando Django..."
"$VENV_DIR/bin/pip" install --quiet django
echo "   ✓ Django instalado"

# 3. Roda migrations
echo "🗄️   Configurando banco..."
"$VENV_DIR/bin/python" manage.py migrate --run-syncdb 2>/dev/null || "$VENV_DIR/bin/python" manage.py migrate
echo "   ✓ Banco criado"

# 4. Instala comandos globais
echo "🔧  Instalando comandos globais em $BIN_DIR..."
mkdir -p "$BIN_DIR"
for CMD in new-project start-session run-server stop-server end-session; do
  cat > "$BIN_DIR/$CMD" << WRAPPER
#!/usr/bin/env bash
export DEVTRACKER_DIR="$HOME/workspace/devtracker"
export DEVTRACKER_URL="\${DEVTRACKER_URL:-http://127.0.0.1:8000}"
exec "$HOME/workspace/devtracker/commands/$CMD" "\$@"
WRAPPER
  chmod +x "$BIN_DIR/$CMD"
  echo "   ✓ $CMD"
done

# 5. Atualiza run.sh para usar o venv correto
cat > "$DEVTRACKER_DIR/run.sh" << 'RUNEOF'
#!/usr/bin/env bash
DEVTRACKER_DIR="$HOME/workspace/devtracker"
VENV_DIR="$DEVTRACKER_DIR/.venv"
[ ! -f "$VENV_DIR/bin/python" ] && echo "❌  Execute ./install_fix.sh primeiro." && exit 1
echo "⬡  DevTracker em http://localhost:8000  (Ctrl+C para encerrar)"
echo ""
cd "$DEVTRACKER_DIR"
"$VENV_DIR/bin/python" manage.py runserver 127.0.0.1:8000
RUNEOF
chmod +x "$DEVTRACKER_DIR/run.sh"

# 6. Verifica PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo ""
  echo "⚠️   $BIN_DIR não está no PATH. Adicione ao ~/.bashrc:"
  echo '   export PATH="$HOME/.local/bin:$PATH"'
  echo "   Depois rode: source ~/.bashrc"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅  Instalação concluída!"
echo ""
echo "   Inicie o servidor:  cd ~/workspace/devtracker && ./run.sh"
echo "   Dashboard:          http://localhost:8000"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
