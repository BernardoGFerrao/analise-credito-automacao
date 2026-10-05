"""
Regras de negócio da análise prévia de crédito.
Funções "puras": recebem valores e devolvem um resultado, sem acessar banco nem API.
"""

# Política de crédito (valores fictícios do projeto)
LIMITE_COMPROMETIMENTO_PCT = 30.0   # acima disso, reprova
LIMITE_ALCADA_GERENTE = 10_000.0    # até esse valor, decide o gerente


def calcular_parcela(valor, prazo_meses):
    """Parcela simples (sem juros): valor dividido pelo prazo."""
    if prazo_meses <= 0:
        raise ValueError(f"Prazo inválido: {prazo_meses}")
    return valor / prazo_meses


def calcular_comprometimento(renda_mensal, parcelas_existentes, parcela_nova):
    """Percentual da renda comprometido com parcelas (existentes + nova)."""
    if renda_mensal <= 0:
        raise ValueError(f"Renda inválida: {renda_mensal}")
    return (parcelas_existentes + parcela_nova) / renda_mensal * 100


def avaliar_politica(tem_restritivo, comprometimento_pct):
    """
    Gateway "Dentro da política de crédito?".
    Retorna (dentro_da_politica, lista_de_motivos).
    """
    motivos = []
    if tem_restritivo:
        motivos.append("Restritivo em birô de crédito")
    if comprometimento_pct > LIMITE_COMPROMETIMENTO_PCT:
        motivos.append("Comprometimento de renda acima de 30%")
    return len(motivos) == 0, motivos


def definir_alcada(valor):
    """Tarefa de regra de negócio "Definir alçada"."""
    if valor <= LIMITE_ALCADA_GERENTE:
        return "GERENTE"
    return "COMITE"