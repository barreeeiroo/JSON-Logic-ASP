import pytest

from json_logic_asp.adapters.json_logic.jl_data_nodes import DataMissingNode, DataVarNode


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


class TestDataMissingNode:
    def test_invalid_value(self):
        with pytest.raises(ValueError):
            DataMissingNode(123)

        with pytest.raises(ValueError):
            DataMissingNode(["var_name", 123])

    def test_valid_value(self):
        node1 = DataMissingNode("var_name")
        assert isinstance(node1, DataMissingNode)
        node2 = DataMissingNode(["var1", "var2"])
        assert isinstance(node2, DataMissingNode)

    def test_statements_single_var(self):
        node = DataMissingNode("var_name")
        stmts = node.to_asp()
        assert len(stmts) == 1
        assert stmts[0] == "missing(mock1) :- not var(s86536e21993c5a96a4d4c9c9afcc9b17, _)."

    def test_statements_multi_var(self):
        node = DataMissingNode(["var1", "var2"])
        stmts = node.to_asp()
        assert len(stmts) == 1
        assert (
            stmts[0] == "missing(mock1) :- not var(s6482a3f94854f5920ef720dbf7944d49, _), "
            "not var(s7eeee37ce4d5f1ce4d968ed8fdd9bcbb, _)."
        )

    def test_statements_single_var_comment(self):
        node = DataMissingNode("var_name")
        stmts = node.to_asp(with_comment=True)
        assert len(stmts) == 2
        assert stmts[0] == "% Missing var_name"
        assert stmts[1] == "missing(mock1) :- not var(s86536e21993c5a96a4d4c9c9afcc9b17, _)."

    def test_statements_multi_var_comment(self):
        node = DataMissingNode(["var1", "var2"])
        stmts = node.to_asp(with_comment=True)
        assert len(stmts) == 2
        assert stmts[0] == "% Missing var1 var2"
        assert (
            stmts[1] == "missing(mock1) :- not var(s6482a3f94854f5920ef720dbf7944d49, _), "
            "not var(s7eeee37ce4d5f1ce4d968ed8fdd9bcbb, _)."
        )

    def test_str_repr(self):
        node = DataMissingNode(["var1", "var2"])
        assert str(node) == "MISSING(var1,var2)"

    def test_hash(self):
        node1 = DataMissingNode("var_name")
        node2 = DataMissingNode("var_name")
        node3 = DataMissingNode("var_name_diff")

        assert hash(node1) == hash(node2) != hash(node3)
