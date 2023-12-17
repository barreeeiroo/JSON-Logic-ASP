from json_logic_asp.simplifier.node_simplifier import simplify_and_or_nodes


def test_simplify_and_or_nodes_obj_input():
    result = simplify_and_or_nodes("and", {"==": [{"var": "a"}, "b"]})
    assert result == {"==": [{"var": "a"}, "b"]}


def test_simplify_and_or_nodes_single_node():
    result = simplify_and_or_nodes("and", [{"==": [{"var": "a"}, "b"]}])
    assert result == {"==": [{"var": "a"}, "b"]}


def test_simplify_and_or_nodes_multiple_nodes():
    result = simplify_and_or_nodes("and",
                                   [{"==": [{"var": "a"}, "b"]}, {"==": [{"var": "c"}, "d"]}])
    assert result == {"and": [{"==": [{"var": "a"}, "b"]}, {"==": [{"var": "c"}, "d"]}]}


def test_simplify_and_or_nodes_same_nested():
    result = simplify_and_or_nodes("and",
                                   [
                                       {"and": [
                                           {"==": [{"var": "a"}, "b"]},
                                           {"==": [{"var": "c"}, "d"]},
                                       ]},
                                       {"or": [
                                           {"==": [{"var": "e"}, "f"]},
                                           {"==": [{"var": "g"}, "h"]},
                                       ]}
                                   ])

    assert result == {"and": [
        {"==": [{"var": "a"}, "b"]},
        {"==": [{"var": "c"}, "d"]},
        {"or": [
            {"==": [{"var": "e"}, "f"]},
            {"==": [{"var": "g"}, "h"]},
        ]}
    ]}


def test_simplify_and_nodes_no_value():
    result = simplify_and_or_nodes("and", [])
    assert result is False


def test_simplify_and_nodes_one_false():
    result = simplify_and_or_nodes("and", [True, True, False])
    assert result is False


def test_simplify_or_nodes_one_true():
    result = simplify_and_or_nodes("or", [False, False, True])
    assert result is True
