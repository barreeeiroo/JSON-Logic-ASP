from typing import Dict, List, Optional

from json_logic_asp.utils.id_management import generate_unique_id


class RuleInput:
    def __init__(self, rule_tree: Dict, rule_id: Optional[str] = None):
        self.rule_id: str = rule_id if rule_id is not None else generate_unique_id()
        self.rule_tree: Dict = rule_tree


class RuleOutput:
    def __init__(self, statements: List[str], rule_mapping: Dict[str, str]):
        self.statements: List[str] = statements
        self.rule_mapping: Dict[str, str] = rule_mapping


class DataInput:
    def __init__(self, data_object: Dict, data_id: Optional[str] = None):
        self.data_id: str = data_id if data_id is not None else generate_unique_id()
        self.data_object: Dict = data_object


class DataOutput:
    def __init__(self, statements: List[str], data_mapping: Dict[str, str]):
        self.statements: List[str] = statements
        self.data_mapping: Dict[str, str] = data_mapping
