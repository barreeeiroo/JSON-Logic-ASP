from json_logic_asp.utils.list_utils import remove_duplicates


def test_remove_duplicates_no_dups():
    assert remove_duplicates(["a", "b", "c"]) == ["a", "b", "c"]


def test_remove_duplicates_dups():
    assert remove_duplicates(["a", "b", "a", "c"]) == ["a", "b", "c"]


def test_remove_duplicates_dups_multitype():
    assert remove_duplicates(["1", "2", "1", "3", 2, "4"]) == ["1", "2", "3", 2, "4"]
