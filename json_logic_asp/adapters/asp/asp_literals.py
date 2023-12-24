from abc import ABC
from typing import List

from json_logic_asp.models.asp_base import Atom


class Literal(Atom, ABC):
    pass


class PredicateAtom(Literal):
    def __init__(self, predicate_name: str, terms: List[str], negated: bool = False):
        self.predicate_name = predicate_name
        self.terms = terms
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
    def __init__(self, left_value: str, comparator: str, right_value: str):
        self.left_value = left_value
        self.comparator = comparator
        self.right_value = right_value

    def to_asp_atom(self):
        return f"{self.left_value} {self.comparator} {self.right_value}"
