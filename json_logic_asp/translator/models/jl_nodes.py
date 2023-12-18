from abc import ABC
from typing import List

from json_logic_asp.translator.models.asp_nodes import Atom


class JsonLogicNode(ABC):
    def __init__(self, asp_nodes: List[Atom]):
        self.asp_nodes = asp_nodes
