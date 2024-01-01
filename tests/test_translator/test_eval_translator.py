from unittest.mock import patch

import pytest

from json_logic_asp.models.translator_dto import DataInput, RuleInput, RuleOutput
from json_logic_asp.translator import translate_multi_rule_eval, translate_single_rule_eval
from tests.fixtures import cuid_fixture  # noqa


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
@patch("json_logic_asp.translator.eval_translator.generate_multiple_rule_asp_definition")
@patch("json_logic_asp.translator.eval_translator.generate_single_data_asp_definition")
def test_translate_multi_rule_eval(
    mock_generate_single_data_asp_definition, mock_generate_multiple_rule_asp_definition, with_comments, custom_nodes
):
    mock_generate_single_data_asp_definition.return_value = "var1\nvar2\nvar3"
    mock_generate_multiple_rule_asp_definition.return_value = "stmt1\nstmt2\nstmt3", {"a": "b", "c": "d"}

    ri1 = RuleInput(
        rule_id="test1",
        rule_tree={"and": {"==": [{"var": "a"}, "b"]}},
    )
    ri2 = RuleInput(
        rule_id="test2",
        rule_tree={"or": {">": [{"var": "c"}, "d"]}},
    )
    di = DataInput(
        data_id="b",
        data_object={
            "e": "f",
            "g": {"h": "i"},
        },
    )
    rule_output = translate_multi_rule_eval([ri1, ri2], di, with_comments=with_comments, custom_nodes=custom_nodes)

    assert rule_output.statements == ["var1", "var2", "var3", "", "stmt1", "stmt2", "stmt3", "", "#show rule/1."]
    assert rule_output.rule_mapping == {"a": "b", "c": "d"}
    mock_generate_single_data_asp_definition.assert_called_once_with(
        data_input=di,
        with_comments=with_comments,
    )
    mock_generate_multiple_rule_asp_definition.assert_called_once_with(
        rule_inputs=[ri1, ri2],
        with_comments=with_comments,
        custom_nodes=custom_nodes,
    )


def test_translate_multi_rule_eval_simple():
    ri1 = RuleInput(
        rule_id="test1",
        rule_tree={"and": {"==": [{"var": "a"}, "b"]}},
    )
    ri2 = RuleInput(
        rule_id="test2",
        rule_tree={"or": {">": [{"var": "c"}, "d"]}},
    )
    di = DataInput(
        data_id="e",
        data_object={
            "f": "g",
            "h": {"i": "j"},
        },
    )

    rule_output = translate_multi_rule_eval([ri1, ri2], di, with_comments=True)

    assert rule_output.statements == [
        "% f : g",
        "var(s8fa14cdd754f91cc6554c9e71929cce7, sb2f5ff47436671b6e533d8dc3614845d).",
        "% h.i : j",
        "var(sd95e8ab9a13affcd43b13b0b5443d484, s363b122c528f54df4a0446b6bab05515).",
        "",
        "% a EQ b",
        "eq(mock2) :- var(s0cc175b9c0f1b6a831c399e269772661, V1), V1 == s92eb5ffee6ae2fec3ad71c777531578f.",
        "and(mock3) :- eq(mock2).",
        "% c GT d",
        "gt(mock5) :- var(s4a8a08f09d37b73795649038408b5f33, V1), V1 > s8277e0910d750195b448797616e091ad.",
        "or(mock6) :- gt(mock5).",
        "% test1",
        "rule(s5a105e8b9d40e1329780d62ea2265d8a) :- and(mock3).",
        "% test2",
        "rule(sad0234829205b9033196ba818f7a872b) :- or(mock6).",
        "",
        "#show rule/1.",
    ]
    assert rule_output.rule_mapping == {
        "s5a105e8b9d40e1329780d62ea2265d8a": "test1",
        "sad0234829205b9033196ba818f7a872b": "test2",
    }


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
@patch("json_logic_asp.translator.eval_translator.translate_multi_rule_eval")
def test_translate_single_rule_eval(mock_translate_multi_rule_eval, with_comments, custom_nodes):
    mock_ro = RuleOutput(
        statements=[],
        rule_mapping={},
    )
    mock_translate_multi_rule_eval.return_value = mock_ro

    ri = RuleInput(
        rule_id="a",
        rule_tree={"c": "d"},
    )
    di = DataInput(
        data_id="b",
        data_object={
            "e": "f",
            "g": {"h": "i"},
        },
    )
    rule_output = translate_single_rule_eval(ri, di, with_comments=with_comments, custom_nodes=custom_nodes)

    assert rule_output == mock_ro
    mock_translate_multi_rule_eval.assert_called_once_with(
        rule_inputs=[ri],
        data_input=di,
        with_comments=with_comments,
        custom_nodes=custom_nodes,
    )


def test_translate_single_rule_eval_simple():
    ri = RuleInput(
        rule_id="test",
        rule_tree={"and": {"==": [{"var": "a"}, "b"]}},
    )
    di = DataInput(
        data_id="b",
        data_object={
            "e": "f",
            "g": {"h": "i"},
        },
    )

    rule_output = translate_single_rule_eval(ri, di, with_comments=True)

    assert rule_output.statements == [
        "% e : f",
        "var(se1671797c52e15f763380b45e841ec32, s8fa14cdd754f91cc6554c9e71929cce7).",
        "% g.h : i",
        "var(s08a6c56ffa6dc13f368e7e73c0ca58ec, s865c0c0b4ab0e063e5caa3387c1a8741).",
        "",
        "% a EQ b",
        "eq(mock2) :- var(s0cc175b9c0f1b6a831c399e269772661, V1), V1 == s92eb5ffee6ae2fec3ad71c777531578f.",
        "and(mock3) :- eq(mock2).",
        "% test",
        "rule(s098f6bcd4621d373cade4e832627b4f6) :- and(mock3).",
        "",
        "#show rule/1.",
    ]
    assert rule_output.rule_mapping == {"s098f6bcd4621d373cade4e832627b4f6": "test"}
