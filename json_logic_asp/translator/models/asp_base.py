from abc import ABC, abstractmethod


class Statement(ABC):
    @abstractmethod
    def to_asp(self):
        raise NotImplementedError()


class Atom(ABC):
    @abstractmethod
    def to_asp(self):
        raise NotImplementedError()
