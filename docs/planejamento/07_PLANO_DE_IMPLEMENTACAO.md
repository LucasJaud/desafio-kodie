# Plano de implementação por etapas

## Etapa 0 — Inspeção e preparação
- Inspecionar repositório, ambiente Python e versões disponíveis.
- Criar estrutura inicial e `.gitignore`.
- Definir versão de Python suportada.
- Criar `.env.example`.
**Saída:** estrutura mínima pronta e decisões registradas.

## Etapa 1 — API sem IA
- Criar aplicação FastAPI.
- Criar `GET /health`.
- Criar schemas Pydantic de entrada e saída.
- Criar `POST /api/v1/tasks/organize` inicialmente com serviço substituível/mockado.
- Implementar validações e erros.
- Testar endpoints.
**Saída:** API executável e contrato validado sem depender do provedor.

## Etapa 2 — Integração com IA
- Escolher/configurar um provedor de IA com API.
- Criar serviço isolado para chamada ao provedor.
- Configurar chave, modelo e timeout por ambiente.
- Implementar prompt conforme `05_ESPECIFICACAO_IA_PROMPT.md`.
- Fazer parse e validação estrita da saída.
- Tratar timeout, indisponibilidade e JSON inválido.
- Criar testes com respostas simuladas; não exigir chamada paga nos testes unitários.
**Saída:** API classifica tarefas com IA e trata falhas.

## Etapa 3 — Testes funcionais da API
- Testar entrada válida e inválida.
- Testar cada prioridade.
- Testar categoria inválida.
- Testar data ausente e data explícita.
- Testar resposta inválida do modelo.
- Testar timeout/erro do provedor.
**Saída:** testes automatizados passando.

## Etapa 4 — Automação n8n
- Subir/configurar n8n.
- Criar Webhook.
- Validar payload.
- Configurar HTTP Request para a API.
- Configurar Switch por prioridade.
- Configurar resposta ao Webhook.
- Implementar tratamento de erro.
**Saída:** fluxo executável ponta a ponta.

## Etapa 5 — Integração e demonstração
- Executar cenários de prioridade crítica, alta, média e baixa.
- Verificar que cada cenário percorre o ramo esperado.
- Testar entrada inválida e API indisponível.
- Salvar exemplos de requisição/resposta sem dados pessoais.
**Saída:** demonstração reproduzível.

## Etapa 6 — Documentação e entrega
- Escrever README com ideia, problema, solução, tecnologias, funcionamento e execução.
- Adicionar prints exigidos do n8n com legendas.
- Exportar workflow JSON.
- Revisar `.env.example` e `.gitignore`.
- Verificar que não há chaves ou credenciais no Git.
- Publicar no GitHub somente após autorização do usuário.
**Saída:** repositório pronto para avaliação.

## Etapa 7 — Diferencial opcional: Docker
Somente após as etapas anteriores:
- Criar Dockerfile da API.
- Criar Docker Compose com API e n8n.
- Configurar rede e variáveis de ambiente.
- Documentar execução.
- Revalidar o fluxo usando nomes de serviço na rede Docker.
**Saída:** execução reproduzível em containers.

## Política de avanço
Ao concluir cada etapa, apresentar:
- resumo do que foi implementado;
- arquivos criados/alterados;
- comandos de execução;
- testes executados e resultados;
- pendências e riscos;
- confirmação antes de mudanças que alterem decisões de arquitetura ou impliquem custos/serviços externos.
