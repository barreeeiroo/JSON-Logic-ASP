from abc import ABC, abstractmethod
from typing import TypeVar, Union, List


class Atom(ABC):
    @abstractmethod
    def to_asp(self):
        raise NotImplementedError()


class PredicateAtom(Atom):
    def __init__(self, predicate_name: str, terms: List[str]):
        self.predicate_name = predicate_name
        self.terms = terms

    def to_asp(self):
        asp_terms = ""
        if self.terms:
            asp_terms = f"({', '.join(self.terms)})"

        return f"{self.predicate_name}{asp_terms}"


class LiteralAtom(Atom):
    def __init__(self, variable_name: str, comparator: str, target: str):
        self.variable_name = variable_name
        self.comparator = comparator
        self.target = target

    def to_asp(self):
        return f"{self.variable_name} {self.comparator} {self.target}"


Literal = TypeVar("Literal", bound=Union[PredicateAtom, LiteralAtom])
