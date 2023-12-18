from typing import List

from json_logic_asp.translator.models.jl_nodes import JsonLogicNode


class BooleanAndNode(JsonLogicNode):
    def __init__(self, child_nodes: List[JsonLogicNode]):
        super().__init__(*[child.asp_nodes for child in child_nodes])
