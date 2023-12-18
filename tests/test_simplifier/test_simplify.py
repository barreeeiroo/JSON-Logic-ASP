from unittest.mock import patch

import pytest

from json_logic_asp.simplifier.simplify import simplify_json_logic


def test_simplify_json_logic():
    with patch("json_logic_asp.simplifier.simplify.simplify_node") as mock_simplify_node:
        simplify_json_logic({"and": [{"var": "a"}, "b"]})

    mock_simplify_node.assert_called_once()


def test_simplify_json_logic_invalid():
    with patch("json_logic_asp.simplifier.simplify.simplify_node") as mock_simplify_node:
        with pytest.raises(ValueError):
            simplify_json_logic(True)

    mock_simplify_node.assert_not_called()
