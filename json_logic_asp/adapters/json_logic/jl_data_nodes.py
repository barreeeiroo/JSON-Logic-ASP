from typing import List

from json_logic_asp.adapters.asp.asp_literals import Literal, PredicateAtom
from json_logic_asp.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.constants.asp_naming import PredicateNames, VariableNames
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import JsonLogicOperationNode, JsonLogicSingleDataNode
from json_logic_asp.utils.id_management import generate_constant_string


class DataVarNode(JsonLogicSingleDataNode):
    def __init__(self, *children):
        super().__init__(term_variable_name=VariableNames.VAR, operation_name=PredicateNames.DATA_VAR)

        if len(children) != 1:
            raise ValueError(f"DataVarNode requires strictly 1 child, received {len(children)}")

        node_value = children[0]
        if not isinstance(node_value, str):
            raise ValueError(f"DataVarNode requires str as value, received {type(node_value)}")

        self.var_name = node_value

    def get_asp_atom(self) -> PredicateAtom:
        return PredicateAtom(
            predicate_name=self.operation_name,
            terms=[generate_constant_string(self.var_name), self.term_variable_name],
        )

    def get_asp_statements(self) -> List[Statement]:
        # return [FactStatement(atom=self.get_asp_atom())]
        return []

    def __str__(self):
        return f"VAR({self.var_name})"

    def __hash__(self):
        return hash(
            (
                PredicateNames.DATA_VAR,
                self.var_name,
            )
        )


class DataMissingNode(JsonLogicOperationNode):
    def __init__(self, *children):
        super().__init__(operation_name=PredicateNames.DATA_MISSING)

        if len(children) < 1:
            raise ValueError("DataVarNode requires at least 1 child")

        self.var_names: List[str] = []
        for var_name in children:
            if not isinstance(var_name, str):
                raise ValueError(f"DataMissingNode requires str as value, received {type(var_name).__name__}")
            if var_name not in self.var_names:
                self.var_names.append(var_name)

    def get_asp_statements(self) -> List[Statement]:
        literals: List[Literal] = []
        comment = ["Missing"]

        for var_name in self.var_names:
            literals.append(
                PredicateAtom(
                    predicate_name=PredicateNames.DATA_VAR,
                    terms=[generate_constant_string(var_name), VariableNames.ANY],
                    negated=True,
                )
            )
            comment.append(var_name)

        return [
            RuleStatement(
                atom=self.get_asp_atom(),
                literals=literals,
                comment=" ".join(comment),
            )
        ]

    def __str__(self):
        return f"MISSING({','.join(self.var_names)})"

    def __hash__(self):
        return hash(
            (
                PredicateNames.DATA_MISSING,
                tuple(sorted(self.var_names)),
            )
        )
