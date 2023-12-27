from json_logic_asp.utils.id_management import generate_constant_string, generate_unique_id


def test_generate_unique_id():
    cuid1, cuid2 = generate_unique_id(), generate_unique_id()
    assert cuid1 != cuid2


def test_generate_constant_string():
    assert generate_constant_string("123") == "s202cb962ac59075b964b07152d234b70"
