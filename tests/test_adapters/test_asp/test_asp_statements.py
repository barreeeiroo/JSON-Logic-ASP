from json_logic_asp.adapters.asp.asp_literals import PredicateAtom
from json_logic_asp.adapters.asp.asp_statements import DirectiveStatement, FactStatement, RuleStatement, ShowStatement


class TestFactStatement:
    def test_statement(self):
        atom = PredicateAtom(predicate_name="test", terms=["a"])
        stmt = FactStatement(atom=atom)
        assert stmt.to_asp_statement() == "test(a)."


class TestRuleStatement:
    def test_statement_single_literal(self):
        atom = PredicateAtom(predicate_name="test", terms=["a"])
        literal1 = PredicateAtom(predicate_name="test2", terms=["b"])
        stmt = RuleStatement(atom=atom, literals=[literal1])
        assert stmt.to_asp_statement() == "test(a) :- test2(b)."

    def test_statement_multi_literal(self):
        atom = PredicateAtom(predicate_name="test", terms=["a"])
        literal1 = PredicateAtom(predicate_name="test2", terms=["b"])
        literal2 = PredicateAtom(predicate_name="test3", terms=["c"])
        stmt = RuleStatement(atom=atom, literals=[literal1, literal2])
        assert stmt.to_asp_statement() == "test(a) :- test2(b), test3(c)."


class TestDirectiveStatement:
    def test_statement(self):
        stmt = DirectiveStatement(action="show", statement="rule/1")
        assert stmt.to_asp_statement() == "#show rule/1."

    def test_comments(self):
        stmt = DirectiveStatement(action="show", statement="rule/1")
        assert stmt.to_asp_comment() is None


class TestShowStatement:
    def test_statement(self):
        stmt = ShowStatement(statement="test", length=2)
        assert stmt.to_asp_statement() == "#show test/2."
