# Instalação

## Pré-requisitos

- Python 3.10 ou superior
- Git configurado
- `~/.local/bin` no seu `PATH`
- PyCharm com o comando `charm` disponível (JetBrains Toolbox)

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

### 4. Configure a variável de ambiente

Adicione ao seu `~/.bashrc`:

```bash
export DEVTRACKER_DIR="$HOME/workspace/devtracker"
```

Recarregue:

```bash
source ~/.bashrc
```

## Verificação

Cadastre um projeto de teste:

```bash
new-project --name "Meu Projeto Teste" --nickname teste --dir /tmp
```

Se retornar `✅ Projeto criado`, a instalação está funcionando.

> Os comandos de terminal gravam diretamente no banco de dados — **não é necessário ter o servidor rodando** para usar `new-project`, `start-session`, `end-session` ou `reset-data`. O servidor (`run-server`) é usado apenas para visualizar o dashboard.

## Abrindo o dashboard

```bash
run-server
```

Abre o Django na porta `7000` e o navegador em `http://localhost:7000` automaticamente.

## Desinstalação

Para remover os comandos globais:

```bash
rm ~/.local/bin/new-project ~/.local/bin/start-session \
   ~/.local/bin/end-session ~/.local/bin/run-server \
   ~/.local/bin/reset-data
```

Para remover o servidor e os dados:

```bash
rm -rf ~/workspace/devtracker
```
