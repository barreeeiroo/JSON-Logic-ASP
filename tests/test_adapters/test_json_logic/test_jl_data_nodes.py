import pytest

from json_logic_asp.adapters.json_logic.jl_data_nodes import DataVarNode


class TestDataVarNode:
    def test_invalid_value(self):
        with pytest.raises(ValueError):
            DataVarNode(123)

        with pytest.raises(ValueError):
            DataVarNode(["var_name"])

    def test_valid_value(self):
        node = DataVarNode("var_name")
        assert isinstance(node, DataVarNode)

    def test_atom_generation(self):
        atom = DataVarNode("var_name").get_asp_atom()
        assert atom.to_asp_atom() == "var(s86536e21993c5a96a4d4c9c9afcc9b17, V)"

    def test_no_statements(self):
        node = DataVarNode("var_name")
        assert node.get_asp_statements() == []

    def test_str_repr(self):
        node = DataVarNode("var_name")
        assert str(node) == "VAR(var_name)"

    def test_hash(self):
        node1 = DataVarNode("var_name")
        node2 = DataVarNode("var_name")
        node3 = DataVarNode("var_name_diff")

        assert hash(node1) == hash(node2) != hash(node3)
