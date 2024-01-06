from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple, Type, final

from json_logic_asp.adapters.asp.asp_literals import PredicateAtom
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.utils.id_management import generate_unique_id


class JsonLogicNode(ABC):
    def __init__(
        self, operation_name: str, accepted_child_node_types: Tuple[Type, ...], allow_duplicated_children: bool = False
    ):
        self.operation_name: str = operation_name
        self.__accepted_child_node_types = accepted_child_node_types
        self.__allow_duplicated_children = allow_duplicated_children

        self.node_id: str = generate_unique_id()
        self.child_nodes: List[Any] = []

    @final
    def register_child(self, child_node: Any):
        if child_node in self.child_nodes and not self.__allow_duplicated_children:
            return

        if not isinstance(child_node, self.__accepted_child_node_types):
            t = type(child_node).__name__
            c = self.__class__.__name__
            raise ValueError(f"Found unexpected child_node type {t} for {c}")

        self.child_nodes.append(child_node)

    @abstractmethod
    def get_asp_atom(self) -> PredicateAtom:
        raise NotImplementedError()  # pragma: no cover

    @final
    def get_negated_asp_atom(self) -> PredicateAtom:
        atom = self.get_asp_atom()
        return PredicateAtom(
            predicate_name=atom.predicate_name,
            terms=atom.terms,
            negated=not atom.negated,
        )

    @abstractmethod
    def get_asp_statements(self) -> List[Statement]:
        raise NotImplementedError()  # pragma: no cover

    @final
    def to_asp(self, with_comment: bool = False) -> List[str]:
        stmts: List[str] = []

        for child_node in self.child_nodes:
            if not isinstance(child_node, JsonLogicNode):
                continue
            stmts.extend(child_node.to_asp(with_comment=with_comment))

        for statement in self.get_asp_statements():
            if with_comment and statement.to_asp_comment():
                stmts.append(statement.to_asp_comment())
            stmts.append(statement.to_asp_statement())

        return stmts

    def _get_children_hash(self, sort: bool = True):
        child_hashes = [hash(child) for child in self.child_nodes]
        child_hashes = sorted(child_hashes) if sort else child_hashes
        return hash(tuple(child_hashes))

    @abstractmethod
    def __str__(self):
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError()  # pragma: no cover

    @final
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return hash(self) == hash(other)


class JsonLogicTreeNode(JsonLogicNode, ABC):
    def __init__(
        self,
        operation_name: str,
        accepted_child_node_types: Optional[Tuple[Type, ...]] = None,
        allow_duplicated_children: bool = False,
    ):
        if accepted_child_node_types is None:
            accepted_child_node_types = (
                JsonLogicTreeNode,
                JsonLogicOperationNode,
            )
        super().__init__(
            operation_name=operation_name,
            accepted_child_node_types=accepted_child_node_types,
            allow_duplicated_children=allow_duplicated_children,
        )

    @final
    def get_asp_atom(self) -> PredicateAtom:
        return PredicateAtom(
            predicate_name=self.operation_name,
            terms=[self.node_id],
        )

    def __str__(self):
        return f"{self.operation_name.upper()}({self.node_id})"

    def __hash__(self):
        return hash(
            (
                self.operation_name,
                self._get_children_hash(),
            )
        )


class JsonLogicOperationNode(JsonLogicNode, ABC):
    def __init__(self, operation_name: str, accepted_child_node_types: Optional[Tuple[Type, ...]] = None):
        if accepted_child_node_types is None:
            accepted_child_node_types = (JsonLogicDataNode,)
        super().__init__(operation_name=operation_name, accepted_child_node_types=accepted_child_node_types)

    def get_asp_atom(self) -> PredicateAtom:
        return PredicateAtom(
            predicate_name=self.operation_name,
            terms=[self.node_id],
        )


class JsonLogicDataNode(JsonLogicOperationNode, ABC):
    def __init__(
        self, term_variable_name: str, operation_name: str, accepted_child_node_types: Optional[Tuple[Type, ...]] = None
    ):
        if accepted_child_node_types is None:
            accepted_child_node_types = ()
        super().__init__(operation_name=operation_name, accepted_child_node_types=accepted_child_node_types)
        self.term_variable_name = term_variable_name

    def get_asp_atom(self) -> PredicateAtom:
        return PredicateAtom(
            predicate_name=self.operation_name,
            terms=[self.node_id, self.term_variable_name],
        )

    @final
    def get_asp_atom_with_different_variable_name(self, var_name: str, negated: bool = False) -> PredicateAtom:
        atom = self.get_asp_atom()
        return PredicateAtom(
            predicate_name=atom.predicate_name,
            terms=[
                atom.terms[0],
                var_name,
            ],
            negated=negated,
        )


class JsonLogicSingleDataNode(JsonLogicDataNode, ABC):
    def __init__(
        self, term_variable_name: str, operation_name: str, accepted_child_node_types: Optional[Tuple[Type, ...]] = None
    ):
        super().__init__(
            term_variable_name=term_variable_name,
            operation_name=operation_name,
            accepted_child_node_types=accepted_child_node_types,
        )


class JsonLogicMultiDataNode(JsonLogicDataNode, ABC):
    def __init__(
        self, term_variable_name: str, operation_name: str, accepted_child_node_types: Optional[Tuple[Type, ...]] = None
    ):
        super().__init__(
            term_variable_name=term_variable_name,
            operation_name=operation_name,
            accepted_child_node_types=accepted_child_node_types,
        )
