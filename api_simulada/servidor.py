"""
API SIMULADA de consulta de crédito (restritivos + SCR).
Imita um serviço externo, inclusive suas instabilidades.

Uso: python api_simulada/servidor.py
"""
import os
import random

from flask import Flask, jsonify, request

app = Flask(__name__)

# Chance de o serviço "cair" em cada chamada (0.3 = 30%)
TAXA_FALHA = float(os.environ.get("TAXA_FALHA", "0.3"))

# Base FICTÍCIA do "birô de crédito"
BASE_FICTICIA = {
    "000.000.001-01": {"tem_restritivo": False, "parcelas_mensais_scr": 600.0},
    "000.000.002-02": {"tem_restritivo": True,  "parcelas_mensais_scr": 900.0},
    "000.000.003-03": {"tem_restritivo": False, "parcelas_mensais_scr": 1200.0},
    "000.000.005-05": {"tem_restritivo": False, "parcelas_mensais_scr": 800.0},
    "000.000.006-06": {"tem_restritivo": False, "parcelas_mensais_scr": 1500.0},
    "000.000.007-07": {"tem_restritivo": False, "parcelas_mensais_scr": 900.0},
}


@app.post("/consultas")
def consultar():
    dados = request.get_json(silent=True) or {}
    cpf = dados.get("cpf")

    if not cpf:
        return jsonify({"erro": "Campo 'cpf' é obrigatório"}), 400

    if random.random() < TAXA_FALHA:
        return jsonify({"erro": "Serviço temporariamente indisponível"}), 503

    if cpf not in BASE_FICTICIA:
        return jsonify({"erro": "CPF não encontrado"}), 404

    return jsonify({"cpf": cpf, **BASE_FICTICIA[cpf]}), 200


if __name__ == "__main__":
    app.run(port=5050)