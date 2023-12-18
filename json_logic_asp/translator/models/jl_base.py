from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from json_logic_asp.translator.adapters.asp.asp_statements import FactStatement, RuleStatement, Statement


class JsonLogicNode(ABC):
    def __init__(self, asp_statements: List[Statement]):
        self.asp_statements = asp_statements

    @abstractmethod
    def to_asp(self) -> List[str]:
        raise NotImplementedError()

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError()


class JsonLogicFactNode(JsonLogicNode, ABC):
    def __init__(self, asp_statements: List[FactStatement]):
        super().__init__(asp_statements)
        self.asp_statements: List[FactStatement] = asp_statements


class JsonLogicRuleNode(JsonLogicNode, ABC):
    def __init__(self, node_id: str, asp_statements: List[RuleStatement]):
        super().__init__(asp_statements)
        self.id = node_id
        self.asp_statements: List[RuleStatement] = asp_statements
