from typing import Dict

from json_logic_asp.simplifier.node_simplifier import simplify_node


def simplify_json_logic(rule: Dict):
    if not isinstance(rule, dict):
        raise ValueError("Expected a dictionary to be simplified")

    return simplify_node(rule)
