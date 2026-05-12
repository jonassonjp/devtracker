# DevTracker

Rastreador de tempo de desenvolvimento pessoal. Registra quanto tempo você passa **codando** e **testando** em cada projeto, com histórico visual e backup automático no GitHub.

## Como funciona

O DevTracker roda como um servidor local em segundo plano. Você interage com ele via comandos de terminal enquanto trabalha nos seus projetos. Ao final de cada sessão, os dados são salvos e enviados automaticamente para o GitHub.

### Divisão do tempo

Cada sessão distingue dois tipos de atividade:

- **Codando** — tempo passado escrevendo código (sem servidor de teste ativo)
- **Testando** — tempo com o servidor da aplicação rodando (`run-server`)
- **Útil** — soma dos dois (tempo de pausa é descartado)

O cálculo é feito a partir de eventos registrados na sessão, não por polling.

## Interface web

Acesse `http://localhost:7000` após iniciar o servidor.

| Página | URL |
|--------|-----|
| Dashboard geral | `/` |
| Lista de projetos | `/projects/` |
| Detalhe do projeto | `/projects/<slug>/` |
| Editar projeto | `/projects/<slug>/edit/` |

### Dashboard

- Tempo útil de hoje, da semana e total acumulado
- Heatmap de atividade dos últimos 12 meses
- Ranking de projetos por tempo
- 10 sessões mais recentes

## Fluxo de uso

```bash
# 1. Dentro da pasta do projeto, inicia a sessão
start-session

# 2. Codando normalmente...

# 3. Ao subir o servidor para testar
run-server

# 4. Quando parar os testes
stop-server

# 5. Ao terminar o trabalho do dia
end-session "comentário opcional"
```

O `end-session` exibe um resumo da sessão e faz backup automático do banco de dados no GitHub.

## Stack

- **Backend:** Python 3.10+, Django, SQLite
- **Frontend:** HTML, CSS e JavaScript puro (sem frameworks)
- **Servidor:** Django dev server, apenas uso local

## Estrutura do projeto

```
devtracker/
├── commands/          # Scripts dos comandos globais
│   ├── new-project
│   ├── start-session
│   ├── run-server
│   ├── stop-server
│   └── end-session
├── tracker/           # App Django principal
│   ├── models.py      # Project, Session, Event
│   ├── views.py       # Views e endpoints da API
│   ├── urls.py        # Roteamento
│   └── templates/     # Interface web
├── devtracker/        # Configurações Django
├── install.sh         # Script de instalação
├── run.sh             # Inicia o servidor
└── db.sqlite3         # Banco de dados (versionado para backup)
```

## Documentação

- [Instalação](docs/INSTALACAO.md)
- [Comandos](docs/COMANDOS.md)
