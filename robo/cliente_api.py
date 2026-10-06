"""
Cliente da API de consulta de crédito.
Tarefa de serviço "Consultar restritivos/SCR" + evento de erro de borda.
"""
import time

import requests

URL_API = "http://127.0.0.1:5050/consultas"
TENTATIVAS = 3
ESPERA_SEGUNDOS = 1
TIMEOUT_SEGUNDOS = 5


class FalhaNaConsulta(Exception):
    """A consulta não pôde ser concluída: a proposta vai para o backoffice."""


def consultar_credito(cpf):
    """Consulta restritivos e SCR. Tenta de novo em falhas temporárias."""
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            resposta = requests.post(URL_API, json={"cpf": cpf}, timeout=TIMEOUT_SEGUNDOS)
        except requests.RequestException as erro:
            print(f"  Tentativa {tentativa}: erro de conexão ({type(erro).__name__})")
        else:
            if resposta.status_code == 200:
                return resposta.json()

            if 400 <= resposta.status_code < 500:
                # Erro no nosso pedido: repetir não vai resolver
                raise FalhaNaConsulta(
                    f"Pedido recusado ({resposta.status_code}): {resposta.json().get('erro')}"
                )

            print(f"  Tentativa {tentativa}: serviço respondeu {resposta.status_code}")

        if tentativa < TENTATIVAS:
            time.sleep(ESPERA_SEGUNDOS * tentativa)  # espera cada vez maior

    raise FalhaNaConsulta(f"Serviço indisponível após {TENTATIVAS} tentativas")