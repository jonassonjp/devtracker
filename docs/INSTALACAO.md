# Instalação

## Pré-requisitos

- Python 3.10 ou superior
- Git configurado
- `~/.local/bin` no seu `PATH`

## Passo a passo

### 1. Clone o repositório

```bash
git clone git@github.com:jonassonjp/devtracker.git ~/workspace/devtracker
cd ~/workspace/devtracker
```

### 2. Execute o instalador

```bash
./install.sh
```

O script realiza automaticamente:

- Cria um virtualenv em `.venv/`
- Instala o Django
- Cria o banco de dados SQLite (`db.sqlite3`)
- Instala os cinco comandos globais em `~/.local/bin/`

### 3. Adicione `~/.local/bin` ao PATH (se ainda não estiver)

Adicione ao final do seu `~/.bashrc` ou `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Depois recarregue o shell:

```bash
source ~/.bashrc
```

### 4. Inicie o servidor

```bash
~/workspace/devtracker/run.sh
```

O servidor roda em `http://localhost:7000`. Deixe-o aberto em um terminal separado (ou em segundo plano).

> **Importante:** o servidor precisa estar rodando para que os comandos funcionem.

### 5. Configure a variável de ambiente (obrigatório)

Os comandos apontam por padrão para a porta `8000`. Como o servidor roda na porta `7000`, adicione ao seu `~/.bashrc`:

```bash
export DEVTRACKER_URL="http://127.0.0.1:7000"
```

Recarregue:

```bash
source ~/.bashrc
```

### 6. Configure o backup automático

O comando `end-session` faz commit e push do banco de dados. Para funcionar, o repositório precisa ter um remote configurado:

```bash
cd ~/workspace/devtracker
git remote add origin git@github.com:jonassonjp/devtracker.git
```

## Verificação

Com o servidor rodando, teste um dos comandos:

```bash
new-project "Meu Projeto Teste"
```

Se retornar `✅ Projeto criado`, a instalação está funcionando.

## Desinstalação

Para remover os comandos globais:

```bash
rm ~/.local/bin/new-project ~/.local/bin/start-session \
   ~/.local/bin/run-server ~/.local/bin/stop-server \
   ~/.local/bin/end-session
```

Para remover o servidor e os dados:

```bash
rm -rf ~/workspace/devtracker
```
