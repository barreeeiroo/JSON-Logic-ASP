from abc import ABC
from typing import Dict, List, Optional

from json_logic_asp.adapters.asp.asp_literals import PredicateAtom
from json_logic_asp.adapters.asp.asp_statements import FactStatement, RuleStatement
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataVarNode
from json_logic_asp.constants.asp_naming import PredicateNames, VariableNames
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import JsonLogicDataNode, JsonLogicTreeNode


class BooleanAndOrNode(JsonLogicTreeNode, ABC):
    def __init__(self, *children, operation_name: str):
        super().__init__(operation_name=operation_name)

        if len(children) < 1:
            raise ValueError(f"{self.__class__.__name__} requires at least 1 child")

        self.has_true: bool = False
        self.has_false: bool = False

        for child_node in children:
            if isinstance(child_node, bool):
                self.has_false = self.has_false or child_node is False
                self.has_true = self.has_true or child_node is True
                continue

            self.register_child(child_node)


class BooleanAndNode(BooleanAndOrNode):
    def __init__(self, *children):
        super().__init__(operation_name=PredicateNames.BOOLEAN_AND, *children)

    def get_asp_statements(self) -> List[Statement]:
        if self.has_false:
            # If the condition can never be satisfied, return no statements (never satisfy the node)
            return []

        if self.has_true and not self.child_nodes:
            # If any True present but no other children, then it's just a fact
            return [
                FactStatement(
                    atom=self.get_asp_atom(),
                )
            ]

        # For each child node, get the atom and use it as literal
        child_statements: Dict[str, PredicateAtom] = {}
        for child_node in self.child_nodes:
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

        if not self.child_nodes:
            return []

        stmts: List[Statement] = []

        for child_node in self.child_nodes:
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
