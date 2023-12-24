from typing import Dict, Union

from json_logic_asp.utils.id_management import generate_constant_string


def extract_key_and_value_from_node(node: Dict):
    node_key = list(node.keys())[0]
    node_value = node[node_key]

    return node_key, node_value


def value_encoder(val: Union[str, int, float, bool]) -> str:
    if isinstance(val, str):
        val = generate_constant_string(val)
    elif isinstance(val, bool):
        val = str(val).lower()
    elif isinstance(val, float):
        # TODO: This is wrong...
        val = str(int(val))
    elif isinstance(val, int):
        val = str(val)
    else:
        val = str(val)

    return val
