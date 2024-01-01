from typing import Dict, List

import pytest

from json_logic_asp.adapters.json_logic.jl_boolean_nodes import BooleanAndNode, BooleanNotNode
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataMissingNode, DataVarNode
from json_logic_asp.adapters.json_logic.jl_logic_nodes import LogicEqualNode
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import JsonLogicNode, JsonLogicTreeNode
from json_logic_asp.translator.rule_generator import (
    SUPPORTED_NODE_TYPES,
    __get_or_update_cache,
    __is_valid_json_logic_node,
    __parse_json_logic_node,
)


class DummyTestNode(JsonLogicTreeNode):
    def get_asp_statements(self) -> List[Statement]:
        return []


def test_get_or_update_cache_not_present():
    dummy_new_node = DummyTestNode(operation_name="test")
    assert __get_or_update_cache(dummy_new_node, {}) == dummy_new_node


def test_get_or_update_cache_present():
    dummy_existing_node = DummyTestNode(operation_name="test2")
    dummy_new_node = DummyTestNode(operation_name="test")

    node_cache: Dict[str, JsonLogicNode] = {str(hash(dummy_new_node)): dummy_existing_node}
    cached_node = __get_or_update_cache(dummy_new_node, node_cache)

    assert dummy_new_node != cached_node == dummy_existing_node


@pytest.mark.parametrize(
    "node",
    ["abc", {"a": "b", "c": "d"}, {123: "b"}, {"wrong key": "b"}],
    ids=[
        "non_dict",
        "multi_key",
        "non_str_key",
        "unknown_op",
    ],
)
def test_is_valid_json_logic_node_invalid_nodes(node):
    assert not __is_valid_json_logic_node(node, list(SUPPORTED_NODE_TYPES.keys()))


def test_is_valid_json_logic_node_standard_op():
    assert __is_valid_json_logic_node({"==": []}, [])


def test_is_valid_json_logic_node_custom_op():
    assert __is_valid_json_logic_node({"op": []}, ["op"])


@pytest.mark.parametrize(
    "json_logic_dict, json_logic_obj",
    [
        ({"var": "a"}, DataVarNode("a")),
        ({"missing": "a"}, DataMissingNode("a")),
        ({"==": [{"var": "a"}, "b"]}, LogicEqualNode(DataVarNode("a"), "b")),
        (
            {
                "and": [
                    {"==": [{"var": "a"}, "b"]},
                    {"missing": "c"},
                ]
            },
            BooleanAndNode(LogicEqualNode(DataVarNode("a"), "b"), DataMissingNode("c")),
        ),
        (
            {
                "!": {"var": "a"},
            },
            BooleanNotNode(DataVarNode("a")),
        ),
    ],
    ids=[
        "var",
        "missing",
        "equals",
        "and",
        "not",
    ],
)
def test_parse_json_logic_node(json_logic_dict, json_logic_obj):
    assert __parse_json_logic_node(json_logic_dict, {}, {}) == json_logic_obj


def test_parse_json_logic_node_unknown_op():
    with pytest.raises(NotImplementedError) as e:
        __parse_json_logic_node({"op": "a"}, {}, {})

    assert e.match("Node op is not yet implemented")


def test_parse_json_logic_node_custom_op():
    custom_nodes = {"op": DummyTestNode}
    res_node = DummyTestNode("a")
    assert __parse_json_logic_node({"op": "a"}, {}, custom_nodes) == res_node
