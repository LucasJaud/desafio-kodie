# Contrato da API

Os exemplos definem o contrato da API, incluindo a extensão aprovada de persistência e Kanban.

## 1. `GET /health`
Resposta `200`:
```json
{
  "status": "ok"
}
```

## 2. `POST /api/v1/tasks/organize`
Descrição: recebe uma solicitação em linguagem natural, retorna a tarefa estruturada e a persiste com estado inicial `todo`.

### Requisição
```json
{
  "request_text": "O relatório mensal precisa ser atualizado até sexta-feira."
}
```

### Resposta de sucesso — `200`
```json
{
  "title": "Atualizar relatório mensal",
  "description": "Atualização do relatório mensal solicitada.",
  "priority": "media",
  "category": "administrativa",
  "reason": "A solicitação informa uma entrega com prazo, mas não indica bloqueio ou impacto crítico.",
  "suggested_next_step": "Confirmar os dados necessários e atualizar o relatório.",
  "due_date": null,
  "needs_human_review": false,
  "id": 1,
  "request_text": "O relatório mensal precisa ser atualizado até sexta-feira.",
  "status": "todo",
  "created_at": "2026-11-25T12:00:00+00:00",
  "updated_at": "2026-11-25T12:00:00+00:00"
}
```

`due_date` só pode conter uma data ISO (`YYYY-MM-DD`) se a data estiver explicitamente identificável na solicitação. Caso contrário, `null`.
`request_text` é persistido exatamente como recebido; o texto enviado ao
classificador é normalizado removendo espaços nas extremidades.

## 3. Tarefas persistidas

### `GET /api/v1/tasks`
Lista tarefas em ordem de criação decrescente. Filtros opcionais: `status`
(`todo`, `in_progress`, `done`) e `priority`
(`critica`, `alta`, `media`, `baixa`).

### `GET /api/v1/tasks/{id}`
Retorna uma tarefa persistida ou `404 TASK_NOT_FOUND`.

### `PATCH /api/v1/tasks/{id}`
Atualiza um ou mais campos permitidos:

```json
{
  "title": "Atualizar relatório mensal",
  "description": "Conferir os dados e enviar.",
  "status": "in_progress"
}
```

Campos: `title` (1–200 caracteres), `description` (até 4.000 caracteres) e
`status` (`todo`, `in_progress`, `done`). É obrigatório enviar pelo menos um
campo. Campos não enviados permanecem inalterados. Uma atualização altera
`updated_at`.

### `DELETE /api/v1/tasks/{id}`
Exclui a tarefa e responde `204`; retorna `404 TASK_NOT_FOUND` se ela não existir.

Os registros são armazenados em SQLite no caminho definido por `DATABASE_PATH`.
O estado e a prioridade são atributos distintos; mover de coluna não altera a
prioridade sugerida.

## 4. Erros esperados
- `422`: corpo ausente, campo vazio ou formato inválido.
- `502`: provedor de IA indisponível ou resposta que não pode ser validada.
- `504`: timeout do provedor de IA.
- `500 TASK_STORAGE_ERROR`: falha de persistência, sem detalhes internos na resposta.

Exemplo de erro:
```json
{
  "detail": {
    "code": "AI_PROVIDER_ERROR",
    "message": "Não foi possível organizar a tarefa neste momento."
  }
}
```

## 5. Validação
- `request_text`: string não vazia após trim.
- Definir e documentar limite máximo (sugestão inicial: 4.000 caracteres).
- `title`: string curta e não vazia.
- `description`, `reason`, `suggested_next_step`: strings.
- `priority`: enum `critica | alta | media | baixa`.
- `category`: enum `incidente | correcao | funcionalidade | melhoria | administrativa | outro`.
- `due_date`: data ISO ou `null`.
- `needs_human_review`: boolean.

## 6. Observação
Não retornar texto livre bruto do modelo como contrato da API. O backend deve converter e validar a saída para o esquema acima.
