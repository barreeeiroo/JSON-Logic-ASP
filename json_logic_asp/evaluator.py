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
    if simplify:
        for json_logic_rule in json_logic_rules:
            json_logic_rule.rule_tree = simplify_json_logic(json_logic_rule.rule_tree)

    asp_rules_definition, rule_id_mapping = generate_multiple_rule_asp_definition(
        rule_inputs=json_logic_rules,
        with_comments=False,
        custom_nodes=custom_nodes,
    )

    return evaluate_pregenerated_json_logic_rules_against_single_data(
        json_logic_rules_in_asp_definition=asp_rules_definition,
        json_logic_data=json_logic_data,
    )


def evaluate_single_json_logic_rule_against_single_data(json_logic_rule: RuleInput, *args, **kwargs):
    kwargs["json_logic_rules"] = [json_logic_rule]
    return evaluate_multiple_json_logic_rules_against_single_data(*args, **kwargs)
