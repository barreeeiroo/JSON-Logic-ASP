from abc import ABC
from typing import List, Union

from json_logic_asp.translator.models.asp_base import Atom


class Literal(Atom, ABC):
    pass


class PredicateAtom(Literal):
    def __init__(self, predicate_name: str, terms: List[str], negated: bool = False):
        self.predicate_name = predicate_name
        self.terms = terms
        self.negated = negated

    def to_asp(self):
        asp_terms = ""
        if self.terms:
            asp_terms = f"({', '.join(self.terms)})"

        negated = ""
        if self.negated:
            negated = "not "

        return f"{negated}{self.predicate_name}{asp_terms}"


class VariableAtom(Literal):
    def __init__(self, variable_name: str, value: Union[int, float, str, bool]):
        self.variable_name = variable_name
        self.value = value

    def to_asp(self):
        return f"{self.variable_name} = {self.value}"


class ComparatorAtom(Literal):
    def __init__(self, variable_name: str, comparator: str, target: Union[int, float, str, bool]):
        self.variable_name = variable_name
        self.comparator = comparator
        self.target = target

    def to_asp(self):
        return f"{self.variable_name} {self.comparator} {self.target}"
