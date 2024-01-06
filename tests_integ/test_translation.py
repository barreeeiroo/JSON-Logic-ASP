import json
from os import listdir
from os.path import isfile, join
from pathlib import Path

import pytest

from json_logic_asp.models.translator_dto import DataInput, RuleInput
from json_logic_asp.translator import generate_single_data_asp_definition, generate_single_rule_asp_definition
from tests.fixtures import cuid_fixture  # noqa

TESTS_RULES_FOLDER = Path(__file__).parent / "test_rule_translations"
TESTS_RULES_FILE_NAMES = list(
    set([f.split(".")[0] for f in listdir(TESTS_RULES_FOLDER) if isfile(join(TESTS_RULES_FOLDER, f))])
)

TESTS_DATAS_FOLDER = Path(__file__).parent / "test_data_translations"
TESTS_DATAS_FILE_NAMES = list(
    set([f.split(".")[0] for f in listdir(TESTS_DATAS_FOLDER) if isfile(join(TESTS_DATAS_FOLDER, f))])
)


@pytest.mark.parametrize(
    "file_name",
    TESTS_RULES_FILE_NAMES,
    ids=TESTS_RULES_FILE_NAMES,
)
def test_rule_translation(file_name):
    with open(TESTS_RULES_FOLDER / f"{file_name}.json") as f:
        jl_rule = json.loads(f.read())

    with open(TESTS_RULES_FOLDER / f"{file_name}.lp") as f:
        expected_asp_rule = f.read()

    asp_rule = generate_single_rule_asp_definition(
        rule_input=RuleInput(
            rule_id=file_name,
            rule_tree=jl_rule,
        ),
        with_comments=True,
    )

    assert asp_rule.strip() == expected_asp_rule.strip()


@pytest.mark.parametrize(
    "file_name",
    TESTS_DATAS_FILE_NAMES,
    ids=TESTS_DATAS_FILE_NAMES,
)
def test_data_translation(file_name):
    with open(TESTS_DATAS_FOLDER / f"{file_name}.json") as f:
        data_object = json.loads(f.read())

    with open(TESTS_DATAS_FOLDER / f"{file_name}.lp") as f:
        expected_asp_data = f.read()

    asp_data = generate_single_data_asp_definition(
        data_input=DataInput(
            data_id=file_name,
            data_object=data_object,
        ),
        with_comments=True,
    )

    assert asp_data.strip() == expected_asp_data.strip()
