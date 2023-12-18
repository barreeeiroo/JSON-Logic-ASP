from typing import List, Union

from json_logic_asp.translator.adapters.asp.asp_nodes import Literal, LiteralAtom, PredicateAtom
from json_logic_asp.translator.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.translator.models.jl_base import JsonLogicFactNode, JsonLogicRuleNode
from json_logic_asp.utils.id_management import generate_unique_id


class LogicEqNode(JsonLogicRuleNode):
    def __init__(self, left_statement: JsonLogicFactNode, right_statement: Union[JsonLogicFactNode, int, float, str]):
        node_id = generate_unique_id()

        self.__node_statements: List[Union[JsonLogicFactNode, int, float, str]] = [left_statement, right_statement]

        literals: List[Literal] = []
        if isinstance(left_statement, JsonLogicFactNode):
            literals.extend([stmt.atom for stmt in left_statement.asp_statements])
        if isinstance(right_statement, JsonLogicFactNode):
            literals.extend([stmt.atom for stmt in right_statement.asp_statements])
        else:
            right_val = right_statement
            if isinstance(right_val, str):
                right_val = f"'{right_val}'"
            literals.append(
                LiteralAtom(
                    variable_name="V",
                    comparator="==",
                    target=right_val,
                )
            )

        self.statement = RuleStatement(
            atom=PredicateAtom(predicate_name="eq", terms=[node_id]),
            literals=literals,
        )

        super().__init__(node_id=node_id, asp_statements=[self.statement])

    def to_asp(self):
        stmts = []
        for child_node in [self.__node_statements]:
            if isinstance(child_node, JsonLogicFactNode):
                stmts.extend(child_node.to_asp())

        stmts.append(self.statement.to_asp())
        return stmts

    def __str__(self):
        return f"EQ({self.id})"

    def __hash__(self):
        return hash(("eq", *sorted(hash(child) for child in self.__node_statements)))
