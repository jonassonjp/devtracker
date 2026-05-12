# DevTracker

Rastreador de tempo de desenvolvimento pessoal. Registra quanto tempo você passa em cada projeto, com histórico visual e dashboard web.

## Como funciona

Os comandos de terminal gravam diretamente no banco de dados SQLite — **sem precisar que o servidor esteja rodando**. O servidor (`run-server`) é usado apenas para visualizar o dashboard no navegador.

Ao iniciar uma sessão, o PyCharm é aberto automaticamente no diretório do projeto.

## Interface web

Execute `run-server` e acesse `http://localhost:7000`.

| Página | URL |
|--------|-----|
| Dashboard geral | `/` |
| Lista de projetos | `/projects/` |
| Detalhe do projeto | `/projects/<slug>/` |
| Editar projeto | `/projects/<slug>/edit/` |

### Dashboard

- Tempo de hoje, da semana e total acumulado
- Heatmap de atividade dos últimos 12 meses
- Ranking de projetos por tempo
- 10 sessões mais recentes

## Fluxo de uso

```bash
# 1. Cadastra o projeto (uma única vez)
new-project --name "Minha API" --nickname minhaapi --dir ~/workspace/minhaapi

# 2. Inicia a sessão — abre o PyCharm automaticamente
start-session minhaapi

# 3. Trabalha no código...

# 4. Encerra a sessão e exibe o resumo
end-session
```

## Stack

- **Backend:** Python 3.10+, Django, SQLite
- **Frontend:** HTML, CSS e JavaScript puro (sem frameworks)
- **Dashboard:** Django dev server, apenas uso local

## Estrutura do projeto

```
devtracker/
├── commands/          # Scripts dos comandos globais
│   ├── _lib.py        # Utilitários compartilhados (Django setup, PyCharm, formatação)
│   ├── new-project
│   ├── start-session
│   ├── end-session
│   ├── run-server
│   └── reset-data
├── tracker/           # App Django principal
│   ├── models.py      # Project, Session, Event
│   ├── views.py       # Views e endpoints da API
│   ├── urls.py        # Roteamento
│   ├── tests.py       # Suite de testes (33 testes)
│   └── templates/     # Interface web
├── devtracker/        # Configurações Django
├── install.sh         # Script de instalação
├── run.sh             # Inicia o servidor do dashboard
└── db.sqlite3         # Banco de dados
```

## Testes

```bash
.venv/bin/python manage.py test tracker
```

33 testes cobrindo todos os comandos e cenários de erro.

## Documentação

- [Instalação](docs/INSTALACAO.md)
- [Comandos](docs/COMANDOS.md)
