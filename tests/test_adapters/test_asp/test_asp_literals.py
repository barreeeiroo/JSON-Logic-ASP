import pytest

from json_logic_asp.adapters.asp.asp_literals import ComparatorAtom, PredicateAtom
from json_logic_asp.constants.asp_naming import PredicateNames, VariableNames


class TestPredicateAtom:
    @pytest.mark.parametrize(
        "terms, expected",
        [([], "test"), (["a"], "test(a)"), (["a", "b"], "test(a, b)")],
        ids=[
            "no_terms",
            "single_term",
            "multi_term",
        ],
    )
    def test_terms(self, terms, expected):
        atom = PredicateAtom(
            predicate_name="test",
            terms=terms,
        )
        assert atom.to_asp_atom() == expected

    @pytest.mark.parametrize(
        "negated, expected",
        [
            (False, "test(a)"),
            (True, "not test(a)"),
        ],
        ids=[
            "not_negated",
            "negated",
        ],
    )
    def test_negated(self, negated, expected):
        atom = PredicateAtom(
            predicate_name="test",
            terms=["a"],
            negated=negated,
        )
        assert atom.to_asp_atom() == expected

    def test_enum_predicate(self):
        atom = PredicateAtom(
            predicate_name=PredicateNames.DATA_VAR,
            terms=["a"],
        )
        assert atom.to_asp_atom() == "var(a)"


class TestComparatorAtom:
    @pytest.mark.parametrize(
        "left_value, right_value, expected",
        [
            ("V1", "V2", "V1 == V2"),
            (VariableNames.VAR, "V2", "V == V2"),
            ("V2", VariableNames.VAR, "V2 == V"),
            (VariableNames.MERGE, VariableNames.VAR, "M == V"),
        ],
        ids=[
            "str_str",
            "enum_str",
            "str_enum",
            "enum_enum",
        ],
    )
    def test_values(self, left_value, right_value, expected):
        atom = ComparatorAtom(
            left_value=left_value,
            comparator="==",
            right_value=right_value,
        )
        assert atom.to_asp_atom() == expected

    @pytest.mark.parametrize(
        "comparator, expected",
        [
            ("=", "V1 = V2"),
            ("==", "V1 == V2"),
            ("!=", "V1 != V2"),
            (">", "V1 > V2"),
        ],
        ids=[
            "assign",
            "eq",
            "neq",
            "gt",
        ],
    )
    def test_comparator(self, comparator, expected):
        atom = ComparatorAtom(
            left_value="V1",
            comparator=comparator,
            right_value="V2",
        )
        assert atom.to_asp_atom() == expected
