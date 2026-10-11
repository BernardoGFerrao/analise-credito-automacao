"""
Lê as decisões preenchidas na planilha do gerente, grava no banco
e notifica o associado.

Uso: python robo/registrar_decisoes.py
"""
import getpass
import logging
import sqlite3
import sys
import time
from pathlib import Path

from openpyxl import load_workbook

from config_log import configurar_log
from exportar_fila import ARQUIVO_FILA
from ler_propostas import CAMINHO_BANCO
from repositorio import registrar_decisao, registrar_notificacao

PASTA_SAIDA = Path(__file__).parent.parent / "caixa_saida"
DECISOES_VALIDAS = {"APROVADA", "REPROVADA"}
TENTATIVAS_LEITURA = 5
ESPERA_LEITURA_SEGUNDOS = 2

logger = logging.getLogger("decisoes")


def ler_decisoes():
    """Lê as linhas da planilha que têm uma decisão preenchida."""
    aba = load_workbook(ARQUIVO_FILA, read_only=True).active
    for proposta_id, associado, _, valor, _, _, decisao, parecer in aba.iter_rows(
        min_row=2, values_only=True
    ):
        if proposta_id is None:
            continue
        yield {
            "proposta_id": proposta_id,
            "associado": associado,
            "valor": valor,
            "decisao": (decisao or "").strip().upper(),
            "parecer": (parecer or "").strip(),
        }


def ler_planilha_com_tentativas():
    """Lê a planilha. Se ela estiver travada (Excel ou OneDrive), espera e tenta de novo."""
    for tentativa in range(1, TENTATIVAS_LEITURA + 1):
        try:
            return list(ler_decisoes())
        except PermissionError:
            if tentativa == TENTATIVAS_LEITURA:
                raise
            logger.warning("Planilha em uso (tentativa %d), aguardando %d s...",
                           tentativa, ESPERA_LEITURA_SEGUNDOS)
            time.sleep(ESPERA_LEITURA_SEGUNDOS)


def ja_processada(conexao, proposta_id):
    """True se a proposta não está mais com o gerente (decisão já registrada antes)."""
    etapa = conexao.execute(
        "SELECT etapa_atual FROM proposta WHERE id = ?", (proposta_id,)
    ).fetchone()
    return etapa is None or etapa[0] != "GERENTE"


def validar(linha):
    """Retorna o motivo pelo qual a linha é inválida, ou None se estiver tudo certo."""
    if linha["decisao"] not in DECISOES_VALIDAS:
        return f"decisão inválida: '{linha['decisao']}'"
    if not linha["parecer"]:
        return "parecer obrigatório"
    return None


def notificar_associado(linha):
    """Simula o envio de um e-mail ao associado gravando a mensagem num arquivo."""
    if linha["decisao"] == "APROVADA":
        resultado = "foi APROVADA. Em breve entraremos em contato para a assinatura do contrato."
    else:
        # Ao associado não vão os detalhes internos da análise
        resultado = "não foi aprovada neste momento. Procure sua agência para mais informações."
    texto = (
        f"Olá, {linha['associado']}.\n\n"
        f"Sua proposta de crédito nº {linha['proposta_id']}, "
        f"no valor de R$ {linha['valor']:.2f}, {resultado}\n"
    )
    PASTA_SAIDA.mkdir(exist_ok=True)
    arquivo = PASTA_SAIDA / f"proposta_{linha['proposta_id']}.txt"
    arquivo.write_text(texto, encoding="utf-8")
    return arquivo.name


def main():
    configurar_log()

    if not ARQUIVO_FILA.exists():
        logger.error("Planilha não encontrada: %s", ARQUIVO_FILA)
        return 1

    responsavel = f"GERENTE:{getpass.getuser()}"
    registradas = invalidas = pendentes = 0

    try:
        linhas = ler_planilha_com_tentativas()
    except PermissionError:
        logger.error("A planilha está aberta no Excel. Feche-a e rode de novo: %s", ARQUIVO_FILA)
        return 1

    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.execute("PRAGMA foreign_keys = ON")
    try:
        for linha in linhas:
            if not linha["decisao"]:
                pendentes += 1
                continue

            if ja_processada(conexao, linha["proposta_id"]):
                logger.info("Proposta %s já processada anteriormente", linha["proposta_id"])
                continue

            motivo = validar(linha)
            if motivo:
                invalidas += 1
                logger.warning("Proposta %s ignorada: %s", linha["proposta_id"], motivo)
                continue

            with conexao:
                registrar_decisao(conexao, linha["proposta_id"], linha["decisao"],
                                  linha["parecer"], responsavel)
                destino = notificar_associado(linha)
                registrar_notificacao(conexao, linha["proposta_id"], destino)
            registradas += 1
            logger.info("Proposta %s: %s por %s", linha["proposta_id"], linha["decisao"], responsavel)
    finally:
        conexao.close()

    resumo = (f"{registradas} decisão(ões) registrada(s), "
              f"{invalidas} inválida(s), {pendentes} pendente(s).")
    logger.info(resumo)
    print(resumo)
    return 1 if invalidas else 0


if __name__ == "__main__":
    sys.exit(main())
