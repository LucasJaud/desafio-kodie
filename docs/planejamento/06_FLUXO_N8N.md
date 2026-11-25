# Especificação do fluxo n8n

## 1. Objetivo
Demonstrar que o n8n recebe uma solicitação, integra-se à API FastAPI e organiza o resultado conforme a prioridade retornada.

## 2. Fluxo proposto
1. **Webhook** — recebe `request_text` por POST.
2. **IF / validação básica** — verifica se o campo existe e não está vazio.
3. **HTTP Request** — chama `POST /api/v1/tasks/organize` da API, que classifica e persiste a solicitação.
4. **Switch** — avalia `priority`.
5. **Ramos de saída** — um ramo para `critica`, `alta`, `media` e `baixa`.
6. **Respond to Webhook** — devolve ao solicitante o resultado organizado, incluindo identificador, estado, prioridade e próximo passo.
7. **Tratamento de erro** — configurar comportamento para falha na chamada HTTP ou entrada inválida.

O desenho exato pode variar conforme a versão do n8n. O agente deve conferir os nodes e opções disponíveis na instalação utilizada.

## 3. Payload de entrada do Webhook
```json
{
  "request_text": "O serviço de autenticação está indisponível para todos os usuários."
}
```

## 4. Chamada HTTP
- Método: `POST`
- URL: endereço da API no ambiente em execução.
- Header: `Content-Type: application/json`
- Body: encaminhar `request_text` recebido pelo Webhook.
- Timeout: definir valor coerente com a latência esperada do provedor.

A URL deve ser configurável para o ambiente. Em Docker Compose, `localhost` dentro do container n8n aponta para o próprio container, não para o container da API. Usar o nome do serviço na rede Compose, quando aplicável.

## 5. Ramificação
O Switch deve comparar o campo `priority` com os valores previstos:
- `critica`
- `alta`
- `media`
- `baixa`

Cada ramo deve produzir uma saída identificável. No MVP, pode ser uma resposta estruturada ou registro de execução demonstrativo; não é necessário conectar a serviços externos reais.

O fluxo n8n não substitui o quadro Kanban: ambos chamam a mesma API e consultam
o registro persistido. A resposta acrescida de `id`, `status`, `request_text`,
`created_at` e `updated_at` deve preservar a ramificação existente por `priority`.

## 6. Evidências obrigatórias
Capturar:
- fluxo completo com todos os nodes;
- execução concluída com sucesso;
- configuração do Webhook;
- configuração do HTTP Request;
- configuração do Switch;
- dados de entrada e saída em etapas relevantes;
- tratamento de erro, se implementado.

## 7. Exportação
Exportar o workflow em JSON e incluir em `n8n/workflow.json`. Antes de entregar, remover credenciais e dados sensíveis da exportação.
