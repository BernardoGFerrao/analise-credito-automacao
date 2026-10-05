"""Testes das regras de negócio. Rode com: python robo/test_regras.py"""
from regras import (
    avaliar_politica,
    calcular_comprometimento,
    calcular_parcela,
    definir_alcada,
)

# --- Parcela ---
assert calcular_parcela(6000, 12) == 500

# --- Comprometimento: o caso do Paulo (Aula 3) ---
comprometimento = calcular_comprometimento(2800, 450, 500)
assert round(comprometimento, 1) == 33.9

# --- Política ---
assert avaliar_politica(True, 50) == (
    False,
    ["Restritivo em birô de crédito", "Comprometimento de renda acima de 30%"],
)
assert avaliar_politica(False, 20) == (True, [])

# --- Alçada ---
assert definir_alcada(8000) == "GERENTE"
assert definir_alcada(30000) == "COMITE"

# --- Entradas inválidas devem gerar erro ---
try:
    calcular_comprometimento(0, 0, 500)
    raise AssertionError("Deveria ter recusado renda zero")
except ValueError:
    pass

print("Todos os testes passaram!")