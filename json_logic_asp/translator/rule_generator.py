from typing import Any, Dict, List, Tuple, Type

from json_logic_asp.adapters.asp.asp_literals import PredicateAtom
from json_logic_asp.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.adapters.json_logic.jl_array_nodes import ArrayInNode
from json_logic_asp.adapters.json_logic.jl_boolean_nodes import BooleanAndNode, BooleanNotNode, BooleanOrNode
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataMissingNode, DataVarNode
from json_logic_asp.adapters.json_logic.jl_logic_nodes import (
    LogicIfNode,
    LogicEqualNode,
    LogicGreaterOrEqualThanNode,
    LogicGreaterThanNode,
    LogicLowerOrEqualThanNode,
    LogicLowerThanNode,
    LogicNotEqualNode,
    LogicStrictEqualNode,
    LogicStrictNotEqualNode,
)
from json_logic_asp.constants.json_logic_ops import JsonLogicOps
from json_logic_asp.models.json_logic_nodes import JsonLogicNode
from json_logic_asp.models.translator_dto import RuleInput
from json_logic_asp.utils.id_management import generate_constant_string
from json_logic_asp.utils.json_logic_helpers import extract_key_and_value_from_node
from json_logic_asp.utils.list_utils import remove_duplicates

RULE_NODE_CACHE: Dict[str, JsonLogicNode] = {}

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
    JsonLogicOps.ARRAY_IN: ArrayInNode,
}


def __parse_json_logic_node(node: Dict[str, Any]) -> JsonLogicNode:
    node_key, node_value = extract_key_and_value_from_node(node)

    if node_key not in SUPPORTED_NODE_TYPES:
        raise NotImplementedError(f"Node {node_key} is not yet implemented")

    if isinstance(node_value, dict):
        node_value = [node_value]

    if isinstance(node_value, list):
        node_value = [__parse_json_logic_node(node) if isinstance(node, dict) else node for node in node_value]

    jl_node = SUPPORTED_NODE_TYPES[node_key](node_value)

    h = str(hash(jl_node))
    if h in RULE_NODE_CACHE:
        jl_node = RULE_NODE_CACHE[h]
    else:
        RULE_NODE_CACHE[h] = jl_node

    return jl_node


def generate_multiple_rule_asp_definition(
    rule_inputs: List[RuleInput],
    with_comments: bool = False,
) -> Tuple[str, Dict[str, str]]:
    global RULE_NODE_CACHE
    RULE_NODE_CACHE = dict()

    statements = []
    root_statements = []

    mapping = {}

    for rule_input in rule_inputs:
        root_node = __parse_json_logic_node(node=rule_input.rule_tree)
        statements.extend(root_node.to_asp(with_comment=with_comments))
        # statements = root_node.to_asp()

        hashed_id = generate_constant_string(rule_input.rule_id)
        mapping[hashed_id] = rule_input.rule_id

        root_statement = RuleStatement(
            atom=PredicateAtom(predicate_name="rule", terms=[hashed_id]),
            literals=[root_node.get_asp_atom()],
            comment=rule_input.rule_id,
        )
        if with_comments:
            root_statements.append(root_statement.to_asp_comment())
        root_statements.append(root_statement.to_asp_statement())

    statements = remove_duplicates(statements + root_statements)

    return "\n".join(statements), mapping


def generate_single_rule_asp_definition(rule_input: RuleInput, with_comments: bool = False) -> str:
    definition, _ = generate_multiple_rule_asp_definition(rule_inputs=[rule_input], with_comments=with_comments)
    return definition
