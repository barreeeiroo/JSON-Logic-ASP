from json_logic_asp.translator.rule_generator import generate_multiple_rule_asp_definition
from json_logic_asp.translator.data_generator import generate_single_data_asp_definition
from json_logic_asp.translator.models.translator import RuleInput, DataInput


def test_rule_usage():
    result = generate_multiple_rule_asp_definition(
        rules=[
            RuleInput(
                rule_id="rule1",
                rule_tree={"and": [
                    {"==": [{"var": "a"}, "abc"]},
                    {"==": [{"var": "b"}, "dce"]},
                    {"or": [
                        {"!": {"==": [{"var": "c"}, "efg"]}},
                        {"==": [{"var": "d"}, "xyz"]},
                    ]},
                    {"!": {"or": [
                        {"==": [{"var": "b"}, "dce"]},
                    ]}},
                    {"and": [
                        {"==": [{"var": "a"}, "abc"]},
                        {"or": [
                            {"==": [{"var": "b"}, "dce"]},
                        ]},
                    ]},
                ]},
            ),
            RuleInput(
                rule_id="rule2",
                rule_tree={"!": {"and": [
                    {"==": [{"var": "a"}, "abc"]},
                    {"==": [{"var": "a"}, "abc"]},
                ]}},
            ),
        ]
    )

    print(result)

    assert False


def test_in_usage():
    result = generate_multiple_rule_asp_definition(
        rules=[
            RuleInput(
                rule_id="rule1",
                rule_tree={"and": [
                    {"in": [{"var": "a"}, ["A", "B", "C"]]},
                    {"in": [{"var": "a"}, ["C", "A", "B"]]},
                ]},
            ),
        ]
    )

    print(result)

    assert False


def test_data_usage():
    result = generate_single_data_asp_definition(
        data_input=DataInput(data_id="data1", data_object={
            "dummy": "val",
            "nested": {
                "dummy2": "val2"
            }
        })
    )

    print(result)

    assert False
