from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from json_logic_asp.sdk.clingo_sdk import run_clingo


@pytest.mark.parametrize(
    "problem, expected_status, expected_rules",
    [
        (
            "rule(a). rule(b). rule(c). #show rule/1.",
            "SAT",
            ["a", "b", "c"],
        ),
        (
            "node(a). rule(r1). rule(r2) :- node(a). rule(r3) :- node(b). #show rule/1.",
            "SAT",
            ["r1", "r2"],
        ),
        (
            "rule(a). :- rule(a). #show rule/1.",
            "UNSAT",
            [],
        ),
        (
            "node(a). rule(r1) :- node(b). #show rule/1.",
            "SAT",
            [],
        ),
        (
            "rule(a, b). #show rule/2.",
            "SAT",
            [],
        ),
        (
            "THIS IS WRONG DEFINITION",
            "ERROR",
            [],
        ),
    ],
    ids=[
        "simple",
        "condition",
        "unsat",
        "no_match",
        "wrong_rule",
        "invalid_asp",
    ],
)
def test_run_clingo(problem, expected_status, expected_rules):
    with NamedTemporaryFile(mode="w+", encoding="utf-8", suffix=".lp", delete=False) as file:
        file.write(problem + "\n")

    file_path = Path(file.name)
    status, rules, _ = run_clingo(absolute_file_path=str(file_path.absolute()))
    file_path.unlink()

    assert status == expected_status
    assert rules == expected_rules
