from typing import Iterable


def remove_duplicates(seq: Iterable):
    """
    Removes duplicate entries from a sequence, preserving the first seen order.
    :param seq: iterable sequence with duplicates
    :return: copy of sequence without duplicates
    """
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
