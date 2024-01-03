from typing import Any, Dict, List, Optional, Tuple, Type, Union

from json_logic_asp.adapters.asp.asp_literals import PredicateAtom
from json_logic_asp.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.adapters.json_logic.jl_array_nodes import ArrayInNode, ArrayMergeNode
from json_logic_asp.adapters.json_logic.jl_boolean_nodes import BooleanAndNode, BooleanNotNode, BooleanOrNode
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataMissingNode, DataVarNode
from json_logic_asp.adapters.json_logic.jl_logic_nodes import (
    LogicEqualNode,
    LogicGreaterOrEqualThanNode,
    LogicGreaterThanNode,
    LogicIfNode,
    LogicLowerOrEqualThanNode,
    LogicLowerThanNode,
    LogicNotEqualNode,
    LogicStrictEqualNode,
    LogicStrictNotEqualNode,
)
from json_logic_asp.constants.asp_naming import PredicateNames
from json_logic_asp.constants.json_logic_ops import JsonLogicOps
from json_logic_asp.models.json_logic_nodes import JsonLogicNode
from json_logic_asp.models.translator_dto import RuleInput
from json_logic_asp.utils.id_management import generate_constant_string
from json_logic_asp.utils.json_logic_helpers import extract_key_and_value_from_node
from json_logic_asp.utils.list_utils import remove_duplicates

SUPPORTED_NODE_TYPES: Dict[JsonLogicOps, Type] = {
    JsonLogicOps.DATA_VAR: DataVarNode,
    JsonLogicOps.DATA_MISSING: DataMissingNode,
    JsonLogicOps.BOOLEAN_AND: BooleanAndNode,
    JsonLogicOps.BOOLEAN_OR: BooleanOrNode,
    JsonLogicOps.BOOLEAN_NOT: BooleanNotNode,
    JsonLogicOps.LOGIC_IF: LogicIfNode,
    JsonLogicOps.LOGIC_EQ: LogicEqualNode,
    JsonLogicOps.LOGIC_STRICT_EQ: LogicStrictEqualNode,
    JsonLogicOps.LOGIC_NOT_EQ: LogicNotEqualNode,
    JsonLogicOps.LOGIC_STRICT_NOT_EQ: LogicStrictNotEqualNode,
    JsonLogicOps.NUMERIC_GT: LogicGreaterThanNode,
    JsonLogicOps.NUMERIC_GTE: LogicGreaterOrEqualThanNode,
    JsonLogicOps.NUMERIC_LT: LogicLowerThanNode,
    JsonLogicOps.NUMERIC_LTE: LogicLowerOrEqualThanNode,
    JsonLogicOps.ARRAY_MERGE: ArrayMergeNode,
    JsonLogicOps.ARRAY_IN: ArrayInNode,
}


def __get_or_update_cache(node: JsonLogicNode, node_cache: Dict[str, JsonLogicNode]) -> JsonLogicNode:
    node_hash = str(hash(node))

    node = node_cache.get(node_hash, node)
    node_cache[node_hash] = node

    return node


def __is_valid_json_logic_node(node_value: Any, json_logic_node_keys: List[str]):
    if not isinstance(node_value, dict):
        return False

    keys = list(node_value.keys())
    if len(keys) != 1:
        return False

    key = keys[0]
    if not isinstance(key, str):
        return False

    try:
        JsonLogicOps(key)
    except ValueError:
        return key in json_logic_node_keys

    return True


def __parse_json_logic_node(
    node: Dict[str, Any], rule_node_cache: Dict[str, JsonLogicNode], custom_nodes: Dict[str, Type]
) -> JsonLogicNode:
    node_key, node_value = extract_key_and_value_from_node(node)

    supported_nodes: Dict[Union[JsonLogicOps, str], Type] = {
        **SUPPORTED_NODE_TYPES,  # type: ignore
        **custom_nodes,
    }

    if node_key not in supported_nodes:
        raise NotImplementedError(f"Node {node_key} is not yet implemented")

    if isinstance(node_value, dict):
        node_value = [node_value]

    if isinstance(node_value, list):
        node_value = [
            __parse_json_logic_node(node, rule_node_cache, custom_nodes)
            if __is_valid_json_logic_node(node, list(supported_nodes.keys()))
            else node
            for node in node_value
        ]

    node_generator = supported_nodes[node_key]
    if isinstance(node_value, list):
        jl_node = node_generator(*node_value)
    else:
        jl_node = node_generator(node_value)

    return __get_or_update_cache(jl_node, rule_node_cache)


def generate_multiple_rule_asp_definition(
    rule_inputs: List[RuleInput],
    with_comments: bool = False,
    custom_nodes: Optional[Dict[str, Type]] = None,
) -> Tuple[str, Dict[str, str]]:
    """
    Given multiple rule inputs, generate the corresponding ASP definition.

    :param rule_inputs: list of rule input objects to translate
    :param with_comments: whether to include ASP comments
    :param custom_nodes: dictionary of node_key and corresponding class generating the node
    :return: tuple of ASP definition and mapping dictionary (ASP rule to original rule id)
    """
    rule_node_cache: Dict[str, JsonLogicNode] = {}

    statements = []
    root_statements = []

    mapping = {}

    for rule_input in rule_inputs:
        root_node = __parse_json_logic_node(
            node=rule_input.rule_tree,
            rule_node_cache=rule_node_cache,
            custom_nodes=custom_nodes or {},
        )
        statements.extend(root_node.to_asp(with_comment=with_comments))
        # statements = root_node.to_asp()

        hashed_id = generate_constant_string(rule_input.rule_id)
        mapping[hashed_id] = rule_input.rule_id

        root_statement = RuleStatement(
            atom=PredicateAtom(predicate_name=PredicateNames.RULE, terms=[hashed_id]),
            literals=[root_node.get_asp_atom()],
            comment=rule_input.rule_id,
        )
        if with_comments:
            root_statements.append(root_statement.to_asp_comment())
        root_statements.append(root_statement.to_asp_statement())

    statements = remove_duplicates(statements + root_statements)

    return "\n".join(statements), mapping


def generate_single_rule_asp_definition(
    rule_input: RuleInput,
    with_comments: bool = False,
    custom_nodes: Optional[Dict[str, Type]] = None,
) -> str:
    """
    Given a single rule input, generate the corresponding ASP definition.

    :param rule_input: rule input object to translate
    :param with_comments: whether to include ASP comments
    :param custom_nodes: dictionary of node_key and corresponding class generating the node
    :return: ASP definition
    """
    definition, _ = generate_multiple_rule_asp_definition(
        rule_inputs=[rule_input], with_comments=with_comments, custom_nodes=custom_nodes
    )
    return definition
