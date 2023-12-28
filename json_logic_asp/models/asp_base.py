from abc import ABC, abstractmethod
from typing import Optional


class Statement(ABC):
    def __init__(self, comment: Optional[str] = None):
        self.comment = comment

    def to_asp_comment(self):
        if self.comment:
            return f"% {self.comment}"
        return None

    @abstractmethod
    def to_asp_statement(self) -> str:
        raise NotImplementedError()  # pragma: no cover


class Atom(ABC):
    @abstractmethod
    def to_asp_atom(self):
        raise NotImplementedError()  # pragma: no cover
