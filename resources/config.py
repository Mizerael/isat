import logging.config
import json
import logging


def configure_logging() -> None:
    with open("config/logger.json") as f:
        d = json.load(f)
        logging.config.dictConfig(d["logger"])


def get_config(path_to_config: str) -> dict:
    with open(path_to_config) as f:
        return json.load(f)
