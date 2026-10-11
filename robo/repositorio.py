"""
Gravação dos resultados da análise prévia no banco de dados.
Cada função grava a mudança na proposta E o registro no log (R9).
"""

EXECUTADO_POR = "ROBO_ANALISE_PREVIA"


def registrar_log(conexao, proposta_id, etapa, resultado, detalhe=None,
                  executado_por=EXECUTADO_POR):
    """Registra uma etapa executada na tabela de log."""
    conexao.execute(
        """
        INSERT INTO log_etapa (proposta_id, etapa, resultado, detalhe, executado_por)
        VALUES (?, ?, ?, ?, ?)
        """,
        (proposta_id, etapa, resultado, detalhe, executado_por),
    )


def registrar_consulta(conexao, proposta_id, consulta):
    """Grava o resultado da consulta automática de restritivos/SCR."""
    conexao.execute(
        """
        INSERT INTO consulta_credito
            (proposta_id, tem_restritivo, parcelas_mensais_scr, origem, data_consulta)
        VALUES (?, ?, ?, 'AUTOMATICA', datetime('now', 'localtime'))
        """,
        (proposta_id, int(consulta["tem_restritivo"]), consulta["parcelas_mensais_scr"]),
    )
    registrar_log(conexao, proposta_id, "CONSULTA_CREDITO", "OK")


def reprovar(conexao, proposta_id, motivos):
    """Gateway 'Dentro da política?' → Não: reprovação automática."""
    motivo = "; ".join(motivos)
    conexao.execute(
        """
        UPDATE proposta
        SET status = 'REPROVADA', motivo_reprovacao = ?, etapa_atual = 'FINALIZADA'
        WHERE id = ?
        """,
        (motivo, proposta_id),
    )
    registrar_log(conexao, proposta_id, "POLITICA_CREDITO", "FORA", motivo)


def encaminhar_alcada(conexao, proposta_id, alcada):
    """Gateway 'Dentro da política?' → Sim: define a alçada e encaminha."""
    conexao.execute(
        "UPDATE proposta SET alcada = ?, etapa_atual = ? WHERE id = ?",
        (alcada, alcada, proposta_id),
    )
    registrar_log(conexao, proposta_id, "POLITICA_CREDITO", "DENTRO")
    registrar_log(conexao, proposta_id, "DEFINIR_ALCADA", alcada)


def encaminhar_backoffice(conexao, proposta_id, motivo):
    """Evento de erro de borda: a consulta falhou, a proposta vai para o backoffice."""
    conexao.execute(
        "UPDATE proposta SET etapa_atual = 'BACKOFFICE' WHERE id = ?",
        (proposta_id,),
    )
    registrar_log(conexao, proposta_id, "CONSULTA_CREDITO", "FALHA", motivo)


def registrar_decisao(conexao, proposta_id, decisao, parecer, responsavel):
    """Tarefa de usuário 'Analisar e decidir proposta': grava a decisão do gerente."""
    conexao.execute(
        """
        UPDATE proposta
        SET status = ?, etapa_atual = 'FINALIZADA',
            motivo_reprovacao = CASE WHEN ? = 'REPROVADA' THEN ? END
        WHERE id = ?
        """,
        (decisao, decisao, parecer, proposta_id),
    )
    registrar_log(conexao, proposta_id, "DECISAO_GERENTE", decisao, parecer,
                  executado_por=responsavel)


def registrar_notificacao(conexao, proposta_id, destino):
    """Tarefa de envio 'Informar associado do resultado'."""
    registrar_log(conexao, proposta_id, "NOTIFICACAO_ASSOCIADO", "ENVIADA", destino,
                  executado_por="ROBO_NOTIFICACAO")
