from typing import List, Union

from json_logic_asp.translator.adapters.asp.asp_nodes import ComparatorAtom, Literal, PredicateAtom
from json_logic_asp.translator.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.translator.models.jl_base import JsonLogicDefinitionNode, JsonLogicFactNode, JsonLogicRuleNode
from json_logic_asp.utils.id_management import generate_unique_id


class LogicEvalNode(JsonLogicRuleNode):
    def __init__(
        self,
        comparator: str,
        predicate: str,
        # TODO: Change to *args
        left_statement: JsonLogicDefinitionNode,
        right_statement: Union[JsonLogicDefinitionNode, int, float, str, bool],
    ):
        self.comparator = comparator
        self.predicate = predicate

        node_id = generate_unique_id()

        self.__node_statements: List[Union[JsonLogicDefinitionNode, int, float, str, bool]] = [
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
            right_val = right_statement
            if isinstance(right_val, str):
                right_val = f"'{right_val}'"
            literals.append(
                ComparatorAtom(
                    variable_name="V",
                    comparator=comparator,
                    target=right_val,
                )
            )

        self.statement = RuleStatement(
            atom=PredicateAtom(predicate_name=self.predicate, terms=[node_id]),
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
        return f"{self.predicate.upper()}({self.id})"

    def __hash__(self):
        return hash((self.predicate, *sorted(hash(child) for child in self.__node_statements)))
