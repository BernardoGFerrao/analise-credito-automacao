"""
Cria (ou recria) o banco de dados do projeto a partir dos scripts SQL.
Uso: python dados/criar_banco.py
"""
import sqlite3
from pathlib import Path

PASTA = Path(__file__).parent
CAMINHO_BANCO = PASTA / "credito.db"


def main():
    if CAMINHO_BANCO.exists():
        CAMINHO_BANCO.unlink()  # apaga o banco antigo para começar do zero

    conexao = sqlite3.connect(CAMINHO_BANCO)
    try:
        conexao.executescript((PASTA / "schema.sql").read_text(encoding="utf-8"))
        conexao.executescript((PASTA / "seed.sql").read_text(encoding="utf-8"))
        conexao.commit()
    finally:
        conexao.close()

    print(f"Banco criado em: {CAMINHO_BANCO}")


if __name__ == "__main__":
    main()