from typing import Any, List, Set

from json_logic_asp.adapters.asp.asp_literals import Literal, PredicateAtom
from json_logic_asp.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import JsonLogicOperationNode
from json_logic_asp.utils.id_management import generate_constant_string


class DataVarNode(JsonLogicOperationNode):
    def __init__(self, node_value: Any):
        super().__init__(operation_name="var")

        if not isinstance(node_value, str):
            raise ValueError(f"DataVarNode requires str as value, received {type(node_value)}")

        self.var_name = node_value
        self.var_variable = "V"

    def get_asp_atom(self) -> PredicateAtom:
        return PredicateAtom(
            predicate_name="var",
            terms=[generate_constant_string(self.var_name), self.var_variable],
        )

    def get_asp_atom_with_different_variable_name(self, var_name: str) -> PredicateAtom:
        atom = self.get_asp_atom()
        return PredicateAtom(
            predicate_name=atom.predicate_name,
            terms=[
                atom.terms[0],
                var_name,
            ],
        )

    def get_asp_statements(self) -> List[Statement]:
        # return [FactStatement(atom=self.get_asp_atom())]
        return []

    def __str__(self):
        return f"VAR({self.var_name})"

    def __hash__(self):
        return hash((self.var_name,))


class DataMissingNode(JsonLogicOperationNode):
    def __init__(self, node_value: Any):
        super().__init__(operation_name="missing")

        if isinstance(node_value, str):
            node_value = [node_value]

        if not isinstance(node_value, list):
            raise ValueError(f"DataVarNode requires list as value, received {type(node_value)}")

        self.var_names: Set[str] = set()
        for var_name in node_value:
            if not isinstance(var_name, str):
                raise ValueError(f"DataVarNode requires str as value, received {type(var_name)}")
            self.var_names.add(var_name)

    def get_asp_statements(self) -> List[Statement]:
        literals: List[Literal] = []
        comment = "Missing "

        for var_name in self.var_names:
            literals.append(
                PredicateAtom(
                    predicate_name="var",
                    terms=[generate_constant_string(var_name), "_"],
                    negated=True,
                )
            )
            comment += var_name

        return [
            RuleStatement(
                atom=self.get_asp_atom(),
                literals=literals,
                comment=comment,
            )
        ]

    def __str__(self):
        return f"MISSING({','.join(self.var_names)})"

    def __hash__(self):
        return hash(tuple(*(sorted(self.var_names))))
