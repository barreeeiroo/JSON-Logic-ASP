from json_logic_asp.translator.adapters.asp.asp_nodes import PredicateAtom
from json_logic_asp.translator.adapters.asp.asp_statements import FactStatement
from json_logic_asp.translator.models.jl_base import JsonLogicFactNode


class DataVarNode(JsonLogicFactNode):
    def __init__(self, var_name: str):
        self.var_name = var_name

        self.statement = FactStatement(
            atom=PredicateAtom(predicate_name="var", terms=[f"'{self.var_name}'", "V"]),
        )

        super().__init__(asp_statements=[self.statement])

    def to_asp(self):
        return [self.statement.to_asp()]

    def __str__(self):
        return f"VAR({self.var_name})"

    def __hash__(self):
        return hash((self.var_name,))
