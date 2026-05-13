#!/usr/bin/env bash
set -e
DEVTRACKER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
VENV_DIR="$DEVTRACKER_DIR/.venv"

echo ""; echo "⬡  DevTracker — Instalação"; echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "📦  Instalando dependências Python..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet django anthropic python-dotenv
echo "   ✓ Django, anthropic e python-dotenv instalados"

echo "🔑  Configurando .env..."
if [[ ! -f "$DEVTRACKER_DIR/.env" ]]; then
  cp "$DEVTRACKER_DIR/.env.example" "$DEVTRACKER_DIR/.env"
  echo "   ✓ .env criado a partir de .env.example"
  echo "   ⚠️  Edite $DEVTRACKER_DIR/.env e adicione sua ANTHROPIC_API_KEY"
else
  echo "   ✓ .env já existe"
fi

echo "🗄️   Configurando banco..."
cd "$DEVTRACKER_DIR"
"$VENV_DIR/bin/python" manage.py migrate 2>/dev/null || "$VENV_DIR/bin/python" manage.py migrate --run-syncdb
echo "   ✓ Banco criado"

echo "🔧  Instalando comandos globais em $BIN_DIR..."
mkdir -p "$BIN_DIR"

# Comandos Python — executados via virtualenv
for CMD in new-project start-session end-session reset-data; do
  cat > "$BIN_DIR/$CMD" << WRAPPER
#!/usr/bin/env bash
export DEVTRACKER_DIR="$DEVTRACKER_DIR"
exec "$VENV_DIR/bin/python" "$DEVTRACKER_DIR/commands/$CMD" "\$@"
WRAPPER
  chmod +x "$BIN_DIR/$CMD"
  echo "   ✓ $CMD"
done

# run-server — script bash
cat > "$BIN_DIR/run-server" << WRAPPER
#!/usr/bin/env bash
export DEVTRACKER_DIR="$DEVTRACKER_DIR"
exec "$DEVTRACKER_DIR/commands/run-server" "\$@"
WRAPPER
chmod +x "$BIN_DIR/run-server"
echo "   ✓ run-server"

# claude-dev — script bash
cat > "$BIN_DIR/claude-dev" << WRAPPER
#!/usr/bin/env bash
exec "$DEVTRACKER_DIR/commands/claude-dev" "\$@"
WRAPPER
chmod +x "$BIN_DIR/claude-dev"
echo "   ✓ claude-dev"

[[ ":$PATH:" != *":$BIN_DIR:"* ]] && echo -e "\n⚠️   Adicione ao ~/.bashrc:\n   export PATH=\"\$HOME/.local/bin:\$PATH\"\n   Depois: source ~/.bashrc"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅  Instalação concluída!"
echo ""
echo "   Novo projeto:    new-project --name \"Nome\" --nickname apelido"
echo "   Iniciar sessão:  start-session <apelido>"
echo "   Encerrar:        end-session <apelido>"
echo "   Ver dashboard:   run-server"
echo "   Limpar dados:    reset-data [--nickname <apelido>]"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
