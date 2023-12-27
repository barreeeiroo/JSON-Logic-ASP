from json_logic_asp.models.translator_dto import DataInput
from json_logic_asp.translator.data_generator import __flatten_data, generate_single_data_asp_definition


def test_flatten_data():
    obj = {
        "a": "b",
        "c": {
            "d": "e",
            "f": "g",
        },
        "h": "i",
        "j": ["k", "l", {"m": "n"}],
        "o": "p",
    }

    expected = {
        "a": "b",
        "c.d": "e",
        "c.f": "g",
        "h": "i",
        "j.0": "k",
        "j.1": "l",
        "j.2_m": "n",
        "o": "p",
    }

    assert __flatten_data(obj) == expected


def test_generate_single_data_asp_definition():
    di = DataInput(
        data_object={
            "a": "b",
            "c": {
                "d": "e",
            },
        }
    )

    l0 = "var(s0cc175b9c0f1b6a831c399e269772661, s92eb5ffee6ae2fec3ad71c777531578f)."
    l1 = "var(se093e60cd3981d0482ad2424b965c171, se1671797c52e15f763380b45e841ec32)."

    expected = f"{l0}\n{l1}"

    assert generate_single_data_asp_definition(di, with_comments=False) == expected


def test_generate_single_data_asp_definition_with_comments():
    di = DataInput(
        data_object={
            "a": "b",
            "c": {
                "d": "e",
            },
        }
    )

    c0 = "% a : b"
    l0 = "var(s0cc175b9c0f1b6a831c399e269772661, s92eb5ffee6ae2fec3ad71c777531578f)."
    c1 = "% c.d : e"
    l1 = "var(se093e60cd3981d0482ad2424b965c171, se1671797c52e15f763380b45e841ec32)."

    expected = f"{c0}\n{l0}\n{c1}\n{l1}"

    assert generate_single_data_asp_definition(di, with_comments=True) == expected
