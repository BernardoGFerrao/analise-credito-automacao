"""
Robô de análise prévia de crédito.
Executa a raia "Automação" do TO-BE para cada proposta pendente
e grava as decisões e o log no banco.

Uso: python robo/analise_previa.py   (com a API simulada rodando)
"""
import sqlite3

from cliente_api import FalhaNaConsulta, consultar_credito
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


def analisar(conexao, proposta):
    """Aplica as etapas automáticas a uma proposta e grava o resultado."""
    proposta_id = proposta["id"]
    print(f"\nProposta {proposta_id} - {proposta['nome']} (R$ {proposta['valor']:.2f})")

    # ⚙️ Consultar restritivos/SCR  (FORA da transação: chamada de rede pode demorar)
    try:
        consulta = consultar_credito(proposta["cpf"])
    except FalhaNaConsulta as erro:
        # (⚡) Falha na consulta → backoffice
        with conexao:
            encaminhar_backoffice(conexao, proposta_id, str(erro))
        print(f"  ⚡ {erro} → encaminhada ao BACKOFFICE")
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
            print(f"  ✖ REPROVADA automaticamente: {'; '.join(motivos)}")
            return

        # 📋 Definir alçada
        alcada = definir_alcada(proposta["valor"])
        encaminhar_alcada(conexao, proposta_id, alcada)
        print(f"  ✔ Comprometimento {comprometimento:.1f}% → encaminhada para {alcada}")


def main():
    if not CAMINHO_BANCO.exists():
        raise SystemExit(f"Banco não encontrado: {CAMINHO_BANCO}")

    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")  # o SQLite só valida as FKs se pedirmos
    try:
        propostas = buscar_propostas_pendentes(conexao)
        print(f"{len(propostas)} proposta(s) para analisar")
        for proposta in propostas:
            analisar(conexao, proposta)
    finally:
        conexao.close()


if __name__ == "__main__":
    main()