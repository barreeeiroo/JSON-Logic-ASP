from unittest.mock import patch

from json_logic_asp.evaluator import (
    evaluate_multiple_json_logic_rules_against_single_data,
    evaluate_pregenerated_json_logic_rules_against_single_data,
    evaluate_single_json_logic_rule_against_single_data,
)
from json_logic_asp.models.translator_dto import DataInput, RuleInput


@patch("json_logic_asp.evaluator.get_matching_rules_for_asp_rules_and_data")
@patch("json_logic_asp.evaluator.generate_single_data_asp_definition")
def test_evaluate_pregenerated_json_logic_rules_against_single_data(
    mock_generate_single_data_asp_definition, mock_get_matching_rules_for_asp_rules_and_data
):
    mock_generate_single_data_asp_definition.return_value = "var(a, b)"
    mock_get_matching_rules_for_asp_rules_and_data.return_value = ["c"]

    di = DataInput(
        data_id="test",
        data_object={"a": "b"},
    )

    res = evaluate_pregenerated_json_logic_rules_against_single_data(
        json_logic_rules_in_asp_definition="rule(c).",
        json_logic_data=di,
        rule_id_mapping={"c": "d"},
    )

    mock_generate_single_data_asp_definition.assert_called_once_with(
        data_input=di,
        with_comments=False,
    )
    mock_get_matching_rules_for_asp_rules_and_data.assert_called_once_with(
        asp_data_definition="var(a, b)",
        asp_rules_definition="rule(c).",
        mapping={"c": "d"},
    )

    assert res == ["c"]


def test_evaluate_pregenerated_json_logic_rules_against_single_data_simple():
    di = DataInput(
        data_id="test",
        data_object={"var1": "a"},
    )

    res = evaluate_pregenerated_json_logic_rules_against_single_data(
        json_logic_rules_in_asp_definition="rule(b) :- var(s6482a3f94854f5920ef720dbf7944d49, _).",
        json_logic_data=di,
        rule_id_mapping={"b": "r1"},
    )

    assert res == ["r1"]


def test_evaluate_multiple_json_logic_rules_against_single_data():
    json_logic_rules = [
        RuleInput(rule_id="rule1", rule_tree={"==": [{"var": "a"}, "b"]}),
        RuleInput(rule_id="rule2", rule_tree={"<": [{"var": "c"}, 3]}),
        RuleInput(rule_id="rule3", rule_tree={"missing": "d"}),
    ]

    json_logic_data = DataInput(
        data_id="data1",
        data_object={
            "a": "b",
            "c": 2,
            "d": "e",
        },
    )

    rules = evaluate_multiple_json_logic_rules_against_single_data(
        json_logic_rules=json_logic_rules,
        json_logic_data=json_logic_data,
        simplify=False,
    )

    assert sorted(rules) == sorted(["rule1", "rule2"])


def test_evaluate_multiple_json_logic_rules_against_single_data_simplify():
    json_logic_rules = [
        RuleInput(rule_id="rule1", rule_tree={"and": [True, {"missing": "d"}]}),
    ]

    json_logic_data = DataInput(
        data_id="data1",
        data_object={
            "a": "b",
            "c": 2,
        },
    )

    rules = evaluate_multiple_json_logic_rules_against_single_data(
        json_logic_rules=json_logic_rules,
        json_logic_data=json_logic_data,
        simplify=True,
    )

    assert sorted(rules) == sorted(["rule1"])


def test_evaluate_single_json_logic_rule_against_single_data():
    json_logic_rule = RuleInput(rule_id="rule1", rule_tree={"==": [{"var": "a"}, "b"]})

    json_logic_data = DataInput(
        data_id="data1",
        data_object={
            "a": "b",
        },
    )

    match = evaluate_single_json_logic_rule_against_single_data(
        json_logic_rule=json_logic_rule,
        json_logic_data=json_logic_data,
    )

    assert match is True


def test_evaluate_single_json_logic_rule_against_single_data_no_match():
    json_logic_rule = RuleInput(rule_id="rule1", rule_tree={">": [{"var": "a"}, 3]})

    json_logic_data = DataInput(
        data_id="data1",
        data_object={
            "a": 3,
        },
    )

    match = evaluate_single_json_logic_rule_against_single_data(
        json_logic_rule=json_logic_rule,
        json_logic_data=json_logic_data,
    )

    assert match is False
