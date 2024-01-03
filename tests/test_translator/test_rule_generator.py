from typing import Dict, List
from unittest.mock import patch

import pytest

from json_logic_asp.adapters.json_logic.jl_boolean_nodes import BooleanAndNode, BooleanNotNode
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataMissingNode, DataVarNode
from json_logic_asp.adapters.json_logic.jl_logic_nodes import LogicEqualNode
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import JsonLogicNode, JsonLogicTreeNode
from json_logic_asp.models.translator_dto import RuleInput
from json_logic_asp.translator import generate_multiple_rule_asp_definition, generate_single_rule_asp_definition
from json_logic_asp.translator.rule_generator import (
    SUPPORTED_NODE_TYPES,
    __get_or_update_cache,
    __is_valid_json_logic_node,
    __parse_json_logic_node,
)
from tests.fixtures import cuid_fixture  # noqa


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
        ({"var": "abc"}, DataVarNode("abc")),
        ({"missing": "a"}, DataMissingNode("a")),
        ({"==": [{"var": "acd"}, "b"]}, LogicEqualNode(DataVarNode("acd"), "b")),
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


@pytest.mark.parametrize(
    "rule_inputs, with_comments, custom_nodes, expected_statements, expected_mapping",
    [
        (
            [
                RuleInput(
                    rule_id="test",
                    rule_tree={"and": {"==": [{"var": "a"}, "b"]}},
                ),
            ],
            False,
            None,
            [
                "eq(mock2) :- var(s0cc175b9c0f1b6a831c399e269772661, V1), V1 == s92eb5ffee6ae2fec3ad71c777531578f.",
                "and(mock3) :- eq(mock2).",
                "rule(s098f6bcd4621d373cade4e832627b4f6) :- and(mock3).",
            ],
            {"s098f6bcd4621d373cade4e832627b4f6": "test"},
        ),
        (
            [
                RuleInput(
                    rule_id="test",
                    rule_tree={"and": {"==": [{"var": "a"}, "b"]}},
                ),
            ],
            True,
            None,
            [
                "% a EQ b",
                "eq(mock2) :- var(s0cc175b9c0f1b6a831c399e269772661, V1), V1 == s92eb5ffee6ae2fec3ad71c777531578f.",
                "and(mock3) :- eq(mock2).",
                "% test",
                "rule(s098f6bcd4621d373cade4e832627b4f6) :- and(mock3).",
            ],
            {"s098f6bcd4621d373cade4e832627b4f6": "test"},
        ),
        (
            [
                RuleInput(
                    rule_id="test1",
                    rule_tree={"and": {"==": [{"var": "a"}, "b"]}},
                ),
                RuleInput(
                    rule_id="test2",
                    rule_tree={"or": {"<": [{"var": "c"}, "d"]}},
                ),
            ],
            True,
            None,
            [
                "% a EQ b",
                "eq(mock2) :- var(s0cc175b9c0f1b6a831c399e269772661, V1), V1 == s92eb5ffee6ae2fec3ad71c777531578f.",
                "and(mock3) :- eq(mock2).",
                "% c LT d",
                "lt(mock5) :- var(s4a8a08f09d37b73795649038408b5f33, V1), V1 < s8277e0910d750195b448797616e091ad.",
                "or(mock6) :- lt(mock5).",
                "% test1",
                "rule(s5a105e8b9d40e1329780d62ea2265d8a) :- and(mock3).",
                "% test2",
                "rule(sad0234829205b9033196ba818f7a872b) :- or(mock6).",
            ],
            {
                "s5a105e8b9d40e1329780d62ea2265d8a": "test1",
                "sad0234829205b9033196ba818f7a872b": "test2",
            },
        ),
        (
            [
                RuleInput(
                    rule_id="test1",
                    rule_tree={"and": {"==": [{"var": "a"}, "b"]}},
                ),
                RuleInput(
                    rule_id="test2",
                    rule_tree={"or": {"==": [{"var": "a"}, "b"]}},
                ),
            ],
            True,
            None,
            [
                "% a EQ b",
                "eq(mock2) :- var(s0cc175b9c0f1b6a831c399e269772661, V1), V1 == s92eb5ffee6ae2fec3ad71c777531578f.",
                "and(mock3) :- eq(mock2).",
                "or(mock6) :- eq(mock2).",
                "% test1",
                "rule(s5a105e8b9d40e1329780d62ea2265d8a) :- and(mock3).",
                "% test2",
                "rule(sad0234829205b9033196ba818f7a872b) :- or(mock6).",
            ],
            {
                "s5a105e8b9d40e1329780d62ea2265d8a": "test1",
                "sad0234829205b9033196ba818f7a872b": "test2",
            },
        ),
        (
            [
                RuleInput(
                    rule_id="test",
                    rule_tree={"op": "dummy"},
                ),
            ],
            True,
            {"op": DummyTestNode},
            [
                "% test",
                "rule(s098f6bcd4621d373cade4e832627b4f6) :- dummy(mock1).",
            ],
            {"s098f6bcd4621d373cade4e832627b4f6": "test"},
        ),
    ],
    ids=[
        "no_comments",
        "with_comments",
        "multi_rule",
        "node_cache",
        "custom_nodes",
    ],
)
def test_generate_multiple_rule_asp_definition(
    rule_inputs, with_comments, custom_nodes, expected_statements, expected_mapping
):
    statements, mapping = generate_multiple_rule_asp_definition(
        rule_inputs=rule_inputs,
        with_comments=with_comments,
        custom_nodes=custom_nodes,
    )

    assert statements == "\n".join(expected_statements)
    assert mapping == expected_mapping


@pytest.mark.parametrize(
    "with_comments, custom_nodes",
    [
        (False, None),
        (True, None),
        (False, {"dummy": None}),
        (True, {"dummy": None}),
    ],
    ids=[
        "simple",
        "with_comments",
        "custom_nodes",
        "both",
    ],
)
@patch("json_logic_asp.translator.rule_generator.generate_multiple_rule_asp_definition")
def test_generate_single_rule_asp_definition_call(
    mock_generate_multiple_rule_asp_definition, with_comments, custom_nodes
):
    mock_generate_multiple_rule_asp_definition.return_value = ("stmt1\nstmt2", {"a": "b"})

    ri = RuleInput(
        rule_id="a",
        rule_tree={"c": "d"},
    )
    asp_definition = generate_single_rule_asp_definition(ri, with_comments=with_comments, custom_nodes=custom_nodes)

    assert asp_definition == "stmt1\nstmt2"
    mock_generate_multiple_rule_asp_definition.assert_called_once_with(
        rule_inputs=[ri],
        with_comments=with_comments,
        custom_nodes=custom_nodes,
    )


def test_generate_single_rule_asp_definition_simple():
    ri = RuleInput(
        rule_id="test",
        rule_tree={"and": {"==": [{"var": "a"}, "b"]}},
    )

    asp_definition = generate_single_rule_asp_definition(ri, with_comments=True)
    assert asp_definition == "\n".join(
        [
            "% a EQ b",
            "eq(mock2) :- var(s0cc175b9c0f1b6a831c399e269772661, V1), V1 == s92eb5ffee6ae2fec3ad71c777531578f.",
            "and(mock3) :- eq(mock2).",
            "% test",
            "rule(s098f6bcd4621d373cade4e832627b4f6) :- and(mock3).",
        ]
    )
