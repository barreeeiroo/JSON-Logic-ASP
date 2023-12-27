from typing import Any, Iterable, Set


def remove_duplicates(seq: Iterable[Any]):
    """
    Removes duplicate entries from a sequence, preserving the first seen order.
    :param seq: iterable sequence with duplicates
    :return: copy of sequence without duplicates
    """
    seen: Set[Any] = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
