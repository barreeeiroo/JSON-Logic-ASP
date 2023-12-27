import pytest

from json_logic_asp.utils.json_logic_helpers import extract_key_and_value_from_node, value_encoder


def test_extract_key_and_value_from_node():
    key, value = extract_key_and_value_from_node({"and": [{"var": "a"}]})
    assert key == "and"
    assert value == [{"var": "a"}]


@pytest.mark.parametrize(
    "test_input, expected_output",
    [
        ("123", "s202cb962ac59075b964b07152d234b70"),
        (123, "123"),
        (123.4, "123"),
        (123.9, "123"),
        (True, "true"),
        (False, "false"),
        (None, "None"),
        (Exception, "<class 'Exception'>"),
        (Exception(), Exception().__str__()),
        (["a", "b"], "['a', 'b']"),
        (("a", "b"), "('a', 'b')"),
        ({"a": "b"}, "{'a': 'b'}"),
        ({"a", "b"}, "{'b', 'a'}"),
    ],
    ids=[
        "string",
        "int",
        "float_pre5",
        "float_post5",
        "bool_true",
        "bool_false",
        "none",
        "type",
        "object",
        "list",
        "tuple",
        "dict",
        "set",
    ],
)
def test_value_encoder(test_input, expected_output):
    assert value_encoder(test_input) == expected_output
