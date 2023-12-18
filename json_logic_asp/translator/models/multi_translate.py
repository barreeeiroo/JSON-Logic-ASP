from typing import Dict

from pydantic import BaseModel, Field

from json_logic_asp.utils.id_management import generate_unique_id


class RuleInput(BaseModel):
    rule_id: str = Field(default_factory=generate_unique_id)
    rule_tree: Dict


class DataInput(BaseModel):
    data_id: str = Field(default_factory=generate_unique_id)
    data_object: Dict
