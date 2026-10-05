-- Esquema do banco de dados da análise de crédito
CREATE TABLE associado (
    id                    INTEGER PRIMARY KEY,
    cpf                   TEXT    NOT NULL UNIQUE,
    nome                  TEXT    NOT NULL,
    agencia               TEXT    NOT NULL,
    situacao              TEXT    NOT NULL CHECK (situacao IN ('ATIVO', 'INATIVO')),
    renda_mensal          REAL    NOT NULL CHECK (renda_mensal >= 0),
    capital_integralizado REAL    NOT NULL DEFAULT 0,
    data_associacao       TEXT    NOT NULL
);

CREATE TABLE proposta (
    id                INTEGER PRIMARY KEY,
    associado_id      INTEGER NOT NULL REFERENCES associado(id),
    valor             REAL    NOT NULL CHECK (valor > 0),
    prazo_meses       INTEGER NOT NULL CHECK (prazo_meses BETWEEN 1 AND 120),
    finalidade        TEXT,
    data_solicitacao  TEXT    NOT NULL,
    alcada            TEXT    CHECK (alcada IN ('GERENTE', 'COMITE')),
    status            TEXT    NOT NULL DEFAULT 'EM_ANALISE'
                              CHECK (status IN ('EM_ANALISE', 'APROVADA', 'REPROVADA')),
    motivo_reprovacao TEXT
);

CREATE TABLE consulta_credito (
    id                   INTEGER PRIMARY KEY,
    proposta_id          INTEGER NOT NULL REFERENCES proposta(id),
    tem_restritivo       INTEGER NOT NULL CHECK (tem_restritivo IN (0, 1)),
    parcelas_mensais_scr REAL    NOT NULL,
    origem               TEXT    NOT NULL CHECK (origem IN ('AUTOMATICA', 'MANUAL')),
    data_consulta        TEXT    NOT NULL
);