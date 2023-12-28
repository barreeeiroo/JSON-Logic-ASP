import hashlib
from typing import Callable

from cuid2 import cuid_wrapper

cuid_generator: Callable[[], str] = cuid_wrapper()


def generate_unique_id() -> str:
    return cuid_generator()


def generate_constant_string(s: str) -> str:
    return f"s{hashlib.md5(s.encode()).hexdigest()}"  # nosec B303 B324
