import pytest

from json_logic_asp.adapters.json_logic.jl_array_nodes import ArrayInNode, ArrayMergeNode
from json_logic_asp.adapters.json_logic.jl_boolean_nodes import BooleanAndNode
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataVarNode
from json_logic_asp.adapters.json_logic.jl_logic_nodes import LogicEqualNode


class TestArrayMergeNode:
    def test_invalid_values(self):
        with pytest.raises(ValueError) as exc1:
            ArrayMergeNode("single_node")
        assert exc1.match("ArrayMergeNode requires list as value")

        with pytest.raises(ValueError) as exc2:
            ArrayMergeNode(["valid", None])
        assert exc2.match("ArrayMergeNode received unexpected node type")

        with pytest.raises(ValueError) as exc3:
            ArrayMergeNode([BooleanAndNode([])])
        assert exc3.match("ArrayMergeNode received unexpected node type")

        with pytest.raises(ValueError) as exc4:
            ArrayMergeNode([LogicEqualNode(["a", "b"])])
        assert exc4.match("ArrayMergeNode received unexpected node type")

    def test_valid_values(self):
        node = ArrayMergeNode(["a", "b"])
        assert isinstance(node, ArrayMergeNode)

    def test_child_registration(self):
        merge = ArrayMergeNode(["merged1", "merged2"])
        data = DataVarNode("var")
        node = ArrayMergeNode(["str", 123, ["str2", merge], data, "str"])

        assert node.child_nodes == [merge]
        assert node._ArrayMergeNode__child_nodes == ["str", 123, "str2", merge, data]  # noqa

    def test_atom_generation(self):
        node = ArrayMergeNode(["merged1", "merged2"])
        assert node.get_asp_atom().to_asp_atom() == "merge(mock1, M)"

    def test_statements(self):
        merge = ArrayMergeNode(["merged1", "merged2"])
        data = DataVarNode("var")
        node = ArrayMergeNode(["str", 123, ["str2", merge], data, "str"])

        # Based on generation order:
        #   mock1 should be initial node
        #   mock2 should be datavar
        #   mock3 the actual node
        assert node.to_asp(with_comment=True) == [
            # Translate first MERGE node
            "% Merge (merged1, merged2)",
            "merge(mock1, M) :- M = (s7aa59c39df9b41dac7610e0eb3e602e5;s522db4a7bc213490b4c1d433865dd944).",
            # Start defining the first operations for the merge, starting with merge
            "% Merge MERGE(mock1)",
            "merge(mock3, M) :- merge(mock1, M).",
            # Then var
            "% Merge VAR(var)",
            "merge(mock3, M) :- var(sb2145aac704ce76dbe1ac7adac535b23, M).",
            # And then the primitives
            "% Merge (str, 123, str2)",
            "merge(mock3, M) :- M = (s341be97d9aff90c9978347f66f945b77;123;s6dc84905d6df841d6f19153bd593e213).",
        ]

    def test_str(self):
        node = ArrayMergeNode(["merged1", "merged2"])
        assert str(node) == "MERGE(mock1)"

    def test_hash(self):
        data = DataVarNode("var")
        node = ArrayMergeNode(["merged1", data, "merged2"])
        node2 = ArrayMergeNode(["merged1", "merged2", data])
        node3 = ArrayMergeNode(["merged1", data, "merged3"])

        child_nodes = sorted([hash("merged1"), hash(data), hash("merged2")])
        assert hash(node) == hash(("merge", tuple(child_nodes))) == hash(node2) != hash(node3)


class TestArrayInNode:
    def test_invalid_values(self):
        with pytest.raises(ValueError) as exc1:
            ArrayInNode("single_node")
        assert exc1.match("ArrayInNode expects a list as child")

        with pytest.raises(ValueError) as exc2:
            ArrayInNode([])
        assert exc2.match("ArrayInNode expects 2 children, received 0")

        with pytest.raises(ValueError) as exc3:
            ArrayInNode(["a"])
        assert exc3.match("ArrayInNode expects 2 children, received 1")

        with pytest.raises(ValueError) as exc4:
            ArrayInNode(["a", "b", "c"])
        assert exc4.match("ArrayInNode expects 2 children, received 3")

        with pytest.raises(ValueError) as exc5:
            merge = ArrayMergeNode(["a", "b"])
            ArrayInNode([merge, ["c", "d"]])
        assert exc5.match("ArrayInNode expects at least 1 JsonLogicSingleDataNode")

        with pytest.raises(ValueError) as exc6:
            data_var1 = DataVarNode("a1")
            data_var2 = DataVarNode("a2")
            ArrayInNode([data_var1, data_var2])
        assert exc6.match("ArrayInNode expects at least 1 JsonLogicMultiDataNode or list")

        with pytest.raises(ValueError) as exc7:
            data_var = DataVarNode("a")
            ArrayInNode([data_var, ["b", None, "c"]])
        assert exc7.match("ArrayInNode expects at least 1 list primitive nodes")

    def test_valid_values(self):
        data_var = DataVarNode("a")
        node = ArrayInNode([data_var, ["b", "c"]])
        assert isinstance(node, ArrayInNode)

    def test_child_registration(self):
        data_var = DataVarNode("a")
        node_left_list = ArrayInNode([["b", "c"], data_var])
        node_right_list = ArrayInNode([data_var, ["b", "c"]])

        assert node_left_list.list_node == ["b", "c"] == node_right_list.list_node
        assert node_left_list.data_node == data_var == node_right_list.data_node
        assert node_left_list.child_nodes == [] == node_right_list.child_nodes
        assert node_left_list == node_right_list

    def test_child_registration_inner(self):
        data_var = DataVarNode("a")
        merge = ArrayMergeNode(["a", "b"])
        node = ArrayInNode([merge, data_var])

        assert node.list_node == merge
        assert node.data_node == data_var
        assert node.child_nodes == [merge]

    def test_statements_list(self):
        data_var = DataVarNode("data_var")
        data_list = ["a", "b", 123, "c"]
        node = ArrayInNode([data_list, data_var])

        assert node.to_asp(with_comment=True) == [
            "% data_var IN (a, b, 123, c)",
            "in(mock2) :- var(s38bb977078c0e5ba5b0b759cf506cc4c, I), I = (s0cc175b9c0f1b6a831c399e269772661;"
            "s92eb5ffee6ae2fec3ad71c777531578f;123;s4a8a08f09d37b73795649038408b5f33).",
        ]

    def test_statements_node(self):
        data_node = ArrayMergeNode(["a"])
        data_var = DataVarNode("data_var")
        node = ArrayInNode([data_node, data_var])

        assert node.to_asp(with_comment=True) == [
            "% Merge (a)",
            "merge(mock1, M) :- M = (s0cc175b9c0f1b6a831c399e269772661).",
            "% data_var IN (MERGE(mock1))",
            "in(mock3) :- var(s38bb977078c0e5ba5b0b759cf506cc4c, I), merge(mock1, I).",
        ]

    def test_str(self):
        data_var = DataVarNode("a")  # mock1
        node = ArrayInNode([[], data_var])  # mock2
        assert str(node) == "IN(mock2)"

    def test_hash_list(self):
        data_var = DataVarNode("var")
        data_list = ["a", "b", "c"]
        node1 = ArrayInNode([data_list, data_var])
        node2 = ArrayInNode([data_var, ["b", "a", "c"]])
        node3 = ArrayInNode([["a", "b"], data_var])

        assert hash(node1) == hash(("in", hash(data_var), hash(tuple(sorted(data_list))))) == hash(node2)
        assert node1 == node2 != node3

    def test_hash_node(self):
        data_var = DataVarNode("var")
        data_node = ArrayMergeNode(["a", "b", "c"])
        node1 = ArrayInNode([data_node, data_var])
        node2 = ArrayInNode([data_var, data_node])
        node3 = ArrayInNode([["a", "b", "c"], data_var])

        assert hash(node1) == hash(("in", hash(data_var), hash(data_node))) == hash(node2)
        assert node1 == node2 != node3
