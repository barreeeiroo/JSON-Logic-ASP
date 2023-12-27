from json_logic_asp.adapters.asp.asp_literals import PredicateAtom
from json_logic_asp.adapters.asp.asp_statements import FactStatement
from json_logic_asp.constants.asp_naming import PredicateNames
from json_logic_asp.models.translator_dto import DataInput
from json_logic_asp.utils.id_management import generate_constant_string
from json_logic_asp.utils.json_logic_helpers import value_encoder
from json_logic_asp.utils.list_utils import remove_duplicates


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


def generate_single_data_asp_definition(data_input: DataInput, with_comments: bool = False) -> str:
    """
    Given a data input, generate the corresponding ASP definition.

    :param data_input: DataInput object with the containing data
    :param with_comments: if true, generate the definition including ASP comments
    :return: data encoded in ASP definition
    """
    statements = []

    flattened_obj = __flatten_data(data_input.data_object)
    for var_name, var_value in flattened_obj.items():
        stmt = FactStatement(
            atom=PredicateAtom(
                predicate_name=PredicateNames.DATA_VAR,
                terms=[
                    generate_constant_string(var_name),
                    value_encoder(var_value),
                ],
            ),
            comment=f"{var_name} : {var_value}",
        )
        if with_comments:
            statements.append(stmt.to_asp_comment())
        statements.append(stmt.to_asp_statement())

    statements = remove_duplicates(statements)

    return "\n".join(statements)
