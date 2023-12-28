from typing import List

import pytest

from json_logic_asp.adapters.asp.asp_literals import PredicateAtom
from json_logic_asp.adapters.asp.asp_statements import FactStatement, RuleStatement
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import (
    JsonLogicDataNode,
    JsonLogicMultiDataNode,
    JsonLogicNode,
    JsonLogicOperationNode,
    JsonLogicSingleDataNode,
    JsonLogicTreeNode,
)
from tests.fixtures import cuid_fixture  # noqa


class DummyJsonLogicNode(JsonLogicNode):
    def get_asp_atom(self) -> PredicateAtom:
        return PredicateAtom(
            predicate_name="test",
            terms=[self.node_id],
        )

    def get_asp_statements(self) -> List[Statement]:
        return [FactStatement(atom=self.get_asp_atom(), comment="Comment")]

    def __str__(self):
        return "NODE"

    def __hash__(self):
        return hash(self.operation_name)


class TestJsonLogicNode:
    def test_invalid_child(self):
        node = DummyJsonLogicNode(accepted_child_node_types=(str,), operation_name="name")
        with pytest.raises(ValueError) as exc:
            node.register_child(1)

        assert exc.match("Found unexpected child_node type int for DummyJsonLogicNode")

    def test_valid_child(self):
        node = DummyJsonLogicNode(accepted_child_node_types=(str,), operation_name="name")
        node.register_child("1")
        assert node.child_nodes == ["1"]

    def test_duplicated_child(self):
        node = DummyJsonLogicNode(accepted_child_node_types=(str,), operation_name="name")
        node.register_child("1")
        node.register_child("1")
        assert node.child_nodes == ["1"]

    def test_negated_atom(self):
        node = DummyJsonLogicNode(accepted_child_node_types=(str,), operation_name="name")
        atom = node.get_asp_atom()
        negated = node.get_negated_asp_atom()
        assert atom.negated != negated.negated

    def test_to_asp(self):
        node = DummyJsonLogicNode(accepted_child_node_types=(DummyJsonLogicNode,), operation_name="test1")
        asp = node.to_asp()
        assert asp == ["test(mock1)."]

    def test_to_asp_child(self):
        node = DummyJsonLogicNode(accepted_child_node_types=(DummyJsonLogicNode,), operation_name="test1")
        nested = DummyJsonLogicNode(accepted_child_node_types=(DummyJsonLogicNode,), operation_name="test2")
        node.register_child(nested)
        asp = node.to_asp()
        assert asp == ["test(mock2).", "test(mock1)."]

    def test_to_asp_child_no_jl_node(self):
        node = DummyJsonLogicNode(accepted_child_node_types=(str,), operation_name="test1")
        node.register_child("nested")
        asp = node.to_asp()
        assert asp == ["test(mock1)."]

    def test_to_asp_with_comment(self):
        node = DummyJsonLogicNode(accepted_child_node_types=(DummyJsonLogicNode,), operation_name="test1")
        asp = node.to_asp(with_comment=True)
        assert asp == ["% Comment", "test(mock1)."]

    def test_children_hash(self):
        node = DummyJsonLogicNode(accepted_child_node_types=(DummyJsonLogicNode,), operation_name="test1")
        nested = DummyJsonLogicNode(accepted_child_node_types=(DummyJsonLogicNode,), operation_name="test2")
        node.register_child(nested)

        assert node._get_children_hash() == hash((hash(nested),))

    def test_eq(self):
        node1 = DummyJsonLogicNode(accepted_child_node_types=(DummyJsonLogicNode,), operation_name="test1")
        node2 = DummyJsonLogicNode(accepted_child_node_types=(DummyJsonLogicNode,), operation_name="test2")
        node3 = DummyJsonLogicNode(accepted_child_node_types=(DummyJsonLogicNode,), operation_name="test1")

        assert hash(node1) == hash(node3) != hash(node2)
        assert node1 == node3 != node2


class DummyJsonLogicTreeNode(JsonLogicTreeNode):
    def get_asp_statements(self) -> List[Statement]:
        if not self.child_nodes:
            return [FactStatement(atom=self.get_asp_atom())]
        return [RuleStatement(atom=self.get_asp_atom(), literals=[child.get_asp_atom() for child in self.child_nodes])]


class TestJsonLogicTreeNode:
    def test_accepted_node_types(self):
        node = DummyJsonLogicTreeNode(operation_name="test")
        nested = DummyJsonLogicTreeNode(operation_name="test2")
        node.register_child(nested)

        with pytest.raises(ValueError):
            invalid = DummyJsonLogicNode(accepted_child_node_types=(), operation_name="test3")
            node.register_child(invalid)

        assert node.child_nodes == [nested]

    def test_asp_atom(self):
        node = DummyJsonLogicTreeNode(operation_name="test")
        assert node.get_asp_atom().to_asp_atom() == "test(mock1)"

    def test_to_asp(self):
        node = DummyJsonLogicTreeNode(operation_name="test")
        nested = DummyJsonLogicTreeNode(operation_name="test2")
        node.register_child(nested)

        assert node.to_asp() == ["test2(mock2).", "test(mock1) :- test2(mock2)."]

    def test_str(self):
        node = DummyJsonLogicTreeNode(operation_name="test")
        assert str(node) == "TEST(mock1)"

    def test_hash(self):
        node = DummyJsonLogicTreeNode(operation_name="test")
        nested = DummyJsonLogicTreeNode(operation_name="test2")
        node.register_child(nested)

        nested_hash = hash(("test", node._get_children_hash()))
        assert hash(node) == nested_hash


class DummyJsonLogicOperationNode(JsonLogicOperationNode):
    def get_asp_statements(self) -> List[Statement]:
        return [RuleStatement(atom=self.get_asp_atom(), literals=[child.get_asp_atom() for child in self.child_nodes])]

    def __str__(self):
        return "NODE"

    def __hash__(self):
        return hash(self.operation_name)


class DummyJsonLogicDataNode(JsonLogicDataNode):
    def get_asp_statements(self) -> List[Statement]:
        return [FactStatement(atom=self.get_asp_atom())]

    def __str__(self):
        return "NODE"

    def __hash__(self):
        return hash(self.operation_name)


class DummyJsonLogicSingleDataNode(JsonLogicSingleDataNode):
    def get_asp_statements(self) -> List[Statement]:
        return [FactStatement(atom=self.get_asp_atom())]

    def __str__(self):
        return "NODE"

    def __hash__(self):
        return hash(self.operation_name)


class DummyJsonLogicMultiDataNode(JsonLogicMultiDataNode):
    def get_asp_statements(self) -> List[Statement]:
        return [FactStatement(atom=self.get_asp_atom())]

    def __str__(self):
        return "NODE"

    def __hash__(self):
        return hash(self.operation_name)


class TestJsonLogicOperationNode:
    def test_accepted_node_types(self):
        node = DummyJsonLogicOperationNode(operation_name="test")
        nested = DummyJsonLogicDataNode(operation_name="test2", term_variable_name="T")
        node.register_child(nested)

        with pytest.raises(ValueError):
            node.register_child(DummyJsonLogicOperationNode(operation_name="test3"))
        with pytest.raises(ValueError):
            node.register_child(DummyJsonLogicTreeNode(operation_name="test4"))

        assert node.child_nodes == [nested]

    def test_asp_atom(self):
        node = DummyJsonLogicOperationNode(operation_name="test")
        assert node.get_asp_atom().to_asp_atom() == "test(mock1)"

    def test_to_asp(self):
        node = DummyJsonLogicOperationNode(operation_name="test")
        nested = DummyJsonLogicDataNode(operation_name="test2", term_variable_name="T")
        node.register_child(nested)

        assert node.to_asp() == ["test2(mock2, T).", "test(mock1) :- test2(mock2, T)."]


@pytest.mark.parametrize(
    "cls",
    [
        DummyJsonLogicDataNode,
        DummyJsonLogicSingleDataNode,
        DummyJsonLogicMultiDataNode,
    ],
    ids=[],
)
class TestJsonLogicDataNode:
    def test_accepted_node_types(self, cls):
        node = cls(operation_name="test", term_variable_name="T")

        with pytest.raises(ValueError):
            node.register_child(cls(operation_name="test2", term_variable_name="T"))
        with pytest.raises(ValueError):
            node.register_child(DummyJsonLogicOperationNode(operation_name="test3"))
        with pytest.raises(ValueError):
            node.register_child(DummyJsonLogicTreeNode(operation_name="test4"))
        with pytest.raises(ValueError):
            node.register_child("b")

        assert node.child_nodes == []

    def test_asp_atom(self, cls):
        node = cls(operation_name="test", term_variable_name="T")
        assert node.get_asp_atom().to_asp_atom() == "test(mock1, T)"

    def test_asp_atom_with_different_var_name(self, cls):
        node = cls(operation_name="test", term_variable_name="T")
        assert node.get_asp_atom_with_different_variable_name("V").to_asp_atom() == "test(mock1, V)"

    def test_to_asp(self, cls):
        node = cls(operation_name="test2", term_variable_name="T")
        assert node.to_asp() == ["test2(mock1, T)."]
