"""Configuração dos logs técnicos, compartilhada pelos scripts do robô."""
import logging
from pathlib import Path

PASTA_LOGS = Path(__file__).parent.parent / "logs"


def configurar_log():
    """Envia os registros para a tela e para o arquivo logs/robo.log."""
    PASTA_LOGS.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        handlers=[
            logging.FileHandler(PASTA_LOGS / "robo.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
