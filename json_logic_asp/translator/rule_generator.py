from typing import Any, Dict, List, Optional

from json_logic_asp.constants.json_logic_ops import JsonLogicOps
from json_logic_asp.translator.adapters.asp.asp_nodes import PredicateAtom
from json_logic_asp.translator.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.translator.adapters.json_logic.jl_array_nodes import ArrayInNode
from json_logic_asp.translator.adapters.json_logic.jl_boolean_nodes import BooleanAndNode, BooleanNotNode, BooleanOrNode
from json_logic_asp.translator.adapters.json_logic.jl_data_nodes import DataVarNode
from json_logic_asp.translator.adapters.json_logic.jl_logic_nodes import LogicEvalNode
from json_logic_asp.translator.models.jl_base import JsonLogicDefinitionNode
from json_logic_asp.translator.models.translator import RuleInput
from json_logic_asp.utils.json_logic_helpers import extract_key_and_value_from_node
from json_logic_asp.utils.list_utils import remove_duplicates

RULE_NODE_CACHE: Dict[str, JsonLogicDefinitionNode] = {}


def __parse_json_logic_node(node: Dict[str, Any]) -> JsonLogicDefinitionNode:
    node_key, node_value = extract_key_and_value_from_node(node)

    jl_node: Optional[JsonLogicDefinitionNode] = None
    if node_key == JsonLogicOps.DATA_VAR:
        jl_node = DataVarNode(var_name=node_value)
        h = str(hash(jl_node))
        if h in RULE_NODE_CACHE:
            jl_node = RULE_NODE_CACHE[h]
        else:
            RULE_NODE_CACHE[h] = jl_node

    if jl_node is not None:
        return jl_node

    child_nodes: List[JsonLogicDefinitionNode]
    if isinstance(node_value, list):
        child_nodes = [__parse_json_logic_node(child) if isinstance(child, dict) else child for child in node_value]
    elif isinstance(node_value, dict):
        child_nodes = [__parse_json_logic_node(node_value) if isinstance(node_value, dict) else node_value]
    else:
        raise ValueError(f"Unknown node type: {node_value}")

    if node_key == JsonLogicOps.BOOLEAN_AND:
        jl_node = BooleanAndNode(child_nodes)
    elif node_key == JsonLogicOps.BOOLEAN_OR:
        jl_node = BooleanOrNode(child_nodes)
    elif node_key == JsonLogicOps.BOOLEAN_NOT:
        jl_node = BooleanNotNode(child_nodes)
    elif node_key == JsonLogicOps.LOGIC_EQ:
        if len(child_nodes) != 2:
            raise ValueError(f"EQ operator expects 2 children, received {len(child_nodes)}")
        jl_node = LogicEvalNode(
            comparator="==", predicate="eq", left_statement=child_nodes[0], right_statement=child_nodes[1]
        )
    elif node_key == JsonLogicOps.LOGIC_NOT_EQ:
        if len(child_nodes) != 2:
            raise ValueError(f"NEQ operator expects 2 children, received {len(child_nodes)}")
        jl_node = LogicEvalNode(
            comparator="!=", predicate="neq", left_statement=child_nodes[0], right_statement=child_nodes[1]
        )
    elif node_key == JsonLogicOps.NUMERIC_GT:
        if len(child_nodes) != 2:
            raise ValueError(f"GT operator expects 2 children, received {len(child_nodes)}")
        jl_node = LogicEvalNode(
            comparator=">", predicate="gt", left_statement=child_nodes[0], right_statement=child_nodes[1]
        )
    elif node_key == JsonLogicOps.NUMERIC_GTE:
        if len(child_nodes) != 2:
            raise ValueError(f"GTE operator expects 2 children, received {len(child_nodes)}")
        jl_node = LogicEvalNode(
            comparator=">=", predicate="gte", left_statement=child_nodes[0], right_statement=child_nodes[1]
        )
    elif node_key == JsonLogicOps.NUMERIC_LT:
        if len(child_nodes) != 2:
            raise ValueError(f"LT operator expects 2 children, received {len(child_nodes)}")
        jl_node = LogicEvalNode(
            comparator="<", predicate="lt", left_statement=child_nodes[0], right_statement=child_nodes[1]
        )
    elif node_key == JsonLogicOps.NUMERIC_LTE:
        if len(child_nodes) != 2:
            raise ValueError(f"LTE operator expects 2 children, received {len(child_nodes)}")
        jl_node = LogicEvalNode(
            comparator="<=", predicate="lte", left_statement=child_nodes[0], right_statement=child_nodes[1]
        )
    elif node_key == JsonLogicOps.ARRAY_IN:
        if len(child_nodes) != 2:
            raise ValueError(f"IN operator expects 2 children, received {len(child_nodes)}")
        jl_node = ArrayInNode(left_statement=child_nodes[0], right_statement=child_nodes[1])
    else:
        raise NotImplementedError(f"Node {node_key} is not yet implemented")

    h = str(hash(jl_node))
    if h in RULE_NODE_CACHE:
        jl_node = RULE_NODE_CACHE[h]
    else:
        RULE_NODE_CACHE[h] = jl_node

    return jl_node


def generate_multiple_rule_asp_definition(rules: List[RuleInput]) -> str:
    global RULE_NODE_CACHE
    RULE_NODE_CACHE = dict()

    statements = []
    root_statements = []

    for rule_input in rules:
        root_node = __parse_json_logic_node(node=rule_input.rule_tree)
        statements.extend(root_node.to_asp())
        # statements = root_node.to_asp()

        root_statement = RuleStatement(
            atom=PredicateAtom(predicate_name="rule", terms=[f"'{rule_input.rule_id}'"]),
            literals=[stmt.atom for stmt in root_node.asp_statements],
        )
        root_statements.append(root_statement.to_asp())

    statements = remove_duplicates(statements + root_statements)

    return "\n".join(statements)


def generate_single_rule_asp_definition(rule_input: RuleInput) -> str:
    return generate_multiple_rule_asp_definition([rule_input])
