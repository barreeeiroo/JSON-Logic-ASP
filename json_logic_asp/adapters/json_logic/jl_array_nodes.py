from typing import Any, List, Union

from json_logic_asp.adapters.asp.asp_literals import ComparatorAtom, Literal
from json_logic_asp.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataVarNode
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import (
    JsonLogicDataNode,
    JsonLogicMultiDataNode,
    JsonLogicNode,
    JsonLogicOperationNode,
    JsonLogicSingleDataNode,
)
from json_logic_asp.utils.json_logic_helpers import value_encoder


class ArrayMergeNode(JsonLogicMultiDataNode):
    def __init__(self, node_value: Any):
        super().__init__(term_variable_name="M", operation_name="merge")

        if not isinstance(node_value, list):
            raise ValueError(f"ArrayMergeNode requires list as value, received {type(node_value)}")

        self.__child_nodes: List[Union[JsonLogicDataNode, int, float, bool, str]] = []

        for values in node_value:
            if not isinstance(values, list):
                values = [values]

            for value in values:
                if not isinstance(value, (JsonLogicDataNode, int, float, bool, str)):
                    raise ValueError(f"ArrayMergeNode received unexpected node type {type(value)}")
                self.__child_nodes.append(value)

        for child_node in self.__child_nodes:
            if not isinstance(child_node, JsonLogicNode) or isinstance(child_node, DataVarNode):
                continue
            self.add_child(child_node)

    def get_asp_statements(self) -> List[Statement]:
        stmts: List[Statement] = []

        primitives = [v for v in self.__child_nodes if not isinstance(v, JsonLogicDataNode)]
        var_nodes = [v for v in self.__child_nodes if isinstance(v, JsonLogicDataNode)]

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
                        left_value="M",
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
            ("merge", tuple(sorted([hash(val) for val in self.__child_nodes]))),
        )


class ArrayInNode(JsonLogicOperationNode):
    def __init__(self, node_value: Any):
        super().__init__(operation_name="in")

        if not isinstance(node_value, list):
            raise ValueError(f"ArrayInNode expects a list as child, received {type(node_value)}")

        if len(node_value) != 2:
            raise ValueError(f"ArrayInNode expects 2 children, received {len(node_value)}")

        left, right = node_value

        if not isinstance(left, JsonLogicSingleDataNode) and not isinstance(right, JsonLogicSingleDataNode):
            raise ValueError("ArrayInNode expects at least 1 JsonLogicSingleDataNode, received 0")

        self.data_nodes: List[JsonLogicSingleDataNode] = []
        self.list_node: Union[List, JsonLogicMultiDataNode]

        if isinstance(left, (list, JsonLogicMultiDataNode)):
            self.list_node = left
        else:
            self.data_nodes.append(left)

        if isinstance(right, (list, JsonLogicMultiDataNode)):
            self.list_node = right
        else:
            self.data_nodes.append(right)

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
                    raise ValueError(f"ArrayInNode expects at least 1 list primitive nodes, received {type(list_elem)}")

        for node in node_value:
            if not isinstance(node, JsonLogicNode) or isinstance(node, DataVarNode):
                continue
            self.add_child(node)

    def get_asp_statements(self) -> List[Statement]:
        literals: List[Literal] = []

        def get_comment_var_name(node: JsonLogicSingleDataNode):
            return node.var_name if isinstance(node, DataVarNode) else str(node)

        if len(self.data_nodes) == 2:
            literals.extend([node.get_asp_atom_with_different_variable_name("I") for node in self.data_nodes])
            comment = " IN ".join([get_comment_var_name(node) for node in self.data_nodes])

        else:
            data_node = self.data_nodes[0]
            list_node = self.list_node
            var_name = get_comment_var_name(data_node)

            literals.append(data_node.get_asp_atom_with_different_variable_name("I"))
            if isinstance(list_node, list):
                right_val = [value_encoder(val) for val in list_node]
                literals.append(
                    ComparatorAtom(
                        left_value="I",
                        comparator="=",
                        right_value=f"({';'.join(right_val)})",
                    )
                )
                comment = f"{var_name} IN ({', '.join([str(stmt) for stmt in list_node])})"
            else:
                literals.append(list_node.get_asp_atom_with_different_variable_name("I"))
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
                "in",
                *tuple(sorted([hash(node) for node in self.data_nodes])),
                *(
                    [hash(self.list_node)]
                    if isinstance(self.list_node, JsonLogicMultiDataNode)
                    else sorted(self.list_node)
                ),
            ),
        )
