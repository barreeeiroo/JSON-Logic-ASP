from json_logic_asp.adapters.json_logic.jl_logic_nodes import (
    LogicEqualNode,
    LogicEvalNode,
    LogicGreaterOrEqualThanNode,
    LogicGreaterThanNode,
    LogicLowerOrEqualThanNode,
    LogicLowerThanNode,
    LogicNotEqualNode,
    LogicStrictEqualNode,
    LogicStrictNotEqualNode,
)


def test_logic_equal_node():
    node = LogicEqualNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "eq"
    assert node.comparator == "=="


def test_logic_not_equal_node():
    node = LogicNotEqualNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "neq"
    assert node.comparator == "!="


def test_logic_strict_equal_node():
    node = LogicStrictEqualNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "seq"
    # assert node.comparator == "==="


def test_logic_strict_not_equal_node():
    node = LogicStrictNotEqualNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "sneq"
    # assert node.comparator == "!=="


def test_logic_lower_than_node():
    node = LogicLowerThanNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "lt"
    assert node.comparator == "<"


def test_logic_lower_or_equal_than_node():
    node = LogicLowerOrEqualThanNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "lte"
    assert node.comparator == "<="


def test_logic_greater_than_node():
    node = LogicGreaterThanNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "gt"
    assert node.comparator == ">"


def test_logic_greater_or_equal_than_node():
    node = LogicGreaterOrEqualThanNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "gte"
    assert node.comparator == ">="
