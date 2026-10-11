"""
Robô de análise prévia de crédito.
Executa a raia "Automação" do TO-BE para cada proposta pendente
e grava as decisões e o log no banco.

Uso: python robo/analise_previa.py   (com a API simulada rodando)
Código de saída: 0 = tudo certo; 1 = alguma proposta teve erro inesperado.
"""
import logging
import sqlite3
import sys

from cliente_api import FalhaNaConsulta, consultar_credito
from config_log import configurar_log
from ler_propostas import CAMINHO_BANCO, buscar_propostas_pendentes
from regras import (
    avaliar_politica,
    calcular_comprometimento,
    calcular_parcela,
    definir_alcada,
)
from repositorio import (
    encaminhar_alcada,
    encaminhar_backoffice,
    registrar_consulta,
    registrar_log,
    reprovar,
)

logger = logging.getLogger("robo")


def analisar(conexao, proposta):
    """Aplica as etapas automáticas a uma proposta e grava o resultado."""
    proposta_id = proposta["id"]
    logger.info("Proposta %d: iniciando análise (R$ %.2f)", proposta_id, proposta["valor"])

    # ⚙️ Consultar restritivos/SCR  (FORA da transação: chamada de rede pode demorar)
    try:
        consulta = consultar_credito(proposta["cpf"])
    except FalhaNaConsulta as erro:
        # (⚡) Falha na consulta → backoffice
        with conexao:
            encaminhar_backoffice(conexao, proposta_id, str(erro))
        logger.warning("Proposta %d: %s → BACKOFFICE", proposta_id, erro)
        return

    # 📜 Calcular comprometimento de renda
    parcela = calcular_parcela(proposta["valor"], proposta["prazo_meses"])
    comprometimento = calcular_comprometimento(
        proposta["renda_mensal"], consulta["parcelas_mensais_scr"], parcela
    )
    dentro_da_politica, motivos = avaliar_politica(consulta["tem_restritivo"], comprometimento)

    # Grava tudo de uma vez: ou tudo, ou nada (transação)
    with conexao:
        registrar_consulta(conexao, proposta_id, consulta)
        registrar_log(conexao, proposta_id, "CALCULO_COMPROMETIMENTO", "OK", f"{comprometimento:.1f}%")

        # ◇ Dentro da política de crédito?
        if not dentro_da_politica:
            reprovar(conexao, proposta_id, motivos)
            logger.info("Proposta %d: REPROVADA (%s)", proposta_id, "; ".join(motivos))
            return

        # 📋 Definir alçada
        alcada = definir_alcada(proposta["valor"])
        encaminhar_alcada(conexao, proposta_id, alcada)
        logger.info("Proposta %d: comprometimento %.1f%% → %s", proposta_id, comprometimento, alcada)


def main():
    configurar_log()

    if not CAMINHO_BANCO.exists():
        logger.error("Banco não encontrado: %s", CAMINHO_BANCO)
        return 1

    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")  # o SQLite só valida as FKs se pedirmos

    erros = 0
    try:
        propostas = buscar_propostas_pendentes(conexao)
        logger.info("Início da execução: %d proposta(s) pendente(s)", len(propostas))
        for proposta in propostas:
            try:
                analisar(conexao, proposta)
            except Exception:
                # Erro inesperado: registra com detalhes e segue para a próxima
                erros += 1
                logger.exception("Proposta %d: erro inesperado", proposta["id"])
    finally:
        conexao.close()

    logger.info("Fim da execução: %d proposta(s), %d erro(s)", len(propostas), erros)
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
