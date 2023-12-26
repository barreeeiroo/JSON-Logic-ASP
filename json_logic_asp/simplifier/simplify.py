from typing import Dict

from json_logic_asp.simplifier.node_simplifier import simplify_node


def simplify_json_logic(rule: Dict):
    """
    Simplify a given JSON Logic rule.

    :param rule: parsed JSON Logic rule definition
    :return: simplified JSON Logic rule definition after applying the simplifiers
    """

    if not isinstance(rule, dict):
        raise ValueError("Expected a dictionary to be simplified")

    return simplify_node(rule)
