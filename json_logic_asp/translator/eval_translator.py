from typing import List

from json_logic_asp.adapters.asp.asp_statements import ShowStatement
from json_logic_asp.models.translator_dto import DataInput, DataOutput, RuleInput
from json_logic_asp.translator.data_generator import generate_single_data_asp_definition
from json_logic_asp.translator.rule_generator import generate_multiple_rule_asp_definition
from json_logic_asp.utils.id_management import generate_constant_string


def translate_multi_rule_eval(
    rule_inputs: List[RuleInput], data_input: DataInput, with_comments: bool = False
) -> DataOutput:
    """
    Given some rule inputs and a data input, generate the corresponding ASP definition ready to be executed.
    :param rule_inputs: multiple rule input objects with the rule definitions
    :param data_input: single data input with data to be evaluated against the rules
    :param with_comments: whether the returning ASP statements should include ASP comments
    :return: data object with the generated ASP definition
    """
    stmts: List[str] = []

    data_str = generate_single_data_asp_definition(data_input, with_comments=with_comments)
    rule_str, rule_mapping = generate_multiple_rule_asp_definition(rule_inputs, with_comments=with_comments)

    stmts.append(data_str)
    stmts.append("")
    stmts.append(rule_str)
    stmts.append("")
    stmts.append(ShowStatement("rule", 1).to_asp_statement())

    return DataOutput(
        statements=stmts,
        rule_mapping={generate_constant_string(rule_input.rule_id): rule_input.rule_id for rule_input in rule_inputs},
    )


def translate_single_rule_eval(rule_input: RuleInput, data_input: DataInput, with_comments: bool = False) -> DataOutput:
    """
    Given a rule input and a data input, generate the corresponding ASP definition ready to be executed.
    :param rule_input: single rule input objects with the rule definition
    :param data_input: single data input with data to be evaluated against the rules
    :param with_comments: whether the returning ASP statements should include ASP comments
    :return: data object with the generated ASP definition
    """
    return translate_multi_rule_eval(rule_inputs=[rule_input], data_input=data_input, with_comments=with_comments)
