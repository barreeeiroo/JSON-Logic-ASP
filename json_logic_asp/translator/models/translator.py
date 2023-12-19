from typing import Dict, List

from pydantic import BaseModel, Field

from json_logic_asp.utils.id_management import generate_unique_id

CLINGO_VARIABLE_PATTERN = r"^[a-z][A-Za-z0-9]*$"


class RuleInput(BaseModel):
    rule_id: str = Field(default_factory=generate_unique_id, pattern=CLINGO_VARIABLE_PATTERN)
    rule_tree: Dict


class RuleOutput(BaseModel):
    statements: List[str]
    mapping: Dict[str, str]


class DataInput(BaseModel):
    data_id: str = Field(default_factory=generate_unique_id, pattern=CLINGO_VARIABLE_PATTERN)
    data_object: Dict


class DataOutput(BaseModel):
    statements: List[str]
