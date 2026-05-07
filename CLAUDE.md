# DevTracker — Contexto para Claude Code

## O que é
Rastreador de tempo de desenvolvimento. Django + SQLite + HTML/CSS puro.

## Stack
Backend: Django, SQLite | Frontend: HTML/CSS/JS puro | Python 3.10+, virtualenv em .venv/

## Modelos
- Project: name, slug, description, path, language, color
- Session: project FK, started_at, ended_at, notes, auto_closed
- Event: session FK, event_type (session_start/end, server_start/stop), timestamp

## Lógica de tempo
Tempo codando = intervalos sem server ativo | Tempo testando = intervalos com server ativo
Calculado nas properties do modelo Session, não armazenado.

## API
POST /api/new-project/ | POST /api/start-session/ | POST /api/run-server/
POST /api/stop-server/ | POST /api/end-session/ | GET /api/status/

## Comandos globais (em ~/.local/bin/)
new-project | start-session | run-server | stop-server | end-session

## Backup
end-session faz git add db.sqlite3 && git commit && git push automaticamente.
