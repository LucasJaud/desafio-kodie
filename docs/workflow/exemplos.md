# Exemplos de integração — Etapa 5

Exemplos de requisição e resposta do fluxo completo, capturados no ambiente
Docker Compose com **provedor de IA simulado**. Todos os dados são fictícios
e não contêm informações pessoais.

- Webhook: `POST http://localhost:5678/webhook/task-organizer`
- API: `POST http://localhost:8000/api/v1/tasks/organize`
- O campo `branch` é acrescentado pelo n8n após o Switch de prioridade;
  ele não faz parte do contrato da API.
- A resposta da API também inclui os campos persistidos `id`, `request_text`,
  `status`, `created_at` e `updated_at`.

## 1. Prioridade crítica

Requisição:

```json
{ "request_text": "prioridade critica" }
```

Resposta (`200`):

```json
{
  "title": "Tarefa simulada",
  "description": "prioridade critica",
  "priority": "critica",
  "category": "incidente",
  "reason": "Resposta simulada para teste do fluxo n8n.",
  "suggested_next_step": "Encaminhar conforme a prioridade.",
  "due_date": null,
  "needs_human_review": false,
  "id": 1,
  "request_text": "prioridade critica",
  "status": "todo",
  "created_at": "2026-11-25T12:00:00+00:00",
  "updated_at": "2026-11-25T12:00:00+00:00",
  "branch": "critica"
}
```

## 2. Prioridade alta

Requisição:

```json
{ "request_text": "prioridade alta" }
```

Resposta (`200`):

```json
{
  "title": "Tarefa simulada",
  "description": "prioridade alta",
  "priority": "alta",
  "category": "incidente",
  "reason": "Resposta simulada para teste do fluxo n8n.",
  "suggested_next_step": "Encaminhar conforme a prioridade.",
  "due_date": null,
  "needs_human_review": false,
  "id": 2,
  "request_text": "prioridade alta",
  "status": "todo",
  "created_at": "2026-11-25T12:00:00+00:00",
  "updated_at": "2026-11-25T12:00:00+00:00",
  "branch": "alta"
}
```

## 3. Prioridade média

Requisição:

```json
{ "request_text": "prioridade media" }
```

Resposta (`200`):

```json
{
  "title": "Tarefa simulada",
  "description": "prioridade media",
  "priority": "media",
  "category": "administrativa",
  "reason": "Resposta simulada para teste do fluxo n8n.",
  "suggested_next_step": "Encaminhar conforme a prioridade.",
  "due_date": null,
  "needs_human_review": false,
  "id": 3,
  "request_text": "prioridade media",
  "status": "todo",
  "created_at": "2026-11-25T12:00:00+00:00",
  "updated_at": "2026-11-25T12:00:00+00:00",
  "branch": "media"
}
```

## 4. Prioridade baixa

Requisição:

```json
{ "request_text": "prioridade baixa" }
```

Resposta (`200`):

```json
{
  "title": "Tarefa simulada",
  "description": "prioridade baixa",
  "priority": "baixa",
  "category": "melhoria",
  "reason": "Resposta simulada para teste do fluxo n8n.",
  "suggested_next_step": "Encaminhar conforme a prioridade.",
  "due_date": null,
  "needs_human_review": false,
  "id": 4,
  "request_text": "prioridade baixa",
  "status": "todo",
  "created_at": "2026-11-25T12:00:00+00:00",
  "updated_at": "2026-11-25T12:00:00+00:00",
  "branch": "baixa"
}
```

## 5. Entrada inválida

Requisição:

```json
{}
```

Resposta (`422`):

```json
{
  "detail": {
    "code": "INVALID_REQUEST",
    "message": "request_text é obrigatório."
  }
}
```

## 6. Provedor de IA indisponível

Resposta (`502`):

```json
{
  "error": true,
  "statusCode": 502,
  "detail": {
    "code": "AI_PROVIDER_ERROR",
    "message": "Não foi possível organizar a tarefa neste momento."
  }
}
```

## 7. API indisponível

Resposta (`502`):

```json
{
  "error": true,
  "statusCode": 502,
  "detail": {
    "code": "API_UNAVAILABLE",
    "message": "Não foi possível contatar a API."
  }
}
```

## Como reproduzir

Com o Docker Compose em execução:

```bash
curl -X POST http://localhost:5678/webhook/task-organizer \
  -H 'Content-Type: application/json' \
  -d '{"request_text":"prioridade alta"}'
```

Para reproduzir sem chave de IA, suba a API com `AI_PROVIDER=mock`:

```bash
AI_PROVIDER=mock docker compose up -d
```

Nesse modo todas as solicitações retornam `priority: media` e
`needs_human_review: true`. Para a demonstração real, configure
`AI_API_KEY` no `.env` e execute `docker compose up -d` sem o override.
