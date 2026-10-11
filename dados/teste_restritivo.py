import sqlite3
conexao = sqlite3.connect("dados/credito.db")
conexao.execute("""
INSERT INTO proposta (associado_id, valor, prazo_meses, finalidade, data_solicitacao)
VALUES (2, 2000, 10, 'Teste restritivo', '2026-10-02 09:00')
""")
conexao.commit()