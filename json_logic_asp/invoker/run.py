import logging
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Optional, Dict

from json_logic_asp.adapters.asp.asp_statements import ShowStatement
from json_logic_asp.constants.loggers import INVOKER_LOGGER_NAME
from json_logic_asp.models.clingo_dto import ClingoOutput
from json_logic_asp.sdk.clingo_sdk import run_clingo

log = logging.getLogger(INVOKER_LOGGER_NAME)


def __store_clingo_temp_file(problem: str) -> Path:
    file = NamedTemporaryFile(
        mode="w+",
        encoding="utf-8",
        suffix=".lp",
        delete=False,
    )

    file.write(problem + "\n")

    file.close()

    return Path(file.name)


def get_matching_rules_from_asp_problem(problem: str, mapping: Optional[Dict[str, str]] = None) -> List[str]:
    file_path = __store_clingo_temp_file(problem)
    log.debug(f"Temp File Path: {file_path}")

    status, matching_rules, stats = run_clingo(absolute_file_path=str(file_path.absolute()))
    log.debug(stats)

    file_path.unlink()
    log.debug("Removed Temp File")

    output = ClingoOutput(
        success=status == "SAT",
        matching_rules=matching_rules,
    )

    if output.success and mapping:
        return [mapping[rule_id] if rule_id in mapping else rule_id for rule_id in output.matching_rules]

    return output.matching_rules


def get_matching_rules_for_asp_rules_and_data(
        asp_data_definition: str,
        asp_rules_definition: str,
        *args, **kwargs
) -> List[str]:
    asp_definition_parts = [
        asp_data_definition,
        asp_rules_definition,
        ShowStatement("rule", 1).to_asp_statement(),
    ]
    asp_definition = "\n\n\n".join(asp_definition_parts)

    return get_matching_rules_from_asp_problem(problem=asp_definition, *args, **kwargs)
