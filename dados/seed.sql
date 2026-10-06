-- Dados FICTÍCIOS para testes (CPFs inválidos de propósito)
INSERT INTO associado (cpf, nome, agencia, situacao, renda_mensal, capital_integralizado, data_associacao) VALUES
('000.000.001-01', 'Maria Souza',    'Pelotas Centro',  'ATIVO',   4500,  1200, '2019-03-10'),
('000.000.002-02', 'João Pereira',   'Pelotas Fragata', 'ATIVO',   3000,   500, '2021-07-22'),
('000.000.003-03', 'Ana Lima',       'Pelotas Centro',  'ATIVO',   8000, 15000, '2015-01-05'),
('000.000.004-04', 'Carlos Silva',   'Capão do Leão',   'INATIVO', 2500,   300, '2018-11-30'),
('000.000.005-05', 'Fernanda Costa', 'Pelotas Fragata', 'ATIVO',   6000,  3000, '2020-05-18'),
('000.000.006-06', 'Ricardo Alves',  'Pelotas Centro',  'ATIVO',  12000, 25000, '2012-09-01'),
('000.000.007-07', 'Paulo Mendes',   'Capão do Leão',   'ATIVO',   2800,   400, '2023-02-14');

INSERT INTO proposta (associado_id, valor, prazo_meses, finalidade, data_solicitacao, alcada, status, motivo_reprovacao, etapa_atual) VALUES
(1,  8000, 24, 'Reforma',             '2026-09-01 09:15', 'GERENTE', 'APROVADA',   NULL,                                    'FINALIZADA'),
(2,  5000, 12, 'Quitação de dívidas', '2026-09-02 10:30', NULL,      'REPROVADA',  'Restritivo em birô de crédito',         'FINALIZADA'),
(3, 30000, 36, 'Veículo',             '2026-09-03 14:00', 'COMITE',  'APROVADA',   NULL,                                    'FINALIZADA'),
(5, 15000, 24, 'Viagem',              '2026-09-05 11:00', 'COMITE',  'REPROVADA',  'Decisão do comitê de crédito',          'FINALIZADA'),
(6,  9000, 12, 'Equipamentos',        '2026-09-08 08:45', 'GERENTE', 'EM_ANALISE', NULL,                                    'GERENTE'),
(7,  6000, 12, 'Reforma',             '2026-09-10 13:20', NULL,      'REPROVADA',  'Comprometimento de renda acima de 30%', 'FINALIZADA');

INSERT INTO consulta_credito (proposta_id, tem_restritivo, parcelas_mensais_scr, origem, data_consulta) VALUES
(1, 0,  600, 'AUTOMATICA', '2026-09-01 09:16'),
(2, 1,  900, 'AUTOMATICA', '2026-09-02 10:31'),
(3, 0, 1200, 'MANUAL',     '2026-09-03 16:40'),
(4, 0,  800, 'AUTOMATICA', '2026-09-05 11:01'),
(5, 0, 1500, 'AUTOMATICA', '2026-09-08 08:46'),
(6, 0,  450, 'AUTOMATICA', '2026-09-10 13:21');

-- Propostas novas, aguardando a análise prévia do robô
INSERT INTO proposta (associado_id, valor, prazo_meses, finalidade, data_solicitacao) VALUES
(1,  3000, 12, 'Celular', '2026-10-01 09:00'),
(3, 25000, 48, 'Reforma', '2026-10-01 10:30'),
(7,  1500,  6, 'Curso',   '2026-10-01 14:10');