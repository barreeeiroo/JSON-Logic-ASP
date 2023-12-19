from json_logic_asp.translator.adapters.asp.asp_nodes import PredicateAtom
from json_logic_asp.translator.adapters.asp.asp_statements import FactStatement
from json_logic_asp.translator.models.jl_base import JsonLogicFactNode
from json_logic_asp.utils.id_management import generate_constant_string


class DataVarNode(JsonLogicFactNode):
    def __init__(self, var_name: str):
        self.var_name = var_name
        self.var_variable = "V"

        self.statement = FactStatement(
            atom=PredicateAtom(
                predicate_name="var", terms=[generate_constant_string(self.var_name), self.var_variable]
            ),
        )

        super().__init__(node_id=self.var_name, asp_statements=[self.statement])

    def to_asp(self, with_comment: bool = False):
        return [self.statement.to_asp()]

    def __str__(self):
        return f"VAR({self.var_name})"

    def __hash__(self):
        return hash((self.var_name,))


class DataMissingNode(JsonLogicFactNode):
    def __init__(self, var_name: str):
        self.var_name = var_name
        self.var_variable = "V"

        self.statement = FactStatement(
            atom=PredicateAtom(
                predicate_name="var",
                terms=[generate_constant_string(self.var_name), "_"],
                negated=True,
            ),
        )

        super().__init__(node_id=self.var_name, asp_statements=[self.statement])

    def to_asp(self, with_comment: bool = False):
        return [self.statement.to_asp()]

    def __str__(self):
        return f"MISSING({self.var_name})"

    def __hash__(self):
        return hash((self.var_name,))
