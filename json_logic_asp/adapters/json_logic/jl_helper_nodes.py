from typing import List

from json_logic_asp.adapters.asp.asp_literals import PredicateAtom
from json_logic_asp.constants.asp_naming import PredicateNames
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import JsonLogicNode


class JsonLogicHelperBoolNode(JsonLogicNode):
    def __init__(self, *children):
        super().__init__(accepted_child_node_types=(bool,), operation_name=PredicateNames.BOOL)

        if len(children) != 1:
            raise ValueError(f"JsonLogicHelperBoolNode accepts only 1 child, received {len(children)}")

        child = children[0]
        if not isinstance(child, bool):
            raise ValueError(f"JsonLogicHelperBoolNode accepts only bool child, received {child.__class__.__name__}")

        self.bool = child

    @property
    def encoded_bool(self):
        return str(self.bool).lower()

    def get_asp_atom(self) -> PredicateAtom:
        return PredicateAtom(
            predicate_name=self.operation_name,
            terms=[self.encoded_bool],
        )

    def get_asp_statements(self) -> List[Statement]:
        return []

    def __str__(self):
        return f"BOOL({self.encoded_bool})"

    def __hash__(self):
        return hash(
            (
                "bool",
                self.node_id,
            )
        )
