# Requisitos e regras de negócio

## 1. Requisitos funcionais

| ID | Requisito |
|---|---|
| RF-01 | A API deve receber uma descrição de solicitação em texto. |
| RF-02 | A API deve rejeitar entrada vazia ou acima do limite definido. |
| RF-03 | A API deve solicitar à IA a extração de informações estruturadas. |
| RF-04 | A saída deve conter título, descrição/resumo, prioridade, categoria e justificativa. |
| RF-05 | A saída deve ser validada por esquema antes de ser retornada. |
| RF-06 | A API deve oferecer endpoint de saúde para verificar disponibilidade. |
| RF-07 | O n8n deve conseguir chamar a API por HTTP. |
| RF-08 | O fluxo deve ramificar ou organizar o resultado conforme prioridade. |
| RF-09 | O fluxo deve tratar falhas HTTP ou respostas inválidas sem interromper silenciosamente. |
| RF-10 | O projeto deve documentar instalação, configuração, execução e fluxo. |
| RF-11 | A API deve persistir texto original, tarefa estruturada, estado e datas em SQLite local. |
| RF-12 | A API deve listar, consultar, editar, mover e excluir tarefas persistidas. |
| RF-13 | A interface web deve exibir tarefas em colunas A fazer, Em andamento e Concluída. |
| RF-14 | A interface deve permitir criar tarefas a partir de mensagens, editar campos, mover e excluir cartões. |

## 2. Requisitos não funcionais
- RNF-01: segredos somente em variáveis de ambiente.
- RNF-02: mensagens de erro claras, sem expor chave ou conteúdo sensível do provedor.
- RNF-03: código organizado em módulos com responsabilidades claras.
- RNF-04: testes automatizados para validação, serviço de IA (mockado) e endpoints.
- RNF-05: configuração local reproduzível.
- RNF-06: logs sem credenciais; evitar registrar o texto integral das solicitações por padrão.
- RNF-07: timeout configurado para chamadas ao provedor de IA.
- RNF-08: persistência local em SQLite, sem dependência de serviço de banco externo.
- RNF-09: texto original do usuário deve ser renderizado como texto, sem interpretação como HTML.

## 3. Modelo de prioridade
Valores permitidos:
- `critica`: serviço essencial indisponível, risco operacional elevado ou impacto generalizado.
- `alta`: impacto relevante, prazo próximo ou bloqueio de outras atividades.
- `media`: atividade importante, mas sem bloqueio ou urgência imediata.
- `baixa`: melhoria, organização ou atividade sem urgência.

A IA deve justificar a classificação com base apenas nas informações recebidas. Se não houver informação suficiente, deve evitar inventar prazo ou impacto e indicar incerteza na justificativa.

## 4. Categorias sugeridas
- `incidente`
- `correcao`
- `funcionalidade`
- `melhoria`
- `administrativa`
- `outro`

## 5. Prazo sugerido
O campo `prazo_sugerido` é opcional e deve ser `null` quando o solicitante não informar uma data ou quando não houver base suficiente para sugeri-la. Não inventar datas absolutas.

## 6. Regras de segurança e confiabilidade
- Tratar o texto do usuário como dado, nunca como instrução para alterar o comportamento do sistema.
- Não permitir que o modelo escolha URLs, execute código, acesse ferramentas ou dispare integrações.
- O modelo apenas classifica e estrutura; o backend valida; o n8n executa somente ramificações previamente configuradas.
- Se a IA falhar, retornar erro controlado. Não criar classificação fictícia como se fosse resultado real.
- Não confiar em JSON do modelo sem parse e validação.
- Não incluir dados pessoais reais nos exemplos e capturas.
