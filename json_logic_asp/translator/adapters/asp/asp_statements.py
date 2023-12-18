from typing import List

from json_logic_asp.translator.adapters.asp.asp_nodes import Literal, PredicateAtom
from json_logic_asp.translator.models.asp_base import Statement


class FactStatement(Statement):
    def __init__(self, atom: PredicateAtom):
        self.atom = atom

    def to_asp(self):
        return f"{self.atom.to_asp()}."


class RuleStatement(Statement):
    def __init__(self, atom: PredicateAtom, literals: List[Literal]):
        self.atom = atom
        self.literals = literals

    def to_asp(self):
        return f"{self.atom.to_asp()} :- {', '.join([literal.to_asp() for literal in self.literals])}."


class DirectiveStatement(Statement):
    def __init__(self, action: str, statement: str):
        self.action = action
        self.statement = statement

    def to_asp(self):
        return f"#{self.action} {self.statement}."


class ShowStatement(DirectiveStatement):
    def __init__(self, statement: str, length: int):
        super().__init__(action="show", statement=f"{statement}/{length}")
