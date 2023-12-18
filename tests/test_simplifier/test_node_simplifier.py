import inspect
from unittest.mock import MagicMock, patch

from json_logic_asp.simplifier.node_simplifier import SIMPLIFIABLE_OPERATIONS, simplify_node


def test_simplify_node_known_operation():
    mock_simplifier = MagicMock()
    mock_simplifier.return_value = None

    with patch.dict(SIMPLIFIABLE_OPERATIONS, {"dummy": mock_simplifier}, clear=True):
        simplify_node({"dummy": []})

    mock_simplifier.assert_called_once()


def test_simplify_node_unknown_operation():
    mock_simplifier = MagicMock()

    with patch.dict(SIMPLIFIABLE_OPERATIONS, {"dummy2": mock_simplifier}, clear=True):
        simplify_node({"dummy": []})

    mock_simplifier.assert_not_called()


def test_simplifiable_operations_functions():
    for key, method in SIMPLIFIABLE_OPERATIONS.items():
        assert isinstance(key, str)
        method_sig_params = inspect.signature(method).parameters
        assert len(method_sig_params) == 2
        assert "node_key" in method_sig_params and "node_values" in method_sig_params
