"""
Robô de análise prévia de crédito.
Parte 3: executa a raia "Automação" do TO-BE para cada proposta pendente
(ainda SEM gravar no banco: isso vem na Parte 4).

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


def analisar(proposta):
    """Aplica as etapas automáticas a uma proposta e mostra a decisão."""
    print(f"\nProposta {proposta['id']} - {proposta['nome']} (R$ {proposta['valor']:.2f})")

    # ⚙️ Consultar restritivos/SCR  +  (⚡) Falha na consulta
    try:
        consulta = consultar_credito(proposta["cpf"])
    except FalhaNaConsulta as erro:
        print(f"  ⚡ {erro} → encaminhada ao BACKOFFICE")
        return

    # 📜 Calcular comprometimento de renda
    parcela = calcular_parcela(proposta["valor"], proposta["prazo_meses"])
    comprometimento = calcular_comprometimento(
        proposta["renda_mensal"], consulta["parcelas_mensais_scr"], parcela
    )
    print(f"  Comprometimento: {comprometimento:.1f}%")

    # ◇ Dentro da política de crédito?
    dentro_da_politica, motivos = avaliar_politica(consulta["tem_restritivo"], comprometimento)
    if not dentro_da_politica:
        print(f"  ✖ REPROVADA automaticamente: {'; '.join(motivos)}")
        return

    # 📋 Definir alçada
    print(f"  ✔ Dentro da política → alçada: {definir_alcada(proposta['valor'])}")


def main():
    if not CAMINHO_BANCO.exists():
        raise SystemExit(f"Banco não encontrado: {CAMINHO_BANCO}")

    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    try:
        propostas = buscar_propostas_pendentes(conexao)
    finally:
        conexao.close()

    print(f"{len(propostas)} proposta(s) para analisar")
    for proposta in propostas:
        analisar(proposta)


if __name__ == "__main__":
    main()