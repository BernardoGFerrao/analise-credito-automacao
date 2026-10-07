SELECT * FROM associado

SELECT * FROM proposta

SELECT * FROM consulta_credito


Select a.nome, p.valor, p.motivo_reprovacao from proposta p join associado a ON a.id = p.associado_id WHERE p.status = 'REPROVADA' ORDER BY p.valor DESC;

SELECT SUM(proposta.valor) as "total_aprovado" from proposta where proposta.status = 'APROVADA';

select a.nome, c.data_consulta
from associado a
JOIN proposta p ON p.associado_id = a.id
JOIN consulta_credito c ON c.proposta_id = p.id
where c.origem = 'MANUAL';

SELECT a.nome, a.situacao
FROM associado a
LEFT JOIN proposta p ON p.associado_id = a.id
WHERE p.id IS NULL;

SELECT COALESCE(alcada, 'SEM ALÇADA (reprovação automática)') AS alcada, -- COALESCE(a, b) significa: "use a; se a for NULL, use b".
       COUNT(*) AS quantidade,
       ROUND(AVG(valor), 2) AS valor_medio
FROM proposta
GROUP BY alcada;

/*
  Indicador: taxa de aprovação
  Considera só propostas já decididas (ignora EM_ANALISE)
*/
SELECT COUNT(*) AS decididas,
       SUM(CASE WHEN status = 'APROVADA' THEN 1 ELSE 0 END) AS aprovadas,
       -- aprovadas ÷ decididas × 100; o 100.0 evita a divisão inteira
       ROUND(SUM(CASE WHEN status = 'APROVADA' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS taxa_aprovacao
FROM proposta
WHERE status <> 'EM_ANALISE';

-- Fila do backoffice: propostas em que a consulta automática falhou, com o motivo
SELECT a.nome, p.valor, l.detalhe AS motivo
FROM proposta p
JOIN associado a ON a.id = p.associado_id
JOIN log_etapa l ON l.proposta_id = p.id
WHERE p.etapa_atual = 'BACKOFFICE'
  AND l.etapa = 'CONSULTA_CREDITO'
  AND l.resultado = 'FALHA';

