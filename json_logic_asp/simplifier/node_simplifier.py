import logging
from typing import Any, Callable, Dict

from json_logic_asp.constants.json_logic_ops import JsonLogicOps
from json_logic_asp.constants.loggers import SIMPLIFIER_LOGGER_NAME
from json_logic_asp.utils.json_logic_helpers import extract_key_and_value_from_node

logger = logging.getLogger(SIMPLIFIER_LOGGER_NAME)


def simplify_and_or_nodes(node_key: str, node_values: Any):
    simplified_node_values = []

    if not isinstance(node_values, list):
        logger.debug(f"Found non-array value at {node_key}, converting to list")
        node_values = [node_values]

    for node_value in node_values:
        if isinstance(node_value, dict):
            simplified_node_value = simplify_node(node_value)
        else:
            simplified_node_value = node_value

        if isinstance(simplified_node_value, dict):
            child_key, child_value = extract_key_and_value_from_node(simplified_node_value)
            # If the nested is another AND or OR of the same type, put the elements in the same level
            if child_key == node_key:
                simplified_node_values.extend(child_value)
                continue

        if node_key == JsonLogicOps.BOOLEAN_AND:
            if simplified_node_value is False:
                # If value is False then the AND condition can never be satisfied
                return False
            if simplified_node_value is True:
                # Or if value is True, then skip it as it's redundant
                continue
        elif node_key == JsonLogicOps.BOOLEAN_OR:
            if simplified_node_value is False:
                # If value is False, skip it as it doesn't change the evaluation
                continue
            if simplified_node_value is True:
                # Or if the value is True, the OR condition will always be true
                return True

        if simplified_node_value:
            simplified_node_values.append(simplified_node_value)

    if len(simplified_node_values) == 0:
        logger.debug(f"Node {node_key} is empty, does never evaluate to True")
        return False

    if len(simplified_node_values) == 1:
        logger.debug(f"Node {node_key} has one node, should be removed")
        return simplified_node_values[0]

    return {node_key: simplified_node_values}


def simplify_negation_nodes(node_key: str, node_values: Any):
    double_negation = node_key == JsonLogicOps.BOOLEAN_NOT_NOT

    if isinstance(node_values, list):
        if len(node_values) == 0:
            logger.debug(f"Found empty {node_key}, evaluating")
            # JL evaluates to False on empty arrays, so return True when not double negation
            return not double_negation

        logger.debug(f"Found array value at {node_key}, exploding")
        node_value = node_values[0]
    else:
        node_value = node_values

    def evaluate_value(value):
        single_neg_evaluation = not bool(value)
        return_eval = single_neg_evaluation if not double_negation else not single_neg_evaluation

        if isinstance(value, (int, float, str, bool)):
            logger.debug(f"Evaluating {node_key} as primitive, resolving")
            return return_eval

        return None

    pre_simplification_eval = evaluate_value(node_value)
    if pre_simplification_eval is not None:
        return pre_simplification_eval

    simplified_node_value = simplify_node(node_value)

    simplified_eval = evaluate_value(simplified_node_value)
    if simplified_eval is not None:
        return simplified_eval

    return {node_key: simplified_node_value}


SIMPLIFIABLE_OPERATIONS: Dict[str, Callable] = {
    JsonLogicOps.BOOLEAN_AND: simplify_and_or_nodes,
    JsonLogicOps.BOOLEAN_OR: simplify_and_or_nodes,
    JsonLogicOps.BOOLEAN_NOT: simplify_negation_nodes,
    JsonLogicOps.BOOLEAN_NOT_NOT: simplify_negation_nodes,
}


def simplify_node(node: Dict):
    node_key, node_value = extract_key_and_value_from_node(node)

    if node_key not in SIMPLIFIABLE_OPERATIONS:
        logger.debug(f"Node {node_key} cannot be simplified, skipping")
        return node

    return SIMPLIFIABLE_OPERATIONS[node_key](node_key=node_key, node_values=node_value)
