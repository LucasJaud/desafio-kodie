# Documentação e checklist de entrega

## 1. Estrutura esperada do repositório
```text
task-organizer/
├── app/
│   ├── api/
│   ├── core/
│   ├── schemas/
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── task_classifier.py
│   │   └── task_repository.py
│   ├── static/
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── app.js
│   └── main.py
├── tests/
├── n8n/
│   └── workflow.json
├── docs/
│   ├── images/
│   │   ├── fluxo-completo.png
│   │   ├── execucao-sucesso.png
│   │   ├── node-webhook.png
│   │   ├── node-http-request.png
│   │   ├── node-switch.png
│   │   └── dados-processados.png
│   └── workflow/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── Dockerfile              # opcional
└── docker-compose.yml      # opcional
```

## 2. Conteúdo mínimo do README
1. Nome e descrição do projeto.
2. Apresentação da ideia.
3. Problema escolhido: organização de tarefas (caso 4.3).
4. Solução proposta.
5. Tecnologias utilizadas.
6. Arquitetura e fluxo de funcionamento.
7. Exemplo de entrada e saída.
8. Pré-requisitos.
9. Configuração das variáveis de ambiente.
10. Como instalar e executar a API.
11. Como importar e executar o workflow n8n.
12. Como executar os testes.
13. Evidências visuais com legendas.
14. Limitações conhecidas.

## 3. Evidências visuais
Cada imagem deve ter uma legenda curta dizendo:
- o que está sendo mostrado;
- qual node/etapa está configurado;
- o que comprova.

Não incluir tokens, chaves, e-mails reais ou dados pessoais.

## 4. Segurança antes do push
- Confirmar `.env` no `.gitignore`.
- Confirmar `.env.example` sem segredos.
- Inspecionar histórico e arquivos em busca de chaves.
- Remover credenciais da exportação n8n.
- Não incluir dados reais de clientes.

## 5. Entrega final
- Código-fonte.
- README.
- Prints do fluxo e da execução.
- JSON exportado do n8n.
- `.env.example`.
- Dockerfile e Compose, se o diferencial opcional for implementado.
- Banco SQLite persistido no volume `task_data` no Docker Compose; não versionar o arquivo local.

O desafio pede o link do repositório GitHub como forma de entrega. A publicação deve ser feita pelo responsável pelo projeto.
