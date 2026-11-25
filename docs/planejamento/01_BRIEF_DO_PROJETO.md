# Brief do projeto — Organizador inteligente de tarefas

## 1. Contexto
Uma equipe recebe solicitações de atividades em linguagem natural. A equipe precisa compreender o que deve ser feito, identificar a urgência e organizar o trabalho. O desafio técnico da KODIE propõe utilizar IA para interpretar solicitações, identificar prioridades e organizar tarefas.

## 2. Problema escolhido
**Caso 4.3 — Organização de Tarefas.**

Desenvolver uma solução que recebe uma solicitação escrita livremente e utiliza IA para transformá-la em uma tarefa estruturada, com prioridade sugerida e informações úteis para organização.

## 3. Objetivo
Reduzir o esforço manual necessário para interpretar e organizar solicitações, demonstrando integração entre:
- uma API própria;
- um modelo de Inteligência Artificial;
- um fluxo de automação no n8n.

## 4. Exemplo de uso
Entrada:
> O sistema de pagamento está apresentando erro para todos os clientes desde hoje cedo. Precisamos verificar isso o quanto antes.

Resultado esperado (ilustrativo):
- título: Investigar erro no sistema de pagamento
- prioridade: alta ou crítica, conforme política de classificação definida
- categoria: incidente
- resumo: falha no pagamento afetando clientes
- justificativa: impacto amplo e serviço essencial indisponível
- próximo passo sugerido: encaminhar para equipe responsável

A IA sugere a classificação; a automação aplica regras fixas e controladas.

## 5. Escopo do MVP
- Receber uma descrição textual de tarefa.
- Validar tamanho e formato da entrada.
- Usar IA para extrair campos estruturados.
- Validar a resposta do modelo.
- Retornar JSON padronizado.
- Disponibilizar endpoint para o n8n.
- Criar fluxo no n8n que chama a API e trata sucesso/erro.
- Demonstrar uma ação de organização, como separar tarefas por prioridade e encaminhar para destinos simulados (por exemplo, saídas/ramificações distintas no fluxo).
- Documentar e testar.

## 6. Fora do escopo
- Aplicativo web completo ou aplicativo móvel.
- Gestão de usuários, login e permissões.
- Banco de dados persistente obrigatório.
- Integração real com Jira, Trello, Slack, e-mail ou outros serviços externos no MVP.
- Planejamento automático de calendário ou atribuição definitiva de responsáveis.
- Execução automática de ações técnicas descritas na solicitação.

## 7. Usuários e cenário
Usuário principal: integrante de uma pequena equipe que envia uma solicitação de atividade.
Beneficiário: pessoa ou equipe que recebe a tarefa já organizada.

## 8. Princípios
- Simplicidade e demonstração ponta a ponta.
- Saída estruturada e validada.
- Prioridade explicável, com justificativa.
- Automação previsível e segura.
- Nenhuma ação externa real sem configuração e autorização explícitas.
