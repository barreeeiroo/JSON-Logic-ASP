from typing import List, Union

from json_logic_asp.translator.adapters.asp.asp_nodes import Literal, PredicateAtom, VariableAtom
from json_logic_asp.translator.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.translator.adapters.json_logic.jl_data_nodes import DataVarNode
from json_logic_asp.translator.models.jl_base import JsonLogicDefinitionNode, JsonLogicFactNode, JsonLogicRuleNode
from json_logic_asp.utils.id_management import generate_constant_string, generate_unique_id
from json_logic_asp.utils.json_logic_helpers import value_encoder


class ArrayInNode(JsonLogicRuleNode):
    def __init__(
        self,
        left_statement: JsonLogicDefinitionNode,
        right_statement: Union[JsonLogicDefinitionNode, List[Union[int, float, str]]],
    ):
        node_id = generate_unique_id()

        self.__node_statements: List[Union[JsonLogicDefinitionNode, List[Union[int, float, str]]]] = [
            left_statement,
            right_statement,
        ]

        literals: List[Literal] = []
        if isinstance(left_statement, JsonLogicDefinitionNode):
            literals.extend([stmt.atom for stmt in left_statement.asp_statements])
        else:
            raise ValueError(f"First argument {left_statement} is not JsonLogicDefinitionNode")

        if isinstance(right_statement, JsonLogicDefinitionNode):
            literals.extend([stmt.atom for stmt in right_statement.asp_statements])
        else:
            right_val = [value_encoder(val) for val in right_statement]
            literals.append(
                VariableAtom(
                    variable_name="V",
                    value=f"({';'.join(right_val)})",
                )
            )

        comment = None
        if isinstance(left_statement, DataVarNode) and isinstance(right_statement, list):
            comment = f"{left_statement.var_name} IN " f"({', '.join([str(stmt) for stmt in right_statement])})"

        self.statement = RuleStatement(
            atom=PredicateAtom(predicate_name="in", terms=[node_id]),
            literals=literals,
            comment=comment,
        )

        super().__init__(node_id=node_id, asp_statements=[self.statement])

    def to_asp(self, with_comment: bool = False):
        stmts = []
        for child_node in [self.__node_statements]:
            if isinstance(child_node, JsonLogicFactNode):
                stmts.extend(child_node.to_asp(with_comment=with_comment))

        if with_comment and self.statement.to_asp_comment():
            stmts.append(self.statement.to_asp_comment())
        stmts.append(self.statement.to_asp_statement())
        return stmts

    def __str__(self):
        return f"IN({self.id})"

    def __hash__(self):
        return hash(
            (
                "in",
                *sorted(
                    hash(child)
                    if not isinstance(child, list)
                    else hash(tuple(sorted(hash(child2) for child2 in child)))
                    for child in self.__node_statements
                ),
            )
        )
