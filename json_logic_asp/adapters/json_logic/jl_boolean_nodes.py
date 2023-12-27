from typing import Any, Dict, List, Optional

from json_logic_asp.adapters.asp.asp_literals import PredicateAtom
from json_logic_asp.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataVarNode
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import JsonLogicDataNode, JsonLogicTreeNode


class BooleanAndNode(JsonLogicTreeNode):
    def __init__(self, child_nodes: List[Any]):
        super().__init__(operation_name="and")

        for child_node in child_nodes:
            self.add_child(child_node)

    def get_asp_statements(self) -> List[Statement]:
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


class BooleanOrNode(JsonLogicTreeNode):
    def __init__(self, child_nodes: List[Any]):
        super().__init__(operation_name="or")

        for child_node in child_nodes:
            self.add_child(child_node)

    def get_asp_statements(self) -> List[Statement]:
        stmts: List[Statement] = []

        for child_node in self.child_nodes:
            statement = RuleStatement(
                atom=self.get_asp_atom(),
                literals=[child_node.get_asp_atom()],
            )
            stmts.append(statement)

        return stmts


class BooleanNotNode(JsonLogicTreeNode):
    def __init__(self, child_nodes: List[Any]):
        super().__init__(operation_name="neg")

        if len(child_nodes) != 1:
            raise ValueError(f"BooleanNotNode expects only 1 child, received {len(child_nodes)}")

        self.add_child(child_nodes[0])

    def get_asp_statements(self) -> List[Statement]:
        # For each child node, get the atom and use it as literal
        child_statements: Dict[str, PredicateAtom] = {}
        comment: Optional[str] = None
        for child_node in self.child_nodes:
            if isinstance(child_node, JsonLogicDataNode):
                # Handle specific case for negating "var" nodes as "not present"
                var_name = child_node.var_name if isinstance(child_node, DataVarNode) else str(child_node)
                child_statements[child_node.node_id] = child_node.get_asp_atom_with_different_variable_name(
                    "_", negated=True
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
                atom=PredicateAtom(predicate_name="neg", terms=[self.node_id]),
                literals=list(child_statements.values()),
                comment=comment,
            )
        ]
