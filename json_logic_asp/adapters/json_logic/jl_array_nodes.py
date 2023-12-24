from typing import List, Any

from json_logic_asp.adapters.asp.asp_literals import Literal, ComparatorAtom
from json_logic_asp.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataVarNode
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import JsonLogicLeafNode
from json_logic_asp.utils.json_logic_helpers import value_encoder


class ArrayInNode(JsonLogicLeafNode):
    def __init__(self, node_value: Any):
        super().__init__(operation_name="in")

        if not isinstance(node_value, list):
            raise ValueError(f"ArrayInNode expects a list as child, received {type(node_value)}")

        if len(node_value) != 2:
            raise ValueError(f"ArrayInNode expects 2 children, received {len(node_value)}")

        left, right = node_value
        if not isinstance(left, DataVarNode) and not isinstance(right, DataVarNode):
            raise ValueError("ArrayInNode expects at least 1 DataVarNode, received 0")
        if not isinstance(left, list) and not isinstance(right, list):
            raise ValueError("ArrayInNode expects at least 1 list, received 0")

        self.data_node = left if isinstance(left, DataVarNode) else right
        self.list_node = right if isinstance(right, list) else left

        for list_elem in self.list_node:
            if not isinstance(list_elem, (str, bool, float, int,)):
                raise ValueError(f"ArrayInNode expects at least 1 list primitve nodes, received {type(list_elem)}")

    def get_asp_statements(self) -> List[Statement]:
        literals: List[Literal] = []
        literals.extend(self.data_node)

        right_val = [value_encoder(val) for val in self.list_node]
        literals.append(
            ComparatorAtom(
                left_value="V",
                comparator="=",
                right_value=f"({';'.join(right_val)})",
            )
        )

        comment = f"{self.data_node.var_name} IN " f"({', '.join([str(stmt) for stmt in self.list_node])})"

        return [RuleStatement(
            atom=self.get_asp_atom(),
            literals=literals,
            comment=comment,
        )]

    def __str__(self):
        return f"IN({self.node_id})"

    def __hash__(self):
        return hash(("in", hash(self.data_node), *sorted(self.list_node)), )
