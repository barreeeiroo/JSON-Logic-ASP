from typing import Dict, List, Optional, Type

from json_logic_asp.invoker.run import get_matching_rules_for_asp_rules_and_data
from json_logic_asp.models.translator_dto import DataInput, RuleInput
from json_logic_asp.simplifier.simplify import simplify_json_logic
from json_logic_asp.translator.data_generator import generate_single_data_asp_definition
from json_logic_asp.translator.rule_generator import generate_multiple_rule_asp_definition


def evaluate_pregenerated_json_logic_rules_against_single_data(
    json_logic_rules_in_asp_definition: str,
    json_logic_data: DataInput,
    rule_id_mapping: Optional[Dict[str, str]] = None,
) -> List[str]:
    """
    Given some rules in ASP definition and a data object, return the matching rules.
    :param json_logic_rules_in_asp_definition: JSON Logic rules in ASP definition
    :param json_logic_data: data object to check against
    :param rule_id_mapping: optional mapping of rule ids
    :return: list of matching rules
    """
    asp_data_definition = generate_single_data_asp_definition(
        data_input=json_logic_data,
        with_comments=False,
    )

    matching_rules = get_matching_rules_for_asp_rules_and_data(
        asp_data_definition=asp_data_definition,
        asp_rules_definition=json_logic_rules_in_asp_definition,
        mapping=rule_id_mapping,
    )

    return matching_rules


def evaluate_multiple_json_logic_rules_against_single_data(
    json_logic_rules: List[RuleInput],
    json_logic_data: DataInput,
    simplify: bool = False,
    custom_nodes: Optional[Dict[str, Type]] = None,
) -> List[str]:
    """
    Given a multiple JSON Logic rules and data, evaluate it using Clingo.
    :param json_logic_rules: list of rule input with JSON Logic definitions
    :param json_logic_data: data input object
    :param simplify: if True, simplifies the JSON Logic definition
    :param custom_nodes: optional dictionary of custom nodes to parse
    :return: list of rule ids matching the data
    """
    if simplify:
        new_json_logic_rules: List[RuleInput] = []
        for json_logic_rule in json_logic_rules:
            new_json_logic_rules.append(
                RuleInput(
                    rule_id=json_logic_rule.rule_id,
                    rule_tree=simplify_json_logic(json_logic_rule.rule_tree),
                )
            )
        json_logic_rules = new_json_logic_rules

    asp_rules_definition, rule_id_mapping = generate_multiple_rule_asp_definition(
        rule_inputs=json_logic_rules,
        with_comments=False,
        custom_nodes=custom_nodes,
    )

    return evaluate_pregenerated_json_logic_rules_against_single_data(
        json_logic_rules_in_asp_definition=asp_rules_definition,
        json_logic_data=json_logic_data,
        rule_id_mapping=rule_id_mapping,
    )


def evaluate_single_json_logic_rule_against_single_data(
    json_logic_rule: RuleInput,
    json_logic_data: DataInput,
    simplify: bool = False,
    custom_nodes: Optional[Dict[str, Type]] = None,
) -> bool:
    """
    Given a single JSON Logic rule and data, evaluate it using Clingo.
    :param json_logic_rule: single rule input with JSON Logic definition
    :param json_logic_data: data input object
    :param simplify: if True, simplifies the JSON Logic definition
    :param custom_nodes: optional dictionary of custom nodes to parse
    :return: whether the rule matches or not the data
    """
    matching_rules = evaluate_multiple_json_logic_rules_against_single_data(
        json_logic_rules=[json_logic_rule],
        json_logic_data=json_logic_data,
        simplify=simplify,
        custom_nodes=custom_nodes,
    )

    return len(matching_rules) == 1
