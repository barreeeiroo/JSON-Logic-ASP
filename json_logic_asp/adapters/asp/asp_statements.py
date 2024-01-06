from typing import Sequence, Union

from json_logic_asp.adapters.asp.asp_literals import Literal, PredicateAtom
from json_logic_asp.constants.asp_naming import PredicateNames
from json_logic_asp.models.asp_base import Statement


class FactStatement(Statement):
    def __init__(self, atom: PredicateAtom, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.atom = atom

    def to_asp_statement(self):
        return f"{self.atom.to_asp_atom()}."


class RuleStatement(Statement):
    def __init__(self, atom: PredicateAtom, literals: Sequence[Literal], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.atom = atom
        self.literals = literals

    def to_asp_statement(self):
        return f"{self.atom.to_asp_atom()} :- {', '.join([literal.to_asp_atom() for literal in self.literals])}."


class DirectiveStatement(Statement):
    def __init__(self, action: str, statement: str):
        super().__init__(comment=None)
        self.action = action
        self.statement = statement

    def to_asp_statement(self):
        return f"#{self.action} {self.statement}."


class ShowStatement(DirectiveStatement):
    def __init__(self, predicate: Union[str, PredicateNames], length: int):
        if isinstance(predicate, PredicateNames):
            predicate = predicate.value
        super().__init__(action="show", statement=f"{predicate}/{length}")
