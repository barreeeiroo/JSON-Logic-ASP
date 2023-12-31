from typing import Any, List

import pytest

from json_logic_asp.adapters.asp.asp_literals import ComparatorAtom
from json_logic_asp.adapters.asp.asp_statements import RuleStatement
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataVarNode
from json_logic_asp.adapters.json_logic.jl_logic_nodes import (
    LogicEqualNode,
    LogicEvalNode,
    LogicGreaterOrEqualThanNode,
    LogicGreaterThanNode,
    LogicIfNode,
    LogicLowerOrEqualThanNode,
    LogicLowerThanNode,
    LogicNotEqualNode,
    LogicStrictEqualNode,
    LogicStrictNotEqualNode,
)
from json_logic_asp.models.asp_base import Statement
from json_logic_asp.models.json_logic_nodes import JsonLogicSingleDataNode


class TestLogicIfNode:
    def test_invalid_values(self):
        with pytest.raises(ValueError) as exc1:
            LogicIfNode("a")
        assert exc1.match("LogicIfNode expects a list as child")

        with pytest.raises(ValueError) as exc1:
            LogicIfNode([])
        assert exc1.match("LogicIfNode at least 1 child")

        with pytest.raises(ValueError) as exc1:
            LogicIfNode(["a"])
        assert exc1.match("Found unexpected child_node type str for LogicIfNode")

    def test_valid_values(self):
        eq = LogicEqualNode(["a", "b"])
        gt = LogicGreaterThanNode([3, 1])
        node = LogicIfNode([eq, gt])

        assert isinstance(node, LogicIfNode)

    def test_child_registration(self):
        eq = LogicEqualNode(["a", "b"])
        gt = LogicGreaterThanNode([3, 1])
        node = LogicIfNode([eq, gt])

        assert node.child_nodes == [eq, gt]

    def test_statements_if(self):
        eq = LogicEqualNode(["a", "b"])
        node = LogicIfNode([eq])

        assert node.to_asp(with_comment=True) == [
            "% a EQ b",
            "eq(mock1) :- s0cc175b9c0f1b6a831c399e269772661 == s92eb5ffee6ae2fec3ad71c777531578f.",
            "if(mock2) :- eq(mock1).",
        ]

    def test_statements_if_cond(self):
        eq = LogicEqualNode(["a", "b"])
        gt = LogicGreaterThanNode([3, 1])
        node = LogicIfNode([eq, gt])

        assert node.to_asp(with_comment=True) == [
            "% a EQ b",
            "eq(mock1) :- s0cc175b9c0f1b6a831c399e269772661 == s92eb5ffee6ae2fec3ad71c777531578f.",
            "% 3 GT 1",
            "gt(mock2) :- 3 > 1.",
            "if(mock3) :- eq(mock1), gt(mock2).",
        ]

    def test_statements_if_cond_else(self):
        eq = LogicEqualNode(["a", "b"])
        gt = LogicGreaterThanNode([3, 1])
        lt = LogicLowerThanNode([4, 3])
        node = LogicIfNode([eq, gt, lt])

        assert node.to_asp(with_comment=True) == [
            "% a EQ b",
            "eq(mock1) :- s0cc175b9c0f1b6a831c399e269772661 == s92eb5ffee6ae2fec3ad71c777531578f.",
            "% 3 GT 1",
            "gt(mock2) :- 3 > 1.",
            "% 4 LT 3",
            "lt(mock3) :- 4 < 3.",
            "else(mock5) :- not eq(mock1), lt(mock3).",
            "if(mock4) :- else(mock5).",
            "if(mock4) :- eq(mock1), gt(mock2).",
        ]

    def test_statements_if_cond_elif_cond(self):
        eq = LogicEqualNode(["a", "b"])
        gt = LogicGreaterThanNode([3, 1])
        eq2 = LogicEqualNode(["a2", "b2"])
        gt2 = LogicGreaterThanNode([30, 10])
        node = LogicIfNode([eq, gt, eq2, gt2])

        assert node.to_asp(with_comment=True) == [
            "% a EQ b",
            "eq(mock1) :- s0cc175b9c0f1b6a831c399e269772661 == s92eb5ffee6ae2fec3ad71c777531578f.",
            "% 3 GT 1",
            "gt(mock2) :- 3 > 1.",
            "% a2 EQ b2",
            "eq(mock3) :- s693a9fdd4c2fd0700968fba0d07ff3c0 == sfbfba2e45c2045dc5cab22a5afe83d9d.",
            "% 30 GT 10",
            "gt(mock4) :- 30 > 10.",
            "elif(mock6) :- not eq(mock1), eq(mock3), gt(mock4).",
            "if(mock5) :- elif(mock6).",
            "if(mock5) :- eq(mock1), gt(mock2).",
        ]

    def test_statements_if_cond_elif_cond_else(self):
        eq = LogicEqualNode(["a", "b"])
        gt = LogicGreaterThanNode([3, 1])
        eq2 = LogicEqualNode(["a2", "b2"])
        gt2 = LogicGreaterThanNode([30, 10])
        lt = LogicLowerThanNode([4, 3])
        node = LogicIfNode([eq, gt, eq2, gt2, lt])

        assert node.to_asp(with_comment=True) == [
            "% a EQ b",
            "eq(mock1) :- s0cc175b9c0f1b6a831c399e269772661 == s92eb5ffee6ae2fec3ad71c777531578f.",
            "% 3 GT 1",
            "gt(mock2) :- 3 > 1.",
            "% a2 EQ b2",
            "eq(mock3) :- s693a9fdd4c2fd0700968fba0d07ff3c0 == sfbfba2e45c2045dc5cab22a5afe83d9d.",
            "% 30 GT 10",
            "gt(mock4) :- 30 > 10.",
            "% 4 LT 3",
            "lt(mock5) :- 4 < 3.",
            "else(mock8) :- not eq(mock1), not eq(mock3), lt(mock5).",
            "elif(mock7) :- else(mock8).",
            "elif(mock7) :- not eq(mock1), eq(mock3), gt(mock4).",
            "if(mock6) :- elif(mock7).",
            "if(mock6) :- eq(mock1), gt(mock2).",
        ]

    def test_statements_if_cond_elif_cond_elif_cond(self):
        eq = LogicEqualNode(["a", "b"])
        gt = LogicGreaterThanNode([3, 1])
        eq2 = LogicEqualNode(["a2", "b2"])
        gt2 = LogicGreaterThanNode([30, 10])
        eq3 = LogicEqualNode(["a3", "b3"])
        gt3 = LogicGreaterThanNode([300, 100])
        node = LogicIfNode([eq, gt, eq2, gt2, eq3, gt3])

        assert node.to_asp(with_comment=True) == [
            "% a EQ b",
            "eq(mock1) :- s0cc175b9c0f1b6a831c399e269772661 == s92eb5ffee6ae2fec3ad71c777531578f.",
            "% 3 GT 1",
            "gt(mock2) :- 3 > 1.",
            "% a2 EQ b2",
            "eq(mock3) :- s693a9fdd4c2fd0700968fba0d07ff3c0 == sfbfba2e45c2045dc5cab22a5afe83d9d.",
            "% 30 GT 10",
            "gt(mock4) :- 30 > 10.",
            "% a3 EQ b3",
            "eq(mock5) :- s9d607a663f3e9b0a90c3c8d4426640dc == s7a6f150b83091ce20c89368641f9a137.",
            "% 300 GT 100",
            "gt(mock6) :- 300 > 100.",
            "elif(mock9) :- not eq(mock1), not eq(mock3), eq(mock5), gt(mock6).",
            "elif(mock8) :- elif(mock9).",
            "elif(mock8) :- not eq(mock1), eq(mock3), gt(mock4).",
            "if(mock7) :- elif(mock8).",
            "if(mock7) :- eq(mock1), gt(mock2).",
        ]

    def test_statements_if_cond_elif_cond_elif_cond_else(self):
        eq = LogicEqualNode(["a", "b"])
        gt = LogicGreaterThanNode([3, 1])
        eq2 = LogicEqualNode(["a2", "b2"])
        gt2 = LogicGreaterThanNode([30, 10])
        eq3 = LogicEqualNode(["a3", "b3"])
        gt3 = LogicGreaterThanNode([300, 100])
        lt = LogicLowerThanNode([4, 3])
        node = LogicIfNode([eq, gt, eq2, gt2, eq3, gt3, lt])

        assert node.to_asp(with_comment=True) == [
            "% a EQ b",
            "eq(mock1) :- s0cc175b9c0f1b6a831c399e269772661 == s92eb5ffee6ae2fec3ad71c777531578f.",
            "% 3 GT 1",
            "gt(mock2) :- 3 > 1.",
            "% a2 EQ b2",
            "eq(mock3) :- s693a9fdd4c2fd0700968fba0d07ff3c0 == sfbfba2e45c2045dc5cab22a5afe83d9d.",
            "% 30 GT 10",
            "gt(mock4) :- 30 > 10.",
            "% a3 EQ b3",
            "eq(mock5) :- s9d607a663f3e9b0a90c3c8d4426640dc == s7a6f150b83091ce20c89368641f9a137.",
            "% 300 GT 100",
            "gt(mock6) :- 300 > 100.",
            "% 4 LT 3",
            "lt(mock7) :- 4 < 3.",
            "else(mock11) :- not eq(mock1), not eq(mock3), not eq(mock5), lt(mock7).",
            "elif(mock10) :- else(mock11).",
            "elif(mock10) :- not eq(mock1), not eq(mock3), eq(mock5), gt(mock6).",
            "elif(mock9) :- elif(mock10).",
            "elif(mock9) :- not eq(mock1), eq(mock3), gt(mock4).",
            "if(mock8) :- elif(mock9).",
            "if(mock8) :- eq(mock1), gt(mock2).",
        ]

    def test_str(self):
        eq = LogicEqualNode(["a", "b"])
        gt = LogicGreaterThanNode([3, 1])
        node = LogicIfNode([eq, gt])

        assert str(node) == "IF(mock3)"

    def test_hash(self):
        eq = LogicEqualNode(["a", "b"])
        gt = LogicGreaterThanNode([3, 1])
        node = LogicIfNode([eq, gt])
        node2 = LogicIfNode([gt, eq])
        node3 = LogicIfNode([eq, gt])

        nested_hash = hash(("if", node._get_children_hash(sort=False)))
        assert hash(node) == nested_hash == hash(node3) != hash(node2)
        assert node == node3 != node2


class DummyLogicEvalNode(LogicEvalNode):
    def __init__(self, node_value: Any):
        super().__init__(comparator="~~", predicate="dummy", node_value=node_value)


class DummySingleDataNode(JsonLogicSingleDataNode):
    def __init__(self):
        super().__init__(term_variable_name="T", operation_name="test")

    def get_asp_statements(self) -> List[Statement]:
        return [RuleStatement(
            atom=self.get_asp_atom(),
            literals=[ComparatorAtom(
                left_value=self.term_variable_name,
                comparator="=",
                right_value=self.node_id,
            )],
            comment=f"TEST {self.node_id}",
        )]

    def __str__(self):
        return f"TEST({self.node_id})"

    def __hash__(self):
        return hash((self.operation_name, self.node_id,))


class TestLogicEvalNode:
    def test_invalid_values(self):
        with pytest.raises(ValueError) as exc1:
            DummyLogicEvalNode("a")
        assert exc1.match("LogicEvalNode expects a list as child")

        with pytest.raises(ValueError) as exc2:
            DummyLogicEvalNode(["a"])
        assert exc2.match("LogicEvalNode expects at least 2 children")

        with pytest.raises(ValueError) as exc2:
            DummyLogicEvalNode(["a", None])
        assert exc2.match("LogicEvalNode received unexpected node type")

    def test_valid_values(self):
        node1 = DummyLogicEvalNode(["a", "b"])
        assert isinstance(node1, LogicEvalNode)

        node2 = DummyLogicEvalNode(["a", ["b"]])
        assert isinstance(node2, LogicEvalNode)

    def test_child_registration(self):
        dummy = DummySingleDataNode()
        data = DataVarNode("var")
        node = DummyLogicEvalNode(["str", 123, ["str2"], [dummy], data, "str"])

        assert node.child_nodes == [dummy]
        assert node._LogicEvalNode__child_nodes == ["str", 123, "str2", dummy, data]  # noqa

    def test_statements_primitives(self):
        node = DummyLogicEvalNode(["str1", "str2", "str3"])

        assert node.to_asp(with_comment=True) == [
            "% str1 DUMMY str2 DUMMY str3",
            "dummy(mock1) :- sd7b5808c3f443eb5a496225468c7e4a5 ~~ s6dc84905d6df841d6f19153bd593e213, "
            "s6dc84905d6df841d6f19153bd593e213 ~~ sbbcdf42954dfd002eca26250327c7601.",
        ]

    def test_statements_single_data_var(self):
        data_var = DataVarNode("var_name")
        node = DummyLogicEvalNode(["str1", data_var, "str2"])

        assert node.to_asp(with_comment=True) == [
            "% str1 DUMMY var_name DUMMY str2",
            "dummy(mock2) :- var(s86536e21993c5a96a4d4c9c9afcc9b17, V1), "
            "sd7b5808c3f443eb5a496225468c7e4a5 ~~ V1, V1 ~~ s6dc84905d6df841d6f19153bd593e213.",
        ]

    def test_statements_multi_data_var(self):
        data_var1 = DataVarNode("var_name1")
        data_var2 = DataVarNode("var_name2")
        node = DummyLogicEvalNode([data_var1, "str", data_var2])

        assert node.to_asp(with_comment=True) == [
            "% var_name1 DUMMY str DUMMY var_name2",
            "dummy(mock3) :- var(sba2b7e1d0917308739c065694dada0f0, V1), var(sa3560e2eb08629b2750d15e8549f29c8, V2), "
            "V1 ~~ s341be97d9aff90c9978347f66f945b77, s341be97d9aff90c9978347f66f945b77 ~~ V2.",
        ]

    def test_statements_multi_data_var_only(self):
        data_var1 = DataVarNode("var_name1")
        data_var2 = DataVarNode("var_name2")
        data_var3 = DataVarNode("var_name3")
        node = DummyLogicEvalNode([data_var1, data_var2, data_var3])

        assert node.to_asp(with_comment=True) == [
            "% var_name1 DUMMY var_name2 DUMMY var_name3",
            "dummy(mock4) :- var(sba2b7e1d0917308739c065694dada0f0, V1), "
            "var(sa3560e2eb08629b2750d15e8549f29c8, V2), var(se4ea6bbcc25f950424a3dc160aca54d0, V3), "
            "V1 ~~ V2, V2 ~~ V3.",
        ]

    def test_statements_single_data_node(self):
        data_var = DataVarNode("var_name")
        dummy = DummySingleDataNode()
        node = DummyLogicEvalNode([data_var, dummy])

        assert node.to_asp(with_comment=True) == [
            "% TEST mock2",
            "test(mock2, T) :- T = mock2.",
            "% var_name DUMMY TEST(mock2)",
            "dummy(mock3) :- var(s86536e21993c5a96a4d4c9c9afcc9b17, V1), test(mock2, V2), "
            "V1 ~~ V2.",
        ]

    def test_statements_multi_data_node(self):
        data_var = DataVarNode("var_name")
        dummy1 = DummySingleDataNode()
        dummy2 = DummySingleDataNode()
        node = DummyLogicEvalNode([dummy1, data_var, dummy2])

        assert node.to_asp(with_comment=True) == [
            "% TEST mock2",
            "test(mock2, T) :- T = mock2.",
            "% TEST mock3",
            "test(mock3, T) :- T = mock3.",
            "% TEST(mock2) DUMMY var_name DUMMY TEST(mock3)",
            "dummy(mock4) :- test(mock2, V1), var(s86536e21993c5a96a4d4c9c9afcc9b17, V2), test(mock3, V3), "
            "V1 ~~ V2, V2 ~~ V3.",
        ]

    def test_str(self):
        node = DummyLogicEvalNode(["a", "b"])

        assert str(node) == "DUMMY(mock1)"

    def test_hash(self):
        node = DummyLogicEvalNode(["a", "b"])
        node2 = DummyLogicEvalNode(["b", "a"])
        node3 = DummyLogicEvalNode(["a", "b"])
        node4 = DummyLogicEvalNode(["a", "b2"])

        nested_hash = tuple(sorted(hash(child) for child in node._LogicEvalNode__child_nodes))  ## noqa
        assert hash(node) == hash(("dummy", nested_hash)) == hash(node3) == hash(node3) != hash(node4)
        assert node == node2 == node3 != node4


def test_logic_equal_node():
    node = LogicEqualNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "eq"
    assert node.comparator == "=="


def test_logic_not_equal_node():
    node = LogicNotEqualNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "neq"
    assert node.comparator == "!="


def test_logic_strict_equal_node():
    node = LogicStrictEqualNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "seq"
    # assert node.comparator == "==="


def test_logic_strict_not_equal_node():
    node = LogicStrictNotEqualNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "sneq"
    # assert node.comparator == "!=="


def test_logic_lower_than_node():
    node = LogicLowerThanNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "lt"
    assert node.comparator == "<"


def test_logic_lower_or_equal_than_node():
    node = LogicLowerOrEqualThanNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "lte"
    assert node.comparator == "<="


def test_logic_greater_than_node():
    node = LogicGreaterThanNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "gt"
    assert node.comparator == ">"


def test_logic_greater_or_equal_than_node():
    node = LogicGreaterOrEqualThanNode(["a", "b"])
    assert isinstance(node, LogicEvalNode)
    assert node.predicate == node.operation_name == "gte"
    assert node.comparator == ">="
