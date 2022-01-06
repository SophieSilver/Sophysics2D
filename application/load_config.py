import json
from typing import Dict


def load_config(path) -> Dict:
    with open(path, "r", encoding="utf-8") as config:
        json_string = config.read()

    config_dict = json.loads(json_string)
    return config_dict
