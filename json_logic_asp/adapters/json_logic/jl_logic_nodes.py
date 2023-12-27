from abc import ABC
from typing import Any, Dict, List, Union

from json_logic_asp.adapters.asp.asp_literals import ComparatorAtom, Literal, PredicateAtom
from json_logic_asp.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataVarNode
from json_logic_asp.constants.asp_naming import PredicateNames, VariableNames
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import JsonLogicOperationNode, JsonLogicSingleDataNode, JsonLogicTreeNode
from json_logic_asp.utils.id_management import generate_unique_id
from json_logic_asp.utils.json_logic_helpers import value_encoder


class LogicIfNode(JsonLogicTreeNode):
    def __init__(self, child_nodes: List[Any]):
        super().__init__(operation_name=PredicateNames.LOGIC_IF)

        for child_node in child_nodes:
            self.register_child(child_node)

    def get_asp_statements(self) -> List[Statement]:
        # Evaluation happens in pairs: if(A, B, C, D, E, F, Z) gets translated to
        #   else(nodeZ) :- not A, not C, not E, Z.
        #   elif(node3) :- else(node4)
        #   elif(node3) :- not A, not C, E, F
        #   elif(node2) :- elif(node3)
        #   elif(node2) :- not A, C, D
        #   if(node1) :- elif(node2)
        #   if(node1) :- A, B

        total_nodes = len(self.child_nodes)
        # Only generate elif's when there are more than 3 nodes
        total_elifs = 0 if total_nodes < 4 else total_nodes // 2 - 1
        # Only generate else when there are more than 1 node
        has_else = total_nodes > 1 and total_nodes % 2 == 1

        stmts: List[Statement] = []

        negated_atoms: List[PredicateAtom] = []

        begin_i, end_i = 0, min(total_nodes, 2)
        # if(node1) :- A, B
        stmts.append(
            RuleStatement(
                atom=self.get_asp_atom(),
                literals=[child.get_asp_atom() for child in self.child_nodes[begin_i:end_i]],
            )
        )
        negated_atoms.append(self.child_nodes[begin_i].get_negated_asp_atom())
        prev_atom = self.get_asp_atom()

        for elif_id in range(total_elifs):
            new_atom = PredicateAtom(predicate_name=PredicateNames.LOGIC_IF_ELIF, terms=[generate_unique_id()])
            # if(node1) :- elif(node2)
            stmts.append(
                RuleStatement(
                    atom=prev_atom,
                    literals=[new_atom],
                )
            )
            begin_i += 2
            end_i += 2
            # elif(node2) :- not A, C, D
            stmts.append(
                RuleStatement(
                    atom=new_atom,
                    literals=negated_atoms + [child.get_asp_atom() for child in self.child_nodes[begin_i:end_i]],
                )
            )
            negated_atoms.append(self.child_nodes[begin_i].get_negated_asp_atom())
            prev_atom = new_atom

        if has_else:
            new_atom = PredicateAtom(predicate_name=PredicateNames.LOGIC_IF_ELSE, terms=[generate_unique_id()])
            stmts.append(
                RuleStatement(
                    atom=prev_atom,
                    literals=[new_atom],
                )
            )
            begin_i += 2
            end_i += 1
            # else(nodeZ) :- not A, not C, not E, Z.
            stmts.append(
                RuleStatement(
                    atom=new_atom,
                    literals=negated_atoms + [child.get_asp_atom() for child in self.child_nodes[begin_i:end_i]],
                )
            )

        return list(reversed(stmts))


class LogicEvalNode(JsonLogicOperationNode, ABC):
    def __init__(self, comparator: str, predicate: str, node_value: Any):
        super().__init__(operation_name=predicate)

        self.comparator = comparator
        self.predicate = predicate

        if not isinstance(node_value, list):
            raise ValueError(f"LogicEvalNode expects a list as child, received {type(node_value)}")

        if len(node_value) < 2:
            raise ValueError(f"LogicEvalNode expects at least 2 children, received {len(node_value)}")

        self.__child_nodes: List[Union[JsonLogicSingleDataNode, str, bool, float, int]] = []
        for node in node_value:
            if isinstance(node, list) and len(node) == 1:
                node = node[0]

            if not isinstance(node, (JsonLogicSingleDataNode, str, bool, float, int)):
                raise ValueError(f"LogicEvalNode received unexpected node type {type(node)}")

            self.__child_nodes.append(node)

            if isinstance(node, JsonLogicSingleDataNode) and not isinstance(node, DataVarNode):
                self.register_child(node)

    def get_asp_statements(self) -> List[Statement]:
        literals: List[Literal] = []
        comment_parts: List[str] = []

        total_comparisons = len(self.__child_nodes) - 1

        variable_names: Dict[JsonLogicSingleDataNode, str] = {}
        for child_node in self.__child_nodes:
            if not isinstance(child_node, JsonLogicSingleDataNode):
                continue

            var_name = f"{VariableNames.VAR}{len(variable_names) + 1}"
            variable_names[child_node] = var_name
            literals.append(child_node.get_asp_atom_with_different_variable_name(var_name))

        for i in range(total_comparisons):
            left, right = self.__child_nodes[i], self.__child_nodes[i + 1]

            if isinstance(left, JsonLogicSingleDataNode):
                if i == 0:
                    comment_parts.append(left.var_name if isinstance(left, DataVarNode) else str(left))
                left = variable_names[left]
            else:
                if i == 0:
                    comment_parts.append(str(left))
                left = value_encoder(left)

            if isinstance(right, JsonLogicSingleDataNode):
                comment_parts.append(right.var_name if isinstance(right, DataVarNode) else str(right))
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
        return hash((self.predicate, sorted(hash(child) for child in self.__child_nodes)))


class LogicEqualNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        # TODO: This is wrong
        super().__init__(comparator="==", predicate=PredicateNames.LOGIC_EQUALS, node_value=node_value)


class LogicNotEqualNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        # TODO: This is wrong
        super().__init__(comparator="!=", predicate=PredicateNames.LOGIC_NOTEQUALS, node_value=node_value)


class LogicStrictEqualNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        super().__init__(comparator="==", predicate=PredicateNames.LOGIC_STRICTEQUALS, node_value=node_value)


class LogicStrictNotEqualNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        super().__init__(comparator="!=", predicate=PredicateNames.LOGIC_STRICTNOTEQUALS, node_value=node_value)


class LogicLowerThanNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        super().__init__(comparator="<", predicate=PredicateNames.LOGIC_LOWER, node_value=node_value)


class LogicLowerOrEqualThanNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        super().__init__(comparator="<=", predicate=PredicateNames.LOGIC_LOWEREQUAL, node_value=node_value)


class LogicGreaterThanNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        super().__init__(comparator=">", predicate=PredicateNames.LOGIC_GREATER, node_value=node_value)


class LogicGreaterOrEqualThanNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        super().__init__(comparator=">=", predicate=PredicateNames.LOGIC_GREATEREQUAL, node_value=node_value)
