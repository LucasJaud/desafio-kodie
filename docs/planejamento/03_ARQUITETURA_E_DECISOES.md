# Arquitetura e decisões técnicas

## 1. Visão geral
Fluxo de automação:

Solicitante → n8n (Webhook) → API FastAPI → serviço de IA → validação Pydantic → resposta JSON → n8n (Switch/IF) → saída demonstrativa por prioridade.

A chamada pode ser iniciada pelo Webhook do n8n. O n8n recebe a solicitação, chama a API por HTTP Request e utiliza o JSON retornado para encaminhar a tarefa. Essa abordagem demonstra claramente a integração entre automação e API.

Fluxo da interface:

Navegador → página estática servida pela FastAPI → API de tarefas → SQLite local.
Ao criar uma tarefa, a API classifica a mensagem, persiste a mensagem original e
os campos estruturados e inicia o cartão em `todo`.

## 2. Responsabilidades

### FastAPI
- Expor endpoints HTTP.
- Validar a entrada.
- Orquestrar o serviço de classificação.
- Validar e normalizar a resposta da IA.
- Persistir e gerenciar tarefas no SQLite.
- Servir a interface estática do Kanban.
- Retornar códigos HTTP e erros coerentes.

### Serviço de IA
- Montar as instruções e o conteúdo da solicitação.
- Chamar o provedor configurado.
- Aplicar timeout e tratamento de exceções.
- Entregar conteúdo ao validador, sem decidir ações externas.

### n8n
- Receber a solicitação via Webhook.
- Chamar o endpoint da API.
- Verificar o resultado.
- Separar tarefas por prioridade usando nodes condicionais/Switch.
- Apresentar ou registrar a saída de cada ramo para fins de demonstração.
- Tratar falhas com ramo de erro ou resposta adequada.

## 3. Organização sugerida do código
O agente pode ajustar nomes, mas deve preservar a separação de responsabilidades.

```text
task-organizer/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   │       └── tasks.py
│   ├── schemas/
│   │   └── task.py
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── task_classifier.py
│   │   └── task_repository.py
│   ├── static/
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── app.js
│   └── core/
│       └── config.py
├── tests/
│   ├── test_health.py
│   ├── test_tasks.py
│   └── test_ai_service.py
├── n8n/
│   └── workflow.json
├── docs/
│   ├── images/
│   └── workflow/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## 4. Decisões
- Python + FastAPI: stack obrigatória permitida pelo desafio e adequada para API pequena.
- Pydantic: validação de entrada e saída.
- Provedor de IA: configurável; não acoplar regras de negócio a um único fornecedor.
- n8n: ferramenta de automação escolhida.
- SQLite local: persistência sem dependência de serviço externo; o caminho é configurado por `DATABASE_PATH` (Compose usa `/data/tasks.db` no volume `task_data`).
- Interface estática em HTML/CSS/JavaScript, servida pela FastAPI.
- Docker Compose: opcional. Implementar depois que execução local e integração estiverem estáveis.

## 5. Contratos e limites
- A API é responsável por produzir uma tarefa estruturada.
- O n8n não deve reinterpretar o texto original com IA; deve usar os campos validados retornados pela API.
- Prioridade é sugestão automatizada. A equipe pode revisar.
- Nenhum prazo ou responsável deve ser inventado.
- Estado do quadro: `todo`, `in_progress` ou `done`; prioridade continua sendo um atributo separado.
- A extensão não adiciona autenticação ou integrações externas reais.
