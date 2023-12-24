from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Tuple, Type, Union, final

from json_logic_asp.adapters.asp.asp_literals import PredicateAtom
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.utils.id_management import generate_unique_id


class JsonLogicNode(ABC):
    def __init__(self, operation_name: str, accepted_child_node_types: Tuple[Type, ...]):
        self.operation_name: str = operation_name
        self.__accepted_child_node_types = accepted_child_node_types

        self.node_id: str = generate_unique_id()
        self.child_nodes: List[Any] = []

    @final
    def add_child(self, child_node: Any):
        if child_node in self.child_nodes:
            return

        if not isinstance(child_node, self.__accepted_child_node_types):
            raise ValueError(f"Found unexpected child_node type {type(child_node)} for {self.__class__.__name__}")

        self.child_nodes.append(child_node)

    @abstractmethod
    def get_asp_atom(self) -> PredicateAtom:
        raise NotImplementedError()

    @abstractmethod
    def get_asp_statements(self) -> List[Statement]:
        raise NotImplementedError()

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

    def _get_children_hash(self):
        child_hashes = [hash(child) for child in self.child_nodes]
        return hash(tuple(sorted(child_hashes)))

    @abstractmethod
    def __str__(self):
        raise NotImplementedError()

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError()


class JsonLogicInnerNode(JsonLogicNode, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(
            accepted_child_node_types=(
                JsonLogicInnerNode,
                JsonLogicLeafNode,
            ),
            *args,
            **kwargs,
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


class JsonLogicLeafNode(JsonLogicNode, ABC):
    def __init__(self, allows_primitives: bool = False, allows_lists: bool = False, *args, **kwargs):
        allowed_types: List[Type] = [JsonLogicLeafNode]
        if allows_primitives:
            allowed_types.extend([str, int, float, bool])
        if allows_lists:
            allowed_types.extend([List[Union[str, int, float, bool]]])

        kwargs["accepted_child_node_types"] = tuple(allowed_types)

        super().__init__(*args, **kwargs)

    def get_asp_atom(self) -> PredicateAtom:
        return PredicateAtom(
            predicate_name=self.operation_name,
            terms=[self.node_id],
        )
