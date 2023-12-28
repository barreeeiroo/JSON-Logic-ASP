from abc import ABC
from typing import List, Union

from json_logic_asp.constants.asp_naming import PredicateNames, VariableNames
from json_logic_asp.models.asp_base import Atom


class Literal(Atom, ABC):
    pass


class PredicateAtom(Literal):
    def __init__(
        self, predicate_name: Union[str, PredicateNames], terms: List[Union[str, VariableNames]], negated: bool = False
    ):
        self.predicate_name = predicate_name if not isinstance(predicate_name, PredicateNames) else predicate_name.value
        self.terms: List[str] = [term if not isinstance(term, VariableNames) else term.value for term in terms]
        self.negated = negated

    def to_asp_atom(self):
        asp_terms = ""
        if self.terms:
            asp_terms = f"({', '.join([str(term) for term in self.terms])})"

        negated = ""
        if self.negated:
            negated = "not "

        return f"{negated}{self.predicate_name}{asp_terms}"


class ComparatorAtom(Literal):
    def __init__(self, left_value: Union[str, VariableNames], comparator: str, right_value: Union[str, VariableNames]):
        self.left_value = left_value if not isinstance(left_value, VariableNames) else left_value.value
        self.comparator = comparator
        self.right_value = right_value if not isinstance(right_value, VariableNames) else right_value.value

    def to_asp_atom(self):
        return f"{self.left_value} {self.comparator} {self.right_value}"
