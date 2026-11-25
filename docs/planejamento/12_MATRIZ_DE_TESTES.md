# Matriz de testes — Etapa 3

Rastreabilidade entre os cenários do `08_TESTES_E_CRITERIOS_DE_ACEITE.md`
e os testes automatizados.

## 1. Cenários funcionais

| ID | Cenário | Teste | Status |
|---|---|---|---|
| CT-01 | Melhoria sem urgência | `test_each_priority_is_returned[media/baixa]` | Coberto |
| CT-02 | Incidente com impacto explícito | `test_each_priority_is_returned[alta/critica]` | Coberto |
| CT-03 | Prazo explícito e inequívoco | `test_explicit_due_date_is_returned_as_iso` | Coberto |
| CT-04 | Solicitação sem data | `test_absent_due_date_returns_null` | Coberto |
| CT-05 | Texto vazio | `test_organize_rejects_empty_text` | Coberto |
| CT-06 | Texto acima do limite | `test_organize_rejects_text_above_max_length` | Coberto |
| CT-07 | IA retorna categoria/prioridade inválida | `test_invalid_priority_from_ai_returns_502`, `test_invalid_category_from_ai_returns_502` | Coberto |
| CT-08 | Provedor indisponível | `test_provider_http_error_returns_502`, `test_ai_provider_error_returns_502` | Coberto |
| CT-09 | Provedor excede timeout | `test_provider_timeout_returns_504`, `test_ai_timeout_returns_504` | Coberto |
| CT-10 | Tentativa de prompt injection | `test_prompt_injection_text_is_sent_as_user_data`, `test_user_text_is_sent_as_data_not_system_instruction` | Coberto |
| CT-11 | Prioridade alta percorre ramo de alta no n8n | Webhook com `prioridade alta` | Coberto (Etapa 4) |
| CT-12 | Prioridade baixa percorre ramo de baixa no n8n | Webhook com `prioridade baixa` | Coberto (Etapa 4) |

## 2. Cenários complementares

| Cenário | Teste |
|---|---|
| Cada categoria do contrato | `test_each_category_is_returned` |
| Revisão humana preservada | `test_needs_human_review_is_preserved` |
| JSON inválido da IA | `test_invalid_json_from_ai_returns_502` |
| Campo obrigatório ausente | `test_missing_required_field_from_ai_returns_502` |
| Contrato completo na resposta | `test_success_response_contains_all_contract_fields` |
| Campo desconhecido na entrada | `test_organize_rejects_unknown_field` |
| Texto com espaços nas bordas | `test_organize_strips_request_text` |
| Limite exato de caracteres | `test_organize_accepts_text_at_max_length` |
| Título longo truncado | `test_organize_truncates_long_title` |
| Health check | `test_health_returns_ok` |
| Interface Kanban na raiz | `test_home_serves_kanban_page` |

## 3. Persistência e interface

| Cenário | Teste |
|---|---|
| Solicitação gravada e lida por outra instância do repositório | `test_organized_task_is_persisted_across_repository_instances` |
| Filtros de estado e prioridade | `test_list_tasks_filters_by_status_and_priority` |
| Edição e movimentação | `test_task_can_be_edited_and_moved_between_columns` |
| PATCH sem campos editáveis | `test_patch_requires_at_least_one_editable_field` |
| Exclusão e consulta de item ausente | `test_delete_removes_task_and_unknown_task_returns_404` |

## 4. Testes do fluxo n8n (Etapa 4)

Executados via `POST http://localhost:5678/webhook/task-organizer` com a API
em execução e um provedor de IA simulado local.

| Cenário | Resultado |
|---|---|
| `prioridade critica` | `200`, `branch: critica` |
| `prioridade alta` | `200`, `branch: alta` |
| `prioridade media` | `200`, `branch: media` |
| `prioridade baixa` | `200`, `branch: baixa` |
| corpo `{}` | `422 INVALID_REQUEST` |
| provedor de IA indisponível | `502 AI_PROVIDER_ERROR` |
| API indisponível | `502 API_UNAVAILABLE` (sem vazar stack trace) |

Os mesmos cenários foram revalidados no Docker Compose (serviços `api` e
`n8n`), com a URL da API resolvida por `http://api:8000`. Os exemplos de
requisição/resposta estão em `docs/workflow/exemplos.md`.

## 5. Execução

```bash
.venv/bin/python -m pytest -v
```

Todos os testes automatizados usam `httpx.MockTransport` ou dependências
substituídas. Nenhuma chamada real ao provedor de IA é feita na suíte.
