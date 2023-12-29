from json_logic_asp.models.translator_dto import DataInput, DataOutput, RuleInput, RuleOutput
from tests.fixtures import cuid_fixture  # noqa


def test_rule_input():
    rule_input = RuleInput(rule_tree={"a": {"b": "c"}})
    assert rule_input.rule_tree == {"a": {"b": "c"}}
    assert rule_input.rule_id == "mock1"


def test_rule_input_with_custom_id():
    rule_input = RuleInput(
        rule_tree={"a": {"b": "c"}},
        rule_id="custom",
    )
    assert rule_input.rule_tree == {"a": {"b": "c"}}
    assert rule_input.rule_id == "custom"


def test_rule_output():
    output = RuleOutput(statements=["a", "b"], rule_mapping={"a": "c", "b": "d"})
    assert output.statements == ["a", "b"]
    assert output.rule_mapping == {"a": "c", "b": "d"}


def test_data_input():
    data_input = DataInput(data_object={"a": {"b": "c"}})
    assert data_input.data_object == {"a": {"b": "c"}}
    assert data_input.data_id == "mock1"


def test_data_input_with_custom_id():
    data_input = DataInput(
        data_object={"a": {"b": "c"}},
        data_id="custom",
    )
    assert data_input.data_object == {"a": {"b": "c"}}
    assert data_input.data_id == "custom"


def test_data_output():
    output = DataOutput(statements=["a", "b"], data_mapping={"a": "c", "b": "d"})
    assert output.statements == ["a", "b"]
    assert output.data_mapping == {"a": "c", "b": "d"}
