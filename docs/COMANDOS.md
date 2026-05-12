# Comandos

Todos os comandos se comunicam com o servidor local via HTTP. O servidor precisa estar rodando (`run.sh`) para que funcionem.

A URL do servidor é lida da variável de ambiente `DEVTRACKER_URL` (padrão: `http://127.0.0.1:8000`). Veja a [instalação](INSTALACAO.md) para configurar corretamente.

---

## new-project

Cadastra um novo projeto no DevTracker.

```bash
new-project <nome>
```

**Exemplos:**

```bash
new-project MinhaAPI
new-project "Meu Site Pessoal"
```

- O slug é gerado automaticamente a partir do nome (ex: `meu-site-pessoal`)
- O caminho atual (`pwd`) é salvo como localização do projeto
- Se o projeto já existir, avisa sem criar duplicata
- Após criar, acesse `/projects/<slug>/edit/` para adicionar descrição, linguagem e cor

---

## start-session

Inicia uma sessão de trabalho para o projeto da pasta atual.

```bash
start-session
```

- O projeto é detectado automaticamente pelo nome da pasta atual
- O projeto precisa existir (criado com `new-project`). Caso contrário, o comando informa o slug esperado
- Se houver outra sessão aberta, ela é encerrada automaticamente (`auto_closed`)
- Atualiza o caminho do projeto para o diretório atual

**Execute sempre dentro da pasta do projeto que você vai trabalhar.**

---

## run-server

Registra o início do modo de teste e executa o servidor da sua aplicação.

```bash
run-server
run-server "comando customizado"
```

**Exemplos:**

```bash
run-server                          # executa: python manage.py runserver
run-server "npm start"
run-server "flask run --port 5000"
```

- Marca um evento `server_start` na sessão ativa — a partir daqui o tempo é contado como **testando**
- Em seguida executa o comando informado (ou `python manage.py runserver` por padrão)
- Quando você encerrar o comando (Ctrl+C), o servidor da aplicação para, mas o modo teste segue ativo no DevTracker até você rodar `stop-server`

---

## stop-server

Registra o fim do modo de teste.

```bash
stop-server
```

- Marca um evento `server_stop` na sessão ativa
- O tempo volta a ser contado como **codando**
- Não encerra o servidor da aplicação — apenas registra que o período de teste acabou

---

## end-session

Encerra a sessão de trabalho, exibe o resumo e faz backup no GitHub.

```bash
end-session
end-session "notas opcionais sobre o que foi feito"
```

**Exemplo de saída:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅  Sessão encerrada — MinhaAPI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐  Horário:    09:15 → 11:42  (2h 27m)
⌨️   Codando:    1h 53m
🔵  Testando:   22m
💪  Útil:       2h 15m
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Após exibir o resumo, o comando:

1. Entra no diretório do DevTracker (`~/workspace/devtracker`)
2. Faz `git add db.sqlite3`
3. Cria um commit: `backup: <projeto> — <data hora>`
4. Executa `git push`

Se o push falhar, o commit é mantido localmente e você pode subir manualmente depois.

---

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `DEVTRACKER_URL` | `http://127.0.0.1:8000` | URL do servidor DevTracker |
| `DEVTRACKER_DIR` | `$HOME/devtracker` | Caminho do repositório DevTracker (usado pelo `end-session` para o backup) |

Configure no seu `~/.bashrc`:

```bash
export DEVTRACKER_URL="http://127.0.0.1:7000"
export DEVTRACKER_DIR="$HOME/workspace/devtracker"
```

---

## Fluxo completo de uma sessão

```bash
# Dentro da pasta do projeto
start-session

# ... trabalha no código ...

run-server "npm run dev"    # marca início do teste, sobe a aplicação

# ... testa no navegador ...

# Ctrl+C para parar a aplicação
stop-server                 # marca fim do teste

# ... mais código ...

end-session "implementei o login com JWT"
```
