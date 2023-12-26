from typing import List

from pydantic import BaseModel, Field


class ClingoOutput(BaseModel):
    success: bool
    has_mapping: bool = Field(default=False)
    matching_rules: List[str] = Field(default_factory=list)
