"""Executa as consultas de um arquivo .sql no banco, somente leitura, e mostra o resultado.

Uso:
    python dados/rodar_sql.py                      (roda dados/indicadores.sql)
    python dados/rodar_sql.py dados/consultas.sql  (roda outro arquivo)

O título de cada consulta é o primeiro comentário "-- " antes dela.
"""
import sqlite3
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
BANCO = PASTA / "credito.db"
PADRAO = PASTA / "indicadores.sql"


def separar_consultas(texto):
    """Devolve (título, sql) para cada comando completo do arquivo."""
    buffer = ""
    for linha in texto.splitlines(keepends=True):
        buffer += linha
        if sqlite3.complete_statement(buffer):
            yield extrair_titulo(buffer), buffer.strip()
            buffer = ""


def extrair_titulo(bloco):
    """Primeiro comentário do parágrafo logo acima do SQL (ignora o cabeçalho do arquivo)."""
    paragrafo = []
    for linha in bloco.splitlines():
        texto = linha.strip()
        if not texto:
            paragrafo = []
        elif texto.startswith("--"):
            paragrafo.append(texto[2:].strip())
        else:
            break
    return paragrafo[0] if paragrafo else "(sem título)"


def imprimir_tabela(colunas, linhas):
    valores = [["" if v is None else str(v) for v in linha] for linha in linhas]
    larguras = [max(len(c), *(len(l[i]) for l in valores)) if valores else len(c)
                for i, c in enumerate(colunas)]
    print(" | ".join(c.ljust(w) for c, w in zip(colunas, larguras)))
    print("-+-".join("-" * w for w in larguras))
    for linha in valores:
        print(" | ".join(v.ljust(w) for v, w in zip(linha, larguras)))
    if not valores:
        print("(nenhuma linha)")


def main():
    arquivo = Path(sys.argv[1]) if len(sys.argv) > 1 else PADRAO
    if not BANCO.exists():
        print(f"Banco não encontrado: {BANCO}. Rode antes: python dados/criar_banco.py")
        return 1

    conexao = sqlite3.connect(f"file:{BANCO.as_posix()}?mode=ro", uri=True)
    erros = 0
    for titulo, sql in separar_consultas(arquivo.read_text(encoding="utf-8")):
        print(f"\n=== {titulo} ===")
        try:
            cursor = conexao.execute(sql)
            colunas = [d[0] for d in cursor.description or []]
            imprimir_tabela(colunas, cursor.fetchall())
        except sqlite3.Error as erro:
            erros += 1
            print(f"ERRO no SQL: {erro}")
    conexao.close()
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
