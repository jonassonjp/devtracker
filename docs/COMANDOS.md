# Comandos

Os comandos gravam diretamente no banco de dados SQLite via Django ORM — **sem precisar que o servidor esteja rodando**.

---

## new-project

Cadastra um novo projeto. Executa uma única vez por projeto.

```bash
# Com parâmetros
new-project --name "Nome do Projeto" --nickname apelido --dir ~/workspace/pasta

# Sem parâmetros — modo interativo (pergunta tudo)
new-project
```

**Parâmetros:**

| Parâmetro | Obrigatório | Descrição |
|-----------|-------------|-----------|
| `--name` | Sim | Nome completo (pode conter espaços, use aspas) |
| `--nickname` | Não | Apelido sem espaços, usado nos demais comandos. Derivado do nome se omitido |
| `--dir` | Não | Diretório do projeto. Usa o diretório atual se omitido |

**Comportamento:**
- Sem nenhum parâmetro: modo interativo — pergunta nome, apelido e diretório
- Com parâmetros: modo direto, sem prompts
- Após criar, abre o PyCharm no diretório informado
- Apelidos duplicados ou com caracteres especiais são rejeitados

**Exemplos:**

```bash
new-project --name "Minha API" --nickname minhaapi --dir ~/workspace/minhaapi
new-project --name "Site Pessoal"          # apelido derivado: site-pessoal
new-project                                # modo interativo
```

---

## start-session

Inicia uma sessão de trabalho e abre o PyCharm no diretório do projeto.

```bash
start-session <apelido>
```

**Comportamento:**
- Registra a hora de início no banco de dados
- Abre o PyCharm com o diretório do projeto
- Se houver outra sessão aberta, ela é encerrada automaticamente:
  - Sessão do **mesmo dia** → encerrada no momento atual
  - Sessão de **dia anterior** → encerrada às 23:59 daquele dia

**Exemplo:**

```bash
start-session minhaapi
```

---

## end-session

Encerra a sessão ativa e exibe o resumo.

```bash
end-session                  # encerra o que estiver ativo
end-session <apelido>        # encerra e valida que é o projeto esperado
end-session --notes "texto"  # adiciona anotação à sessão
```

**Comportamento:**
- Sem parâmetro: encerra qualquer sessão ativa
- Com apelido: encerra somente se a sessão ativa for desse projeto; caso contrário, exibe erro
- Sem sessão ativa: exibe informação e sai normalmente (sem erro)

**Exemplo de saída:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅  Sessão encerrada — Minha API
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕐  Horário:     09:15 → 11:42  (2h 27m)
📊  Total acum.: 14h 30m
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## run-server

Abre o dashboard web com o histórico de todos os projetos.

```bash
run-server
```

- Inicia o Django na porta `7000`
- Abre o navegador em `http://localhost:7000` automaticamente
- Encerre com `Ctrl+C`

> Este é o único comando que requer o servidor rodando — os demais comandos funcionam sem ele.

---

## reset-data

Apaga dados do DevTracker. Pede confirmação antes de agir.

```bash
reset-data --nickname <apelido>   # apaga projeto específico e suas sessões
reset-data                        # apaga todos os dados
reset-data -y                     # confirma sem perguntar
```

**Exemplos:**

```bash
reset-data --nickname minhaapi        # apaga o projeto "minhaapi"
reset-data --nickname minhaapi -y     # sem confirmação
reset-data -y                         # apaga tudo sem confirmação
```

---

## Fluxo completo de uma sessão

```bash
# Primeira vez: cadastra o projeto
new-project --name "Minha API" --nickname minhaapi --dir ~/workspace/minhaapi

# Início do dia de trabalho
start-session minhaapi         # registra início + abre PyCharm

# ... trabalha no código ...

end-session --notes "implementei autenticação JWT"   # registra fim + exibe resumo

# Para ver o histórico no navegador
run-server
```
