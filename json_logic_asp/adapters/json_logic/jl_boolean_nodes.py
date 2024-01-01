from abc import ABC
from typing import Dict, List, Optional

from json_logic_asp.adapters.asp.asp_literals import PredicateAtom
from json_logic_asp.adapters.asp.asp_statements import FactStatement, RuleStatement
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataVarNode
from json_logic_asp.constants.asp_naming import PredicateNames, VariableNames
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import (
    JsonLogicDataNode,
    JsonLogicNode,
    JsonLogicOperationNode,
    JsonLogicTreeNode,
)


class BooleanAndOrNode(JsonLogicTreeNode, ABC):
    def __init__(self, *children, operation_name: str):
        super().__init__(
            operation_name=operation_name,
            accepted_child_node_types=(
                JsonLogicTreeNode,
                JsonLogicOperationNode,
                bool,
            ),
        )

        if len(children) < 1:
            raise ValueError(f"{self.__class__.__name__} requires at least 1 child")

        for child_node in children:
            self.register_child(child_node)

    @property
    def has_true(self) -> bool:
        return any(child_node is True for child_node in self.child_nodes)

    @property
    def has_false(self) -> bool:
        return any(child_node is False for child_node in self.child_nodes)

    @property
    def has_non_bool_nodes(self) -> bool:
        return any(not isinstance(child_node, bool) for child_node in self.child_nodes)


class BooleanAndNode(BooleanAndOrNode):
    def __init__(self, *children):
        super().__init__(operation_name=PredicateNames.BOOLEAN_AND, *children)

    def get_asp_statements(self) -> List[Statement]:
        if self.has_false:
            # If the condition can never be satisfied, return no statements (never satisfy the node)
            return []

        if self.has_true and not self.has_non_bool_nodes:
            # If any True present but no other children, then it's just a fact
            return [
                FactStatement(
                    atom=self.get_asp_atom(),
                )
            ]

        # For each child node, get the atom and use it as literal
        child_statements: Dict[str, PredicateAtom] = {}
        for child_node in self.child_nodes:
            if not isinstance(child_node, JsonLogicNode):
                continue
            child_statements[child_node.node_id] = child_node.get_asp_atom()

        return [
            RuleStatement(
                atom=self.get_asp_atom(),
                literals=list(child_statements.values()),
            )
        ]


class BooleanOrNode(BooleanAndOrNode):
    def __init__(self, *children):
        super().__init__(operation_name=PredicateNames.BOOLEAN_OR, *children)

    def get_asp_statements(self) -> List[Statement]:
        if self.has_true:
            return [
                FactStatement(
                    atom=self.get_asp_atom(),
                )
            ]

        if not self.has_non_bool_nodes:
            return []

        stmts: List[Statement] = []

        for child_node in self.child_nodes:
            if not isinstance(child_node, JsonLogicNode):
                continue
            statement = RuleStatement(
                atom=self.get_asp_atom(),
                literals=[child_node.get_asp_atom()],
            )
            stmts.append(statement)

        return stmts


class BooleanNotNode(JsonLogicTreeNode):
    def __init__(self, *children):
        super().__init__(operation_name=PredicateNames.BOOLEAN_NOT)

        if len(children) != 1:
            raise ValueError(f"BooleanNotNode expects only 1 child, received {len(children)}")

        self.register_child(children[0])

    def get_asp_statements(self) -> List[Statement]:
        # For each child node, get the atom and use it as literal
        child_statements: Dict[str, PredicateAtom] = {}
        comment: Optional[str] = None

        child_node = self.child_nodes[0]

        if isinstance(child_node, JsonLogicDataNode):
            # Handle specific case for negating "var" nodes as "not present"
            var_name = child_node.var_name if isinstance(child_node, DataVarNode) else str(child_node)
            child_statements[child_node.node_id] = child_node.get_asp_atom_with_different_variable_name(
                VariableNames.ANY, negated=True
            )
            comment = f"Not {var_name}"
        else:
            child_atom = child_node.get_asp_atom()
            child_statements[child_node.node_id] = PredicateAtom(
                predicate_name=child_atom.predicate_name,
                terms=child_atom.terms,
                negated=not child_atom.negated,
            )

        return [
            RuleStatement(
                atom=PredicateAtom(predicate_name=PredicateNames.BOOLEAN_NOT, terms=[self.node_id]),
                literals=list(child_statements.values()),
                comment=comment,
            )
        ]
