from typing import Any, List, Union, Dict, Type, Optional, Tuple

from json_logic_asp.adapters.asp.asp_literals import ComparatorAtom, Literal, PredicateAtom
from json_logic_asp.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataVarNode
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import JsonLogicOperationNode
from json_logic_asp.utils.json_logic_helpers import value_encoder


class ArrayMergeNode(JsonLogicOperationNode):
    def __init__(self, node_value: Any):
        super().__init__(operation_name="merge")

        if not isinstance(node_value, list):
            raise ValueError(f"ArrayMergeNode requires list as value, received {type(node_value)}")

        self.__child_nodes: Dict[Type, List[Union[DataVarNode, int, float, bool, str]]] = {
            DataVarNode: [],
            int: [],
            float: [],
            bool: [],
            str: [],
        }

        actual_values: List[Union[DataVarNode, int, float, bool, str]] = []

        for value in node_value:
            if isinstance(value, list):
                actual_values.extend(value)
            else:
                actual_values.append(value)

        for value in actual_values:
            t = type(value)
            if t in self.__child_nodes:
                self.__child_nodes[t].append(value)
            else:
                raise ValueError(f"ArrayMergeNode received unexpected node type {t}")

        self.var_variable = "M"

    def get_asp_atom(self) -> PredicateAtom:
        return PredicateAtom(
            predicate_name="merge",
            terms=[self.node_id, self.var_variable],
        )

    def get_asp_atom_with_different_variable_name(self, var_name: str):
        atom = self.get_asp_atom()
        return PredicateAtom(
            predicate_name=atom.predicate_name,
            terms=[
                atom.terms[0],
                var_name,
            ],
        )

    def get_asp_statements(self) -> List[Statement]:
        stmts = []

        for var_node in self.__child_nodes[DataVarNode]:
            stmts.append(
                RuleStatement(
                    atom=self.get_asp_atom(),
                    literals=[var_node.get_asp_atom_with_different_variable_name(self.var_variable)],
                    comment=f"Merge {var_node.var_name}"
                )
            )

        for list_type, list_values in self.__child_nodes.items():
            if list_type == DataVarNode:
                continue
            if not list_values:
                continue

            stmts.append(
                RuleStatement(
                    atom=self.get_asp_atom(),
                    literals=[
                        ComparatorAtom(
                            left_value="M",
                            comparator="=",
                            right_value=f"({';'.join([value_encoder(val) for val in list_values])})",
                        )
                    ],
                    comment=f"Merge ({', '.join([str(stmt) for stmt in list_values])})",
                )
            )

        return stmts

    def __str__(self):
        return f"MERGE({self.node_id})"

    def __hash__(self):
        child_hashes = []
        for val_list in self.__child_nodes.values():
            for val in val_list:
                child_hashes.append(hash(val))

        return hash(
            ("merge", tuple(sorted(child_hashes))),
        )


class ArrayInNode(JsonLogicOperationNode):
    def __init__(self, node_value: Any):
        super().__init__(operation_name="in")

        if not isinstance(node_value, list):
            raise ValueError(f"ArrayInNode expects a list as child, received {type(node_value)}")

        if len(node_value) != 2:
            raise ValueError(f"ArrayInNode expects 2 children, received {len(node_value)}")

        left, right = node_value

        if not isinstance(left, DataVarNode) and not isinstance(right, DataVarNode):
            raise ValueError("ArrayInNode expects at least 1 DataVarNode, received 0")

        self.data_nodes: List[DataVarNode] = []
        self.list_node: Optional[Union[List, ArrayMergeNode]] = None

        if isinstance(left, (list, ArrayMergeNode)):
            self.list_node = left
        else:
            self.data_nodes.append(left)

        if isinstance(right, (list, ArrayMergeNode)):
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
        elif self.list_node and isinstance(self.list_node, ArrayMergeNode):
            self.add_child(self.list_node)

    def get_asp_statements(self) -> List[Statement]:
        literals: List[Literal] = []

        if len(self.data_nodes) == 2:
            literals.extend([node.get_asp_atom_with_different_variable_name("I") for node in self.data_nodes])
            comment = " IN ".join([node.var_name for node in self.data_nodes])

        else:
            data_node = self.data_nodes[0]
            list_node = self.list_node

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
                comment = f"{data_node.var_name} IN ({', '.join([str(stmt) for stmt in self.list_node])})"
            else:
                literals.append(list_node.get_asp_atom_with_different_variable_name("I"))
                comment = f"{data_node.var_name} IN ({str(list_node)})"

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
            ("in",
             *tuple(sorted([hash(node) for node in self.data_nodes])),
             *([hash(self.list_node)] if isinstance(self.list_node, ArrayMergeNode) else sorted(self.list_node))),
        )
