import pytest

from json_logic_asp.adapters.json_logic.jl_array_nodes import ArrayMergeNode
from json_logic_asp.adapters.json_logic.jl_data_nodes import DataVarNode


class TestArrayMergeNode:
    def test_invalid_values(self):
        with pytest.raises(ValueError) as exc1:
            ArrayMergeNode("single_node")
        assert exc1.match("ArrayMergeNode requires list as value")

        with pytest.raises(ValueError) as exc2:
            ArrayMergeNode(["valid", None])
        assert exc2.match("ArrayMergeNode received unexpected node type")

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
