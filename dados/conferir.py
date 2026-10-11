"""
Mostra o estado do banco para conferir os casos de teste, sem precisar do DB Browser.

Uso:
    python dados/conferir.py              mostra Q1, Q2 e Q3 na tela
    python dados/conferir.py ct01         mostra e também salva em docs/evidencias/ct01.txt
"""
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

PASTA = Path(__file__).parent
CAMINHO_BANCO = PASTA / "credito.db"
PASTA_EVIDENCIAS = PASTA.parent / "docs" / "evidencias"

CONSULTAS = {
    "Q1 - Onde está cada proposta": """
        SELECT p.id, a.nome, p.valor, p.status, p.etapa_atual, p.alcada, p.motivo_reprovacao
        FROM proposta p
        JOIN associado a ON a.id = p.associado_id
        WHERE p.id >= 5
        ORDER BY p.id
    """,
    "Q2 - O que aconteceu, passo a passo": """
        SELECT proposta_id, etapa, resultado, detalhe, executado_por
        FROM log_etapa ORDER BY id
    """,
    "Q3 - Quantas consultas de crédito existem (o seed tem 6)": """
        SELECT COUNT(*) AS total FROM consulta_credito
    """,
}


def formatar_tabela(colunas, linhas):
    """Monta uma tabela de texto com as colunas alinhadas."""
    textos = [[("" if v is None else str(v)) for v in linha] for linha in linhas]
    larguras = [max([len(c)] + [len(l[i]) for l in textos]) for i, c in enumerate(colunas)]
    separador = "-+-".join("-" * w for w in larguras)
    saida = [" | ".join(c.ljust(w) for c, w in zip(colunas, larguras)), separador]
    saida += [" | ".join(v.ljust(w) for v, w in zip(l, larguras)) for l in textos]
    if not linhas:
        saida.append("(nenhuma linha)")
    return "\n".join(saida)


def main():
    if not CAMINHO_BANCO.exists():
        raise SystemExit(f"Banco não encontrado: {CAMINHO_BANCO}")

    # Abre em modo somente leitura: a conferência nunca altera o banco
    conexao = sqlite3.connect(f"file:{CAMINHO_BANCO}?mode=ro", uri=True)
    try:
        partes = [f"Conferência em {datetime.now():%Y-%m-%d %H:%M:%S}"]
        for titulo, sql in CONSULTAS.items():
            cursor = conexao.execute(sql)
            colunas = [d[0] for d in cursor.description]
            partes.append(f"\n== {titulo} ==\n{formatar_tabela(colunas, cursor.fetchall())}")
    finally:
        conexao.close()

    relatorio = "\n".join(partes)
    print(relatorio)

    if len(sys.argv) > 1:
        PASTA_EVIDENCIAS.mkdir(parents=True, exist_ok=True)
        arquivo = PASTA_EVIDENCIAS / f"{sys.argv[1]}.txt"
        arquivo.write_text(relatorio + "\n", encoding="utf-8")
        print(f"\nEvidência salva em: {arquivo}")


if __name__ == "__main__":
    main()
