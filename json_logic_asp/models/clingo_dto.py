from typing import List, Optional


class ClingoOutput:
    def __init__(self, success: bool, has_mapping: bool = False, matching_rules: Optional[List[str]] = None):
        if matching_rules is None:
            matching_rules = []

        self.success: bool = success
        self.has_mapping: bool = has_mapping
        self.matching_rules: List[str] = matching_rules
