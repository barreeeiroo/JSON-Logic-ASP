from typing import Dict

from json_logic_asp.translator.adapters.asp.asp_nodes import PredicateAtom
from json_logic_asp.translator.adapters.asp.asp_statements import FactStatement
from json_logic_asp.translator.models.jl_base import JsonLogicNode
from json_logic_asp.translator.models.multi_translate import DataInput
from json_logic_asp.utils.list_utils import remove_duplicates

DATA_NODE_CACHE: Dict[str, JsonLogicNode] = {}


def __flatten_data(y):
    out = {}

    def flatten(x, name=""):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + ".")
        elif isinstance(x, list):
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)

    return out


def generate_single_data_asp_definition(data_input: DataInput) -> str:
    global DATA_NODE_CACHE
    DATA_NODE_CACHE = dict()

    statements = []

    flattened_obj = __flatten_data(data_input.data_object)
    for var_name, var_value in flattened_obj.items():
        if isinstance(var_value, str):
            var_value = f"'{var_value}'"

        statements.append(
            FactStatement(
                atom=PredicateAtom(predicate_name="var", terms=[f"'{var_name}'", var_value]),
            ).to_asp()
        )

    statements = remove_duplicates(statements)

    return "\n".join(statements)
