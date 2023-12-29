from json_logic_asp.models.clingo_dto import ClingoOutput


def test_clingo_output():
    output = ClingoOutput(
        success=False,
    )
    assert output.success is False
    assert output.has_mapping is False
    assert output.matching_rules == []


def test_clingo_output_with_mapping():
    output = ClingoOutput(
        success=True,
        has_mapping=True,
    )
    assert output.success is True
    assert output.has_mapping is True
    assert output.matching_rules == []


def test_clingo_output_with_matching_rules():
    output = ClingoOutput(
        success=True,
        matching_rules=["a", "b"]
    )
    assert output.success is True
    assert output.has_mapping is False
    assert output.matching_rules == ["a", "b"]
