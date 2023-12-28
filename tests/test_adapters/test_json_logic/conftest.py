from unittest.mock import patch

import pytest


class MockedCuidGenerator:
    def __init__(self):
        self.counter = 0

    def __call__(self, *args, **kwargs):
        self.counter += 1
        return f"mock{self.counter}"


@pytest.fixture(scope="module", autouse=True)
def cuid_fixture():
    with patch("json_logic_asp.utils.id_management.cuid_generator") as _fixture:
        _fixture.side_effect = MockedCuidGenerator()
        yield _fixture
