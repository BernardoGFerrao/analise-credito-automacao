-- Indicadores do processo de análise prévia de crédito
-- Rode com: python dados/rodar_sql.py

-- E0 (exemplo pronto): volume de propostas por status
SELECT status, COUNT(*) AS qtd
FROM proposta
GROUP BY status
ORDER BY qtd DESC;

-- E1: funil - quantas propostas estão em cada etapa_atual
SELECT etapa_atual, COUNT(*) AS qtd FROM proposta GROUP BY etapa_atual;

-- E2: destino das propostas analisadas pelo robô
SELECT
    SUM(CASE WHEN alcada = 'GERENTE' THEN 1 ELSE 0 END) AS encaminhada_gerente,
    SUM(CASE WHEN alcada = 'COMITE' THEN 1 ELSE 0 END) AS encaminhada_comite,
    SUM(CASE WHEN alcada IS NULL AND etapa_atual <> 'BACKOFFICE' THEN 1 ELSE 0 END) AS automatico,
    SUM(CASE WHEN alcada IS NULL AND etapa_atual = 'BACKOFFICE' THEN 1 ELSE 0 END) AS backoffice

FROM proposta
WHERE id IN ( -- Passo A
            SELECT DISTINCT proposta_id
            FROM log_etapa
            WHERE executado_por = 'ROBO_ANALISE_PREVIA');

-- E3: ranking dos motivos de reprovação
SELECT
    COUNT(*) AS total_reprovadas,
    SUM(CASE WHEN motivo_reprovacao LIKE '%Comprometimento%' THEN 1 ELSE 0 END) AS comprometimento,
    SUM(CASE WHEN motivo_reprovacao LIKE '%Restritivo%'      THEN 1 ELSE 0 END) AS restritivo,
    SUM(CASE WHEN motivo_reprovacao NOT LIKE '%Comprometimento%'
              AND motivo_reprovacao NOT LIKE '%Restritivo%'  THEN 1 ELSE 0 END) AS outros
FROM proposta
WHERE status = 'REPROVADA';

-- E3b: motivos de reprovação só das decisões do robô
SELECT
    COUNT(*) AS total_reprovadas,
    SUM(CASE WHEN motivo_reprovacao LIKE '%Comprometimento%' THEN 1 ELSE 0 END) AS comprometimento,
    SUM(CASE WHEN motivo_reprovacao LIKE '%Restritivo%'      THEN 1 ELSE 0 END) AS restritivo,
    SUM(CASE WHEN motivo_reprovacao NOT LIKE '%Comprometimento%'
              AND motivo_reprovacao NOT LIKE '%Restritivo%'  THEN 1 ELSE 0 END) AS outros
FROM proposta
WHERE status = 'REPROVADA'
  AND alcada IS NULL
  AND id IN (SELECT DISTINCT proposta_id
             FROM log_etapa
             WHERE executado_por = 'ROBO_ANALISE_PREVIA');

-- E4: tempo entre o pedido e a análise do robô
SELECT
    p.id,
    p.data_solicitacao,
    MIN(l.data_hora) AS analisada_em,
    ROUND((julianday(MIN(l.data_hora)) - julianday(p.data_solicitacao)) * 24, 1) AS horas_ate_analise,
    ROUND( julianday(MIN(l.data_hora)) - julianday(p.data_solicitacao), 1)       AS dias_ate_analise
FROM proposta AS p
JOIN log_etapa AS l ON l.proposta_id = p.id
WHERE l.executado_por = 'ROBO_ANALISE_PREVIA'
GROUP BY p.id, p.data_solicitacao
ORDER BY p.id;