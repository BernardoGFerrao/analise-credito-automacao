# Plano de testes: análise prévia de crédito

Homologação do processo TO-BE (robô de análise prévia + fila do gerente), executada em **11/10/2026**.
Todos os dados são fictícios. As evidências estão em [`docs/evidencias/`](evidencias/). Caminhos locais e o usuário do Windows foram substituídos por `<pasta_projeto>` e `usuario` antes da publicação.

## Como os testes foram executados

- **Estado inicial:** cada caso parte de um banco recriado (`python dados/criar_banco.py`), exceto quando a pré-condição diz o contrário.
- **API simulada:** a taxa de falha é controlada pela variável `TAXA_FALHA` (0, 0.5 ou 1).
- **Conferência:** `python dados/conferir.py <caso>` abre o banco **somente leitura** e mostra três consultas:
  - **Q1 (estado):** como cada proposta ficou (status, etapa, alçada, motivo).
  - **Q2 (histórico):** o que aconteceu, passo a passo, em `log_etapa`.
  - **Q3 (efeitos colaterais):** quantas consultas de crédito foram gravadas.

## Rastreabilidade: requisito × caso de teste

| Requisito | Casos | Cobertura |
|---|---|---|
| R1 · Formulário digital | — | Não coberto |
| R2 · Documentos obrigatórios | — | Não coberto |
| R3 · Análise automática | CT-01 | Parcial |
| R4 · Reprovação automática | CT-03, CT-04 | Total |
| R5 · Alçadas | CT-01, CT-02, CT-10 | Parcial |
| R6 · SLA | — | Não coberto |
| R7 · Falha → backoffice | CT-05, CT-06, CT-07 | Parcial |
| R8 · Notificação | CT-10, CT-14 | Parcial |
| R9 · Rastreabilidade | CT-01, CT-03 a CT-05, CT-08 a CT-13, CT-15 | Total |

## Casos de teste

| Caso | Cenário | Req. | Resultado esperado | Obtido | Evidência |
|---|---|---|---|---|---|
| CT-01 | Proposta dentro da política, até R$ 10 mil | R3, R5, R9 | Maria (R$ 3.000): 18,9% → GERENTE; 9 consultas no total | ✅ Passou | `ct01.txt` |
| CT-02 | Proposta acima de R$ 10 mil | R5 | Ana (R$ 25.000): 21,5% → COMITE | ✅ Passou | `ct01.txt` (mesma execução do CT-01) |
| CT-03 | Comprometimento acima de 30% | R4, R9 | Paulo (R$ 1.500): 41,1% → REPROVADA, sem etapa de alçada | ✅ Passou | `ct01.txt` (mesma execução do CT-01) |
| CT-04 | Restritivo em birô | R4, R9 | João: REPROVADA com **os dois** motivos (restritivo + 36,7%) | ✅ Passou | `ct04.txt` |
| CT-05 | Serviço responde 503 | R7, R9 | 3 tentativas → BACKOFFICE; nenhuma consulta nova; código de saída 0 | ✅ Passou | `ct05.txt` |
| CT-06 | API desligada | R7 | `ConnectionError` no log → BACKOFFICE | ✅ Passou | `ct06.txt`, `ct06_log.txt` |
| CT-07 | Falha temporária recuperada | R7 | 503 na 1ª tentativa, sucesso na seguinte, sem BACKOFFICE | ✅ Passou (1ª rodada, propostas 7 e 9) | `ct07_log.txt` |
| CT-08 | Robô rodado de novo sem propostas novas | R9 | "0 proposta(s) pendente(s)"; nada novo no banco | ✅ Passou | `ct08.png` |
| CT-09 | Erro inesperado numa proposta | R9 | Proposta 7 desfeita (rollback) e mantida em ANALISE_PREVIA; 8 e 9 processadas; código 1 | ✅ Passou | `ct09.txt`, `ct09_log.txt` |
| CT-10 | Gerente aprova e reprova pela fila | R5, R8, R9 | 5 APROVADA, 7 REPROVADA; responsável `GERENTE:<usuário>`; notificações geradas | ✅ Passou | `ct10.txt`, `ct10.png` |
| CT-11 | Parecer em branco | R9 | Proposta 7 ignorada ("parecer obrigatório") e mantida em GERENTE | ✅ Passou | `ct11.png` |
| CT-12 | Decisão fora da lista no Excel | R9 | Excel recusa "TALVEZ" com mensagem de erro | ✅ Passou | `ct12.png`, `ct12.txt` |
| CT-13 | Decisões registradas duas vezes | R9 | "já processada anteriormente"; nenhum log novo | ✅ Passou | `ct13.txt` |
| CT-14 | Conteúdo das notificações | R8 | Aprovação traz o próximo passo; reprovação não expõe o motivo e orienta procurar a agência | ✅ Passou | `ct14_notificacoes.txt` |
| CT-15 | Robô termina com erro e o PAD alerta | R9 | PAD mostra ALERTA com código 1 e o trecho do log, com acentos corretos | ✅ Passou | `ct15.png` |

**Resumo:** 15 casos executados, 15 passaram, 0 falharam.

## Observações da execução

- **CT-05 × CT-06:** o destino é o mesmo (BACKOFFICE), mas a causa é diferente. Um 503 indica que o serviço está no ar e com problema interno, então o time da API deve ser acionado. Um `ConnectionError` indica que o serviço nem está acessível, então primeiro se verifica se ele está rodando e se a URL/porta estão corretas. O log registra a causa exata para orientar o suporte.
- **CT-07:** o retry evita trabalho manual desnecessário. Com 50% de falha, sem novas tentativas cerca de metade das propostas iria para o backoffice.
- **CT-12:** a validação existe em duas camadas. O Excel recusa o valor e o `registrar_decisoes.py` valida de novo antes de gravar.
- **CT-14:** a reprovação não informa o motivo por sigilo. O motivo envolve dados sensíveis (SCR, birô), e um texto enviado por e-mail pode vazar. A conversa sobre o motivo acontece na agência (LGPD).

## Limitações conhecidas

**Requisitos sem caso de teste**
- **R1 e R2:** o formulário de pedido e o envio de documentos são simulados. As propostas já entram prontas pelo `seed.sql`.
- **R6:** não há controle de prazo (SLA) para o gerente ou o comitê responderem.

**Requisitos parcialmente atendidos**
- **R3:** o robô não verifica a **situação do associado**. Um associado INATIVO seria analisado normalmente.
- **R5:** o comitê não foi implementado. Propostas acima de R$ 10 mil ficam paradas na etapa COMITE.
- **R7:** as propostas chegam ao BACKOFFICE, mas não há fila nem ferramenta para a consulta manual e a devolução ao fluxo.
- **R8:** só as decisões do gerente geram notificação. Reprovações automáticas do robô (ex.: Paulo) e decisões do comitê não avisam o associado.

**Lacuna mais grave para produção**
A falta de notificação nas reprovações automáticas (R8) e a ausência do comitê (R5). No primeiro caso, o associado nunca recebe retorno. No segundo, toda proposta acima de R$ 10 mil fica sem dono. No mundo real, a falta de coleta de documentos (R2) também seria um bloqueio.
