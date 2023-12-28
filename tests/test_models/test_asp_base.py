from json_logic_asp.models.asp_base import Statement


class DummyStatement(Statement):
    def to_asp_statement(self) -> str:
        return "a(b)."


class TestStatement:
    def test_without_comment(self):
        stmt = DummyStatement()
        assert stmt.to_asp_comment() is None

    def test_with_comment(self):
        stmt = DummyStatement(comment="test")
        assert stmt.to_asp_comment() == "% test"
