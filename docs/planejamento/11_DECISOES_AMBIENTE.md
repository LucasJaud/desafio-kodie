# Decisões do ambiente — Etapa 0

Registro das decisões tomadas na Etapa 0 (inspeção e preparação).
Este documento complementa `07_PLANO_DE_IMPLEMENTACAO.md` e não substitui os
documentos originais de planejamento.

Data da inspeção: 2026-11-25

## 1. Ambiente validado

| Item | Valor |
|---|---|
| Sistema operacional | Linux Mint 22.3 (base Ubuntu 24.04) |
| Python | 3.12.3 (`/usr/bin/python3`) |
| Gerenciador de ambiente | `venv` local em `.venv/` |
| pip | 26.3 (dentro do `.venv`; não há pip global) |
| Git | 2.43.0 |
| Docker | 29.10.1 (daemon ativo) |
| Docker Compose | v5.8.0 |
| Node.js / npm | v24.21.0 / 11.19.0 |
| n8n | não instalado localmente; imagem Docker ainda não baixada |

## 2. Decisões

- **D-01 — Versão do Python:** 3.12.3, única disponível no ambiente.
  A aplicação deve funcionar em Python 3.12.
- **D-02 — Isolamento:** dependências instaladas apenas em `.venv/`
  (versionado no `.gitignore`). Nada é instalado globalmente.
- **D-03 — Dependências:** versões fixadas em `requirements.txt`
  (execução) e `requirements-dev.txt` (testes), conforme política de
  registrar versões do `00_GUIA_DO_AGENTE.md`.
- **D-04 — Limite de entrada:** `TASK_REQUEST_MAX_LENGTH=4000`
  caracteres, conforme sugestão do `04_CONTRATO_DA_API.md`.
- **D-05 — Configuração:** todas as configurações virão de variáveis de
  ambiente, carregadas com `pydantic-settings`. O arquivo `.env` é local e
  ignorado pelo Git; `.env.example` contém apenas placeholders.
- **D-06 — Provedor de IA:** Google Gemini, acessado pelo endpoint
  compatível com OpenAI
  (`https://generativelanguage.googleapis.com/v1beta/openai/`). O código
  usa um cliente genérico compatível com OpenAI, então a troca de provedor
  exige apenas alterar variáveis de ambiente.
- **D-09 — Configuração de IA:** `AI_JSON_MODE` fica `false` no `.env`
  local por segurança de compatibilidade com o endpoint do Google; pode ser
  ativado em provedores que suportam `response_format: json_object`.
  O `.env` local contém valores mock e não é versionado.
- **D-07 — n8n e Docker:** n8n executado via Docker desde a Etapa 4. Na
  Etapa 7 a aplicação foi containerizada e o Docker Compose passou a orquestrar
  API + n8n, mantendo também a execução local da API como alternativa.
- **D-08 — Versionamento:** nenhum commit ou push será feito sem solicitação
  explícita, conforme `00_GUIA_DO_AGENTE.md`.

## 3. Variáveis de ambiente

| Variável | Padrão | Uso |
|---|---|---|
| `APP_NAME` | `task-organizer` | Nome exibido na documentação OpenAPI |
| `LOG_LEVEL` | `INFO` | Nível de log da aplicação |
| `TASK_REQUEST_MAX_LENGTH` | `4000` | Limite de `request_text` |
| `AI_PROVIDER` | — | Identificador do provedor de IA |
| `AI_API_KEY` | — | Credencial do provedor (somente via ambiente) |
| `AI_MODEL` | — | Modelo utilizado na classificação |
| `AI_BASE_URL` | — | Endpoint base do provedor (inclui a versão) |
| `AI_TIMEOUT_SECONDS` | `30` | Timeout das chamadas ao provedor |
| `AI_MAX_TOKENS` | `800` | Limite de tokens da resposta |
| `AI_TEMPERATURE` | `0.0` | Determinismo da classificação |
| `AI_JSON_MODE` | `true` | Envia `response_format: json_object` quando suportado |

## 4. Estrutura inicial criada

```text
app/
├── api/routes/
├── core/
├── schemas/
└── services/
tests/
n8n/
docs/images/
docs/workflow/
.env.example
.gitignore
requirements.txt
requirements-dev.txt
```

Os diretórios vazios contêm `.gitkeep` e serão preenchidos nas etapas
seguintes. Nenhum código de aplicação foi criado nesta etapa.

## 5. Validação executada

- Criação do `.venv` e instalação das dependências: OK.
- Importação de `fastapi`, `pydantic` e `pydantic_settings`: OK.
- `pytest` disponível: OK (sem testes ainda; a suíte inicia na Etapa 1).

## 6. Pendências conhecidas

- Chave real do Google ainda não configurada no `.env` local (valores mock).
- Imagem do n8n ainda não baixada (Etapa 4).
- Branch local `master` duplicada de `main`; remoção pendente de confirmação.
- `jq` não instalado (opcional; inspeção de JSON pode ser feita com Python).

## 7. Atualização — Etapa 2 (integração com IA)

- `app/services/ai_service.py` implementa o cliente compatível com OpenAI,
  com timeout, validação estrita e exceções próprias.
- `app/services/prompt.py` contém a instrução de sistema do
  `05_ESPECIFICACAO_IA_PROMPT.md`.
- `app/services/task_classifier.py` ganhou `AITaskClassifier`; o
  `MockTaskClassifier` permanece apenas para testes e para
  `AI_PROVIDER=mock` explícito.
- `app/api/routes/tasks.py` mapeia falhas: timeout → `504` (`AI_TIMEOUT`),
  resposta inválida → `502` (`AI_INVALID_RESPONSE`) e falha do provedor →
  `502` (`AI_PROVIDER_ERROR`). Não existe fallback silencioso para o mock.
- `.env` local criado com valores mock, ignorado pelo Git.
- Testes: 34 passando, sem chamadas reais ao provedor.

## 8. Atualização — Etapa 4 (n8n)

- n8n **2.49.6** executado em Docker (`docker.n8n.io/n8nio/n8n`), com volume
  nomeado `n8n_data`, porta `5678` e `--add-host=host.docker.internal:host-gateway`.
- Workflow `Organizador de Tarefas` importado de `n8n/workflow.json` e
  publicado via CLI (`import:workflow` + `publish:workflow`).
- Webhook de produção: `POST http://localhost:5678/webhook/task-organizer`.
- A API é chamada em `http://host.docker.internal:8000`; por isso o uvicorn
  precisa escutar em `0.0.0.0` para ser alcançável pelo container.
- Fluxo: Webhook → validação → HTTP Request → verificação de status →
  Switch por prioridade (4 ramos) → Respond to Webhook. Falhas de entrada,
  provedor e conexão possuem ramo de erro com mensagem sanitizada.
- Validação manual: as 4 prioridades percorreram os ramos corretos; `422`
  para entrada inválida; `502` para provedor/API indisponíveis.
- Interface do n8n: `http://localhost:5678` (o primeiro acesso define o
  proprietário local).

Comandos de referência:

```bash
# API acessível pelo container n8n
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000

# n8n
docker start n8n

# Reimportar o workflow, se necessário
docker cp n8n/workflow.json n8n:/tmp/workflow.json
docker exec n8n n8n import:workflow --input=/tmp/workflow.json
docker exec n8n n8n list:workflow
docker exec n8n n8n publish:workflow --id=<id>
```

## 9. Atualização — Etapa 7 (Docker Compose)

- `Dockerfile` baseado em `python:3.12-slim`, com usuário não-root e
  `HEALTHCHECK` em `/health`.
- `.dockerignore` exclui `.venv`, `.env`, testes, documentação e o workflow,
  mantendo a imagem enxuta.
- `docker-compose.yml` com dois serviços:
  - `api`: build local, porta `8000`, healthcheck e `extra_hosts` para
    `host.docker.internal`.
  - `n8n`: imagem fixada em `2.49.6`, porta `5678`, volume `n8n_data`,
    `N8N_SECURE_COOKIE=false` e `API_BASE_URL=http://api:8000`.
- O workflow passou a montar a URL da API com
  `$env.API_BASE_URL`, permitindo o mesmo JSON funcionar no Compose
  (`http://api:8000`) e em execução avulsa
  (`http://host.docker.internal:8000`).
- `depends_on` garante que o n8n só inicia após a API ficar saudável.

Comandos:

```bash
docker compose up -d --build     # configuração do .env (Google)
docker compose down              # encerra os serviços
docker compose logs -f           # acompanha logs
docker compose ps                # status e healthchecks
AI_PROVIDER=mock docker compose up -d   # demonstração sem chave
```

Validação realizada no Compose: API saudável, n8n acessível, as quatro
prioridades percorrendo os ramos corretos, `422` para entrada inválida e
`502` para provedor/API indisponíveis.
