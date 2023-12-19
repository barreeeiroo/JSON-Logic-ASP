from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

from json_logic_asp.translator.adapters.asp.asp_statements import FactStatement, RuleStatement

TStatement = TypeVar("TStatement")


class JsonLogicNode(ABC, Generic[TStatement]):
    def __init__(self, asp_statements: List[TStatement]):
        self.asp_statements = asp_statements

    @abstractmethod
    def to_asp(self) -> List[str]:
        raise NotImplementedError()

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError()


class JsonLogicDefinitionNode(JsonLogicNode[TStatement], ABC, Generic[TStatement]):
    def __init__(self, node_id: str, asp_statements: List[TStatement]):
        super().__init__(asp_statements)
        self.id = node_id


class JsonLogicFactNode(JsonLogicDefinitionNode[FactStatement], ABC):
    def __init__(self, node_id: str, asp_statements: List[FactStatement]):
        super().__init__(node_id, asp_statements)


class JsonLogicRuleNode(JsonLogicDefinitionNode[RuleStatement], ABC):
    def __init__(self, node_id: str, asp_statements: List[RuleStatement]):
        super().__init__(node_id, asp_statements)
