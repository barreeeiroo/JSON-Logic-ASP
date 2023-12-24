from abc import ABC
from typing import Any, Dict, List, Union

from json_logic_asp.adapters.asp.asp_literals import ComparatorAtom, Literal
from json_logic_asp.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataVarNode
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import JsonLogicLeafNode
from json_logic_asp.utils.json_logic_helpers import value_encoder


class LogicEvalNode(JsonLogicLeafNode, ABC):
    def __init__(self, comparator: str, predicate: str, node_value: Any):
        super().__init__(operation_name=predicate)

        self.comparator = comparator
        self.predicate = predicate

        if not isinstance(node_value, list):
            raise ValueError(f"LogicEvalNode expects a list as child, received {type(node_value)}")

        if len(node_value) < 2:
            raise ValueError(f"LogicEvalNode expects at least 2 children, received {len(node_value)}")

        self.__child_nodes: List[Union[DataVarNode, str, bool, float, int]] = []
        for node in node_value:
            if not isinstance(node, (DataVarNode, str, bool, float, int)):
                raise ValueError(f"LogicEvalNode received unexpected node type {type(node)}")

            self.__child_nodes.append(node)

    def get_asp_statements(self) -> List[Statement]:
        literals: List[Literal] = []
        comment_parts: List[str] = []

        total_comparisons = len(self.__child_nodes) - 1

        variable_names: Dict[DataVarNode, str] = {}
        for child_node in self.__child_nodes:
            if not isinstance(child_node, DataVarNode):
                continue
            var_name = f"V{len(variable_names) + 1}"
            variable_names[child_node] = var_name
            literals.append(child_node.get_asp_atom_with_different_variable_name(var_name))

        for i in range(total_comparisons):
            left, right = self.__child_nodes[i], self.__child_nodes[i + 1]
            comment_part = ""

            if isinstance(left, DataVarNode):
                if i == 0:
                    comment_parts.append(left.var_name)
                left = variable_names[left]
            else:
                if i == 0:
                    comment_parts.append(str(left))
                left = value_encoder(left)

            if isinstance(right, DataVarNode):
                comment_parts.append(right.var_name)
                right = variable_names[right]
            else:
                comment_parts.append(str(right))
                right = value_encoder(right)

            literals.append(
                ComparatorAtom(
                    left_value=left,
                    comparator=self.comparator,
                    right_value=right,
                )
            )

        return [
            RuleStatement(
                atom=self.get_asp_atom(),
                literals=literals,
                comment=f" {self.predicate.upper()} ".join(comment_parts),
            )
        ]

    def __str__(self):
        return f"{self.predicate.upper()}({self.node_id})"

    def __hash__(self):
        return hash((self.predicate, *sorted(hash(child) for child in self.__child_nodes)))


class LogicEqualNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        super().__init__(comparator="==", predicate="eq", node_value=node_value)


class LogicNotEqualNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        super().__init__(comparator="!=", predicate="neq", node_value=node_value)


class LogicStrictEqualNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        # TODO: This is wrong
        super().__init__(comparator="==", predicate="seq", node_value=node_value)


class LogicStrictNotEqualNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        # TODO: This is wrong
        super().__init__(comparator="!=", predicate="sneq", node_value=node_value)


class LogicLowerThanNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        super().__init__(comparator="<", predicate="lt", node_value=node_value)


class LogicLowerOrEqualThanNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        super().__init__(comparator="<=", predicate="lte", node_value=node_value)


class LogicGreaterThanNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        super().__init__(comparator=">", predicate="gt", node_value=node_value)


class LogicGreaterOrEqualThanNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        super().__init__(comparator=">=", predicate="gte", node_value=node_value)
