from unittest.mock import patch

from json_logic_asp.invoker import get_matching_rules_for_asp_rules_and_data, get_matching_rules_from_asp_problem
from json_logic_asp.invoker.run import __store_clingo_temp_file


def test_store_clingo_temp_file():
    fp = __store_clingo_temp_file("a\nb\nc")
    assert fp.exists() and fp.is_file()

    with open(fp) as f:
        data = f.read()

    assert data == "a\nb\nc\n"
    fp.unlink()


def test_get_matching_rules_from_asp_problem():
    rules = get_matching_rules_from_asp_problem("rule(a). rule(b). #show rule/1.")
    assert rules == ["a", "b"]


def test_get_matching_rules_from_asp_problem_mapping():
    rules = get_matching_rules_from_asp_problem("rule(a). rule(b). #show rule/1.", mapping={"a": "c", "b": "d"})
    assert rules == ["c", "d"]


def test_get_matching_rules_from_asp_problem_no_match():
    rules = get_matching_rules_from_asp_problem("rule(a). :- rule(a). #show rule/1.", mapping={"a": "c"})
    assert rules == []


@patch("json_logic_asp.invoker.run.get_matching_rules_from_asp_problem")
def test_get_matching_rules_for_asp_rules_and_data(mock_get_matching_rules_from_asp_problem):
    mock_get_matching_rules_from_asp_problem.return_value = ["b"]

    rules = get_matching_rules_for_asp_rules_and_data("var(a, b).", "rule(a).", mapping={"a": "b"})

    mock_get_matching_rules_from_asp_problem.assert_called_once_with(
        problem="var(a, b).\n\n\nrule(a).\n\n\n#show rule/1.",
        mapping={"a": "b"},
    )
    assert rules == ["b"]


def test_get_matching_rules_for_asp_rules_and_data_real():
    rules = get_matching_rules_for_asp_rules_and_data("var(a, b).", "rule(a) :- var(a, _).", mapping={"a": "b"})

    assert rules == ["b"]
