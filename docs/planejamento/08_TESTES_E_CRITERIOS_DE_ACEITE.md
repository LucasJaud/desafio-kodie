# Testes e critérios de aceite

## 1. Cenários funcionais
| ID | Entrada/cenário | Resultado esperado |
|---|---|---|
| CT-01 | Solicitação válida de melhoria sem urgência | JSON válido, prioridade baixa ou média justificada |
| CT-02 | Incidente com impacto generalizado explícito | Prioridade alta/crítica conforme regras |
| CT-03 | Atividade com prazo explicitamente informado | Data interpretada apenas se inequívoca |
| CT-04 | Solicitação sem data | `due_date: null` |
| CT-05 | Texto vazio | API retorna 422 |
| CT-06 | Texto acima do limite | API retorna 422 |
| CT-07 | IA retorna categoria/prioridade inválida | API não aceita saída; erro controlado |
| CT-08 | Provedor indisponível | Erro controlado, sem classificação inventada |
| CT-09 | Provedor excede timeout | Resposta de timeout controlada |
| CT-10 | Texto tenta instruir o modelo a ignorar regras | Modelo mantém o formato e as regras de classificação |
| CT-11 | Prioridade `alta` | n8n percorre ramo de alta |
| CT-12 | Prioridade `baixa` | n8n percorre ramo de baixa |

## 2. Critérios de aceite da API
- OpenAPI/Swagger acessível em `/docs` durante desenvolvimento.
- Health check responde corretamente.
- Entrada e saída seguem os schemas.
- Erros possuem status HTTP coerentes.
- Chaves e detalhes internos não aparecem nas respostas.
- Testes automatizados passam.

## 3. Critérios de aceite do n8n
- Webhook recebe payload válido.
- HTTP Request chama a API correta.
- Resultado da API chega ao Switch.
- Cada prioridade possui ramo configurado.
- Resposta final permite entender como a tarefa foi organizada.
- Erros de entrada ou API são visíveis e tratados.
- Workflow JSON exportado sem credenciais.

## 4. Critério ponta a ponta
Uma solicitação enviada ao Webhook deve resultar em uma tarefa estruturada pela API e encaminhada pelo ramo correspondente no n8n.

## 5. Exemplos de dados para demonstração
1. "Adicionar opção de exportar relatório em CSV, sem prazo definido."
2. "O login está indisponível para todos os usuários e impede o acesso ao sistema."
3. "Corrigir erro que impede um usuário de salvar o formulário."
4. "Atualizar a documentação interna quando possível."

Usar apenas dados fictícios nas demonstrações.
