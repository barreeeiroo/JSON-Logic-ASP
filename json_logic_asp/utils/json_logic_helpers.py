from typing import Dict


def extract_key_and_value_from_node(node: Dict):
    node_key = list(node.keys())[0]
    node_value = node[node_key]

    return node_key, node_value
