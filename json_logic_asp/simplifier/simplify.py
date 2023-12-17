from typing import Dict


def simplify_json_logic(rule: Dict):
    if not isinstance(rule, dict):
        raise ValueError('Expected a dictionary to be simplified')


