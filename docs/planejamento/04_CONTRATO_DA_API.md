# Contrato da API

Os exemplos abaixo definem o contrato inicial do MVP. O agente deve mantê-lo estável ou documentar qualquer alteração.

## 1. `GET /health`
Resposta `200`:
```json
{
  "status": "ok"
}
```

## 2. `POST /api/v1/tasks/organize`
Descrição: recebe uma solicitação em linguagem natural e retorna uma tarefa estruturada.

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
  "needs_human_review": false
}
```

`due_date` só pode conter uma data ISO (`YYYY-MM-DD`) se a data estiver explicitamente identificável na solicitação. Caso contrário, `null`.

### Erros esperados
- `422`: corpo ausente, campo vazio ou formato inválido.
- `502`: provedor de IA indisponível ou resposta que não pode ser validada.
- `504`: timeout do provedor de IA.
- `500`: erro interno inesperado, sem detalhes sensíveis na resposta.

Exemplo de erro:
```json
{
  "detail": {
    "code": "AI_PROVIDER_ERROR",
    "message": "Não foi possível organizar a tarefa neste momento."
  }
}
```

## 3. Validação
- `request_text`: string não vazia após trim.
- Definir e documentar limite máximo (sugestão inicial: 4.000 caracteres).
- `title`: string curta e não vazia.
- `description`, `reason`, `suggested_next_step`: strings.
- `priority`: enum `critica | alta | media | baixa`.
- `category`: enum `incidente | correcao | funcionalidade | melhoria | administrativa | outro`.
- `due_date`: data ISO ou `null`.
- `needs_human_review`: boolean.

## 4. Observação
Não retornar texto livre bruto do modelo como contrato da API. O backend deve converter e validar a saída para o esquema acima.
