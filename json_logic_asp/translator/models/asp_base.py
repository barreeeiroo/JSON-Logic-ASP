from abc import ABC, abstractmethod
from typing import Optional


class Statement(ABC):
    def __init__(self, comment: Optional[str] = None):
        self.comment = comment

    def comment_to_asp(self):
        if self.comment:
            return f"% {self.comment}"
        return None

    @abstractmethod
    def to_asp(self) -> str:
        raise NotImplementedError()


class Atom(ABC):
    @abstractmethod
    def to_asp(self):
        raise NotImplementedError()
