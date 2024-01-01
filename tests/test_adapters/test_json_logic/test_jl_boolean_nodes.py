import pytest

from json_logic_asp.adapters.json_logic.jl_boolean_nodes import BooleanAndNode, BooleanNotNode, BooleanOrNode
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataVarNode
from json_logic_asp.adapters.json_logic.jl_logic_nodes import LogicEqualNode


class TestBooleanAndNode:
    def test_invalid_values(self):
        with pytest.raises(ValueError) as exc1:
            BooleanAndNode()
        assert exc1.match("BooleanAndNode requires at least 1 child")

        with pytest.raises(ValueError) as exc2:
            BooleanAndNode("a")
        assert exc2.match("Found unexpected child_node type str for BooleanAndNode")

    def test_valid_values(self):
        node = BooleanAndNode(True)
        assert isinstance(node, BooleanAndNode) and not node.has_false

        node = BooleanAndNode(False)
        assert isinstance(node, BooleanAndNode) and node.has_false

    def test_statements(self):
        eq1 = LogicEqualNode("a", "b")
        eq2 = LogicEqualNode("c", "d")
        node = BooleanAndNode(eq1, eq2)

        assert node.to_asp(with_comment=True) == [
            "% a EQ b",
            "eq(mock1) :- s0cc175b9c0f1b6a831c399e269772661 == s92eb5ffee6ae2fec3ad71c777531578f.",
            "% c EQ d",
            "eq(mock2) :- s4a8a08f09d37b73795649038408b5f33 == s8277e0910d750195b448797616e091ad.",
            "and(mock3) :- eq(mock1), eq(mock2).",
        ]

    def test_statements_true(self):
        eq1 = LogicEqualNode("a", "b")
        eq2 = LogicEqualNode("c", "d")
        node = BooleanAndNode(eq1, True, eq2)

        assert node.to_asp(with_comment=True) == [
            "% a EQ b",
            "eq(mock1) :- s0cc175b9c0f1b6a831c399e269772661 == s92eb5ffee6ae2fec3ad71c777531578f.",
            "% c EQ d",
            "eq(mock2) :- s4a8a08f09d37b73795649038408b5f33 == s8277e0910d750195b448797616e091ad.",
            "and(mock3) :- eq(mock1), eq(mock2).",
        ]

    def test_statements_false(self):
        eq1 = LogicEqualNode("a", "b")
        eq2 = LogicEqualNode("c", "d")
        node = BooleanAndNode(eq1, False, eq2)

        assert node.to_asp(with_comment=True) == [
            "% a EQ b",
            "eq(mock1) :- s0cc175b9c0f1b6a831c399e269772661 == s92eb5ffee6ae2fec3ad71c777531578f.",
            "% c EQ d",
            "eq(mock2) :- s4a8a08f09d37b73795649038408b5f33 == s8277e0910d750195b448797616e091ad.",
        ]

    def test_statements_empty_true(self):
        node = BooleanAndNode(True, True)

        assert node.to_asp(with_comment=True) == ["and(mock1)."]

    def test_statements_empty_false(self):
        node = BooleanAndNode(False, False)

        assert node.to_asp(with_comment=True) == []

    def test_statements_empty_mix(self):
        node = BooleanAndNode(True, False)

        assert node.to_asp(with_comment=True) == []

    def test_str(self):
        node = BooleanAndNode(True)
        assert str(node) == "AND(mock1)"

    def test_hash(self):
        eq1 = LogicEqualNode("a", "b")
        eq1b = LogicEqualNode("b", "a")
        eq2 = LogicEqualNode("c", "d")
        eq3 = LogicEqualNode("e", "f")
        node1 = BooleanAndNode(eq1, eq2)
        node2 = BooleanAndNode(eq2, eq1b, eq1)
        node3 = BooleanAndNode(eq2, eq1, eq3)

        assert hash(node1) == hash(("and", hash(tuple(sorted([hash(eq1), hash(eq2)]))))) == hash(node2) != hash(node3)
        assert node1 == node2 != node3


class TestBooleanOrNode:
    def test_invalid_values(self):
        with pytest.raises(ValueError) as exc1:
            BooleanOrNode()
        assert exc1.match("BooleanOrNode requires at least 1 child")

        with pytest.raises(ValueError) as exc2:
            BooleanOrNode("a")
        assert exc2.match("Found unexpected child_node type str for BooleanOrNode")

    def test_valid_values(self):
        node = BooleanOrNode(True)
        assert isinstance(node, BooleanOrNode) and node.has_true

        node = BooleanOrNode(False)
        assert isinstance(node, BooleanOrNode) and not node.has_true

    def test_statements(self):
        eq1 = LogicEqualNode("a", "b")
        eq2 = LogicEqualNode("c", "d")
        node = BooleanOrNode(eq1, eq2)

        assert node.to_asp(with_comment=True) == [
            "% a EQ b",
            "eq(mock1) :- s0cc175b9c0f1b6a831c399e269772661 == s92eb5ffee6ae2fec3ad71c777531578f.",
            "% c EQ d",
            "eq(mock2) :- s4a8a08f09d37b73795649038408b5f33 == s8277e0910d750195b448797616e091ad.",
            "or(mock3) :- eq(mock1).",
            "or(mock3) :- eq(mock2).",
        ]

    def test_statements_true(self):
        eq1 = LogicEqualNode("a", "b")
        eq2 = LogicEqualNode("c", "d")
        node = BooleanOrNode(eq1, True, eq2)

        assert node.to_asp(with_comment=True) == [
            "% a EQ b",
            "eq(mock1) :- s0cc175b9c0f1b6a831c399e269772661 == s92eb5ffee6ae2fec3ad71c777531578f.",
            "% c EQ d",
            "eq(mock2) :- s4a8a08f09d37b73795649038408b5f33 == s8277e0910d750195b448797616e091ad.",
            "or(mock3).",
        ]

    def test_statements_false(self):
        eq1 = LogicEqualNode("a", "b")
        eq2 = LogicEqualNode("c", "d")
        node = BooleanOrNode(eq1, False, eq2)

        assert node.to_asp(with_comment=True) == [
            "% a EQ b",
            "eq(mock1) :- s0cc175b9c0f1b6a831c399e269772661 == s92eb5ffee6ae2fec3ad71c777531578f.",
            "% c EQ d",
            "eq(mock2) :- s4a8a08f09d37b73795649038408b5f33 == s8277e0910d750195b448797616e091ad.",
            "or(mock3) :- eq(mock1).",
            "or(mock3) :- eq(mock2).",
        ]

    def test_statements_empty_true(self):
        node = BooleanOrNode(True, True)

        assert node.to_asp(with_comment=True) == ["or(mock1)."]

    def test_statements_empty_false(self):
        node = BooleanOrNode(False, False)

        assert node.to_asp(with_comment=True) == []

    def test_statements_empty_mix(self):
        node = BooleanOrNode(True, False)

        assert node.to_asp(with_comment=True) == ["or(mock1)."]

    def test_str(self):
        node = BooleanOrNode(True)
        assert str(node) == "OR(mock1)"

    def test_hash(self):
        eq1 = LogicEqualNode("a", "b")
        eq1b = LogicEqualNode("b", "a")
        eq2 = LogicEqualNode("c", "d")
        eq3 = LogicEqualNode("e", "f")
        node1 = BooleanOrNode(eq1, eq2)
        node2 = BooleanOrNode(eq2, eq1b, eq1)
        node3 = BooleanOrNode(eq2, eq1, eq3)

        assert hash(node1) == hash(("or", hash(tuple(sorted([hash(eq1), hash(eq2)]))))) == hash(node2) != hash(node3)
        assert node1 == node2 != node3


class TestBooleanNotNode:
    def test_invalid_values(self):
        with pytest.raises(ValueError) as exc1:
            BooleanNotNode()
        assert exc1.match("BooleanNotNode expects only 1 child, received 0")

        with pytest.raises(ValueError) as exc2:
            BooleanNotNode("a", "b")
        assert exc2.match("BooleanNotNode expects only 1 child, received 2")

    def test_valid_values(self):
        data_var = DataVarNode("data_var")
        node = BooleanNotNode(data_var)
        assert isinstance(node, BooleanNotNode)

    def test_statements_data_node(self):
        data_var = DataVarNode("data_var")
        node = BooleanNotNode(data_var)

        assert node.to_asp(with_comment=True) == [
            "% Not data_var",
            "neg(mock2) :- not var(s38bb977078c0e5ba5b0b759cf506cc4c, _).",
        ]

    def test_statements_tree_nodes(self):
        and_node = BooleanAndNode(True)
        node = BooleanNotNode(and_node)

        assert node.to_asp(with_comment=True) == [
            "and(mock1).",
            "neg(mock2) :- not and(mock1).",
        ]

    def test_str(self):
        data_var = DataVarNode("data_var")
        node = BooleanNotNode(data_var)
        assert str(node) == "NEG(mock2)"

    def test_hash(self):
        dv1 = DataVarNode("data_var1")
        dv2 = DataVarNode("data_var2")
        node1 = BooleanNotNode(dv1)
        node2 = BooleanNotNode(dv1)
        node3 = BooleanNotNode(dv2)

        assert hash(node1) == hash(("neg", hash((hash(dv1),)))) == hash(node2) != hash(node3)
        assert node1 == node2 != node3
