"""
Robô de análise prévia de crédito.
Parte 1: ler do banco as propostas que aguardam análise.
"""
import sqlite3
from pathlib import Path

# Caminho do banco: sobe da pasta "robo" para a pasta do projeto e entra em "dados"
CAMINHO_BANCO = Path(__file__).parent.parent / "dados" / "credito.db"

# Proposta pendente = em análise e ainda sem consulta de crédito registrada
SQL_PENDENTES = """
    SELECT p.id, a.nome, a.situacao, a.renda_mensal, p.valor, p.prazo_meses, p.valor / p.prazo_meses as 'parcela_simples'
    FROM proposta p
    JOIN associado a             ON a.id = p.associado_id
    LEFT JOIN consulta_credito c ON c.proposta_id = p.id
    WHERE p.status = 'EM_ANALISE'
      AND c.id IS NULL
    ORDER BY p.data_solicitacao
"""


def buscar_propostas_pendentes(conexao):
    """Retorna a lista de propostas que o robô ainda precisa analisar."""
    cursor = conexao.execute(SQL_PENDENTES)
    return cursor.fetchall()


def main():
    # Sem esta checagem, o sqlite3 criaria um banco VAZIO no caminho errado
    if not CAMINHO_BANCO.exists():
        raise SystemExit(f"Banco não encontrado: {CAMINHO_BANCO}")

    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row  # permite acessar colunas pelo nome
    try:
        propostas = buscar_propostas_pendentes(conexao)
    finally:
        conexao.close()  # fecha a conexão mesmo se der erro

    print(f"{len(propostas)} proposta(s) aguardando análise prévia\n")
    for proposta in propostas:
        print(
            f"Proposta {proposta['id']}: {proposta['nome']} "
            f"pediu R$ {proposta['valor']:.2f} em {proposta['prazo_meses']}x"
            f" de R$ {proposta['parcela_simples']:.2f}"
            f". O Associado possui renda mensal de R${proposta['renda_mensal']}"
        )


if __name__ == "__main__":
    main()