# Guia do agente de desenvolvimento

## Missão
Implementar o projeto descrito neste conjunto de documentos: uma solução de organização de tarefas que utiliza IA para interpretar solicitações, sugerir prioridade e estruturar tarefas, integrando uma API própria a um fluxo de automação no n8n.

O agente deve trabalhar de forma incremental, preservar decisões documentadas e entregar uma aplicação funcional, testável e documentada.

## Ordem de leitura
1. `01_BRIEF_DO_PROJETO.md`
2. `02_REQUISITOS_E_REGRAS.md`
3. `03_ARQUITETURA_E_DECISOES.md`
4. `04_CONTRATO_DA_API.md`
5. `05_ESPECIFICACAO_IA_PROMPT.md`
6. `06_FLUXO_N8N.md`
7. `07_PLANO_DE_IMPLEMENTACAO.md`
8. `08_TESTES_E_CRITERIOS_DE_ACEITE.md`
9. `09_DOCUMENTACAO_E_ENTREGA.md`

## Regras de trabalho
- Antes de alterar arquivos, inspecione o repositório e identifique o que já existe.
- Não presuma que arquivos, comandos, dependências ou serviços existem: verifique.
- Siga os documentos. Se encontrar conflito ou lacuna que afete arquitetura, segurança ou contrato, registre a dúvida e proponha a menor decisão coerente; não invente requisitos silenciosamente.
- Implemente uma etapa por vez. Ao terminar cada etapa, execute os testes aplicáveis e informe arquivos alterados, comandos executados e resultados.
- Não avance com testes falhando sem explicar a causa e registrar o bloqueio.
- Não implemente frontend completo: o desafio não exige interface visual.
- Não adicione banco de dados, autenticação, filas ou serviços externos sem necessidade demonstrada.
- Não coloque chaves, tokens, senhas ou dados pessoais nos arquivos versionados, logs, testes ou documentação.
- Use variáveis de ambiente. Mantenha `.env.example` apenas com nomes e valores fictícios/seguros.
- Valide todos os dados recebidos da IA como entrada não confiável. Não execute comandos ou ações arbitrárias sugeridas pelo modelo.
- A prioridade sugerida pela IA deve ser tratada como classificação assistiva, não como decisão infalível. Inclua fallback para resposta inválida ou indisponibilidade do provedor.
- Prefira dependências estáveis e simples. Registre versões e justifique dependências relevantes.
- Não faça commits nem publique o repositório sem solicitação explícita.

## Stack definida
- Python
- FastAPI
- Pydantic para validação e modelos
- API de modelo de IA configurável por variável de ambiente
- n8n para automação
- Docker Compose como diferencial opcional, sem torná-lo pré-requisito para execução local

## Definição de pronto
O projeto só está pronto quando:
1. A API recebe uma solicitação de tarefa e valida os dados.
2. A IA produz uma estrutura de tarefa com título, descrição, prioridade, categoria, justificativa e prazo sugerido opcional.
3. A API valida e normaliza a resposta antes de devolvê-la.
4. O n8n chama a API e executa um encaminhamento/registro demonstrável.
5. Há testes automatizados dos cenários principais e de falha.
6. README, `.env.example`, exportação JSON do n8n e evidências visuais estão preparados.
