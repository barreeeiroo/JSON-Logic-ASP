import pytest

from json_logic_asp.adapters.json_logic.jl_helper_nodes import JsonLogicHelperBoolNode


class TestJsonLogicHelperBoolNode:
    def test_invalid_values(self):
        with pytest.raises(ValueError) as exc1:
            JsonLogicHelperBoolNode()
        assert exc1.match("JsonLogicHelperBoolNode accepts only 1 child")

        with pytest.raises(ValueError) as exc2:
            JsonLogicHelperBoolNode(True, False)
        assert exc2.match("JsonLogicHelperBoolNode accepts only 1 child")

        with pytest.raises(ValueError) as exc1:
            JsonLogicHelperBoolNode("a")
        assert exc1.match("JsonLogicHelperBoolNode accepts only bool child")

    def test_encoded_bool(self):
        node = JsonLogicHelperBoolNode(True)
        assert node.encoded_bool == "true"

        node = JsonLogicHelperBoolNode(False)
        assert node.encoded_bool == "false"

    def test_atom(self):
        node = JsonLogicHelperBoolNode(True)
        assert node.get_asp_atom().to_asp_atom() == "bool(true)"

        node = JsonLogicHelperBoolNode(False)
        assert node.get_asp_atom().to_asp_atom() == "bool(false)"

    def test_statements(self):
        node = JsonLogicHelperBoolNode(True)
        assert node.get_asp_statements() == []

        node = JsonLogicHelperBoolNode(False)
        assert node.get_asp_statements() == []

    def test_str(self):
        node = JsonLogicHelperBoolNode(True)
        assert str(node) == "BOOL(true)"

        node = JsonLogicHelperBoolNode(False)
        assert str(node) == "BOOL(false)"

    def test_hash(self):
        node = JsonLogicHelperBoolNode(True)
        assert hash(node) == hash(("bool", "mock1"))

        node = JsonLogicHelperBoolNode(False)
        assert hash(node) == hash(("bool", "mock2"))
