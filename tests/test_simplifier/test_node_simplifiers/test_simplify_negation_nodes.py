from json_logic_asp.simplifier.node_simplifier import simplify_negation_nodes


def test_simplify_negation_nodes_empty_list():
    result = simplify_negation_nodes("!", [])
    assert result is True


def test_simplify_negation_nodes_double_neg_empty_list():
    result = simplify_negation_nodes("!!", [])
    assert result is False


def test_simplify_negation_nodes_explode_list():
    result = simplify_negation_nodes("!", [{"var": "a"}])
    assert result == {"!": {"var": "a"}}


def test_simplify_negation_nodes_falsy_primitive():
    result = simplify_negation_nodes("!", "")
    assert result is True


def test_simplify_negation_nodes_truthy_primitive():
    result = simplify_negation_nodes("!", 1)
    assert result is False


def test_simplify_negation_nodes_double_neg_truthy_primitive():
    result = simplify_negation_nodes("!!", 1)
    assert result is True


def test_simplify_negation_nodes_inner_bool_node():
    # This AND evaluates to False as no element inside it evaluates ever to True, hence its negation evaluates
    #   to True.
    result = simplify_negation_nodes("!", [{"and": []}])
    assert result is True
