from typing import Callable

from cuid2 import cuid_wrapper

cuid_generator: Callable[[], str] = cuid_wrapper()


def generate_unique_id() -> str:
    return cuid_generator()
