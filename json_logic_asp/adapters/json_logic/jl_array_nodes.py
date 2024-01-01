from typing import List, Union

from json_logic_asp.adapters.asp.asp_literals import ComparatorAtom, Literal
from json_logic_asp.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataVarNode
from json_logic_asp.constants.asp_naming import PredicateNames, VariableNames
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import (
    JsonLogicDataNode,
    JsonLogicMultiDataNode,
    JsonLogicOperationNode,
    JsonLogicSingleDataNode,
)
from json_logic_asp.utils.json_logic_helpers import value_encoder


class ArrayMergeNode(JsonLogicMultiDataNode):
    def __init__(self, *children):
        super().__init__(
            accepted_child_node_types=(JsonLogicDataNode, int, float, bool, str),
            term_variable_name=VariableNames.MERGE,
            operation_name=PredicateNames.ARRAY_MERGE,
        )

        for values in children:
            if not isinstance(values, list):
                values = [values]

            for value in values:
                self.register_child(value)

    def get_asp_statements(self) -> List[Statement]:
        stmts: List[Statement] = []

        primitives = [v for v in self.child_nodes if not isinstance(v, JsonLogicDataNode)]
        var_nodes = [v for v in self.child_nodes if isinstance(v, JsonLogicDataNode)]

        for var_node in var_nodes:
            if isinstance(var_node, JsonLogicDataNode):
                var_name = var_node if isinstance(var_node, DataVarNode) else str(var_node)
                stmts.append(
                    RuleStatement(
                        atom=self.get_asp_atom(),
                        literals=[var_node.get_asp_atom_with_different_variable_name(self.term_variable_name)],
                        comment=f"Merge {var_name}",
                    )
                )

        stmts.append(
            RuleStatement(
                atom=self.get_asp_atom(),
                literals=[
                    ComparatorAtom(
                        left_value=VariableNames.MERGE,
                        comparator="=",
                        right_value=f"({';'.join([value_encoder(val) for val in primitives])})",
                    )
                ],
                comment=f"Merge ({', '.join([str(stmt) for stmt in primitives])})",
            )
        )

        return stmts

    def __str__(self):
        return f"MERGE({self.node_id})"

    def __hash__(self):
        return hash(
            (PredicateNames.ARRAY_MERGE, tuple(sorted([hash(val) for val in self.child_nodes]))),
        )


class ArrayInNode(JsonLogicOperationNode):
    def __init__(self, *children):
        super().__init__(operation_name=PredicateNames.ARRAY_IN, accepted_child_node_types=(JsonLogicDataNode, list))

        if len(children) != 2:
            raise ValueError(f"ArrayInNode expects 2 children, received {len(children)}")

        left, right = children

        if not isinstance(left, JsonLogicSingleDataNode) and not isinstance(right, JsonLogicSingleDataNode):
            raise ValueError("ArrayInNode expects at least 1 JsonLogicSingleDataNode")
        list_types = (list, JsonLogicMultiDataNode)
        if not isinstance(left, list_types) and not isinstance(right, list_types):
            raise ValueError("ArrayInNode expects at least 1 JsonLogicMultiDataNode or list")

        self.data_node: Union[JsonLogicSingleDataNode]
        self.list_node: Union[List, JsonLogicMultiDataNode]

        if isinstance(left, (list, JsonLogicMultiDataNode)):
            self.list_node = left
        else:
            self.data_node = left

        if isinstance(right, (list, JsonLogicMultiDataNode)):
            self.list_node = right
        else:
            self.data_node = right

        if self.list_node and isinstance(self.list_node, list):
            for list_elem in self.list_node:
                if not isinstance(
                    list_elem,
                    (
                        str,
                        bool,
                        float,
                        int,
                    ),
                ):
                    t = type(list_elem).__name__
                    raise ValueError(f"ArrayInNode expects at least 1 list primitive nodes, received {t}")

        for node in children:
            self.register_child(node)

    def get_asp_statements(self) -> List[Statement]:
        literals: List[Literal] = []

        def get_comment_var_name(node: JsonLogicSingleDataNode):
            return node.var_name if isinstance(node, DataVarNode) else str(node)

        data_node = self.data_node
        list_node = self.list_node
        var_name = get_comment_var_name(data_node)

        literals.append(data_node.get_asp_atom_with_different_variable_name(VariableNames.IN))
        if isinstance(list_node, list):
            right_val = [value_encoder(val) for val in list_node]
            literals.append(
                ComparatorAtom(
                    left_value=VariableNames.IN,
                    comparator="=",
                    right_value=f"({';'.join(right_val)})",
                )
            )
            comment = f"{var_name} IN ({', '.join([str(stmt) for stmt in list_node])})"
        else:
            literals.append(list_node.get_asp_atom_with_different_variable_name(VariableNames.IN))
            comment = f"{var_name} IN ({str(list_node)})"

        return [
            RuleStatement(
                atom=self.get_asp_atom(),
                literals=literals,
                comment=comment,
            )
        ]

    def __str__(self):
        return f"IN({self.node_id})"

    def __hash__(self):
        return hash(
            (
                PredicateNames.ARRAY_IN,
                hash(self.data_node),
                hash(self.list_node)
                if isinstance(self.list_node, JsonLogicMultiDataNode)
                else hash(tuple(sorted(self.list_node))),
            ),
        )
