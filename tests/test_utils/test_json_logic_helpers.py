from json_logic_asp.utils.json_logic_helpers import extract_key_and_value_from_node


def test_extract_key_and_value_from_node():
    key, value = extract_key_and_value_from_node({"and": [{"var": "a"}]})
    assert key == "and"
    assert value == [{"var": "a"}]
