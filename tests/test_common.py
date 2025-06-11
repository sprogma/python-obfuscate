import common
import pytest
import copy
from pprint import pformat


"""
    Must use [common.jsd()] instead of simple common.jsd(),
    becouse pytest raises exception in _idval_from_value: elif isinstance(getattr(val, "__name__", None), str):  KeyError: '__name__'
    may be it is check on module, but common.jsd uses __setattr__ method,
    and give error on this line.
"""



@pytest.mark.parametrize("constructor, expected", [
    ([common.jsd({"a": "b"})], [common.jsd(a = "b")]),
    ([common.jsd({"a": "b", "c": {"d": 1}})], [common.jsd(a = "b", c = {"d": 1})]),
])
def test_CommonJsd_constructor_1(constructor, expected):
    assert constructor[0] == expected[0], f"Expected: {str(constructor[0])} == {str(expected[0])}."




@pytest.mark.parametrize("input_data, expected", [
    (
        [
            {"a": ("b", ["c", {"x":"y"}]), "e": ("f",{"x":"y"}), "h":common.jsd(z=(1, {"x":"y"}))}
        ], [
            common.jsd(
                a = ("b", ["c", common.jsd(x="y")]),
                e = ("f", common.jsd(x="y")),
                h = common.jsd(
                    z = (1, common.jsd(x="y"))
                )
            )
        ]),
])
def test_CommonJsd_recurse_1(input_data, expected):
    assert common.jsd.recurse(input_data[0]) == expected[0], f"Expected: {str(common.jsd.recurse(input_data[0]))} == {str(expected[0])}."



def test_CommonJsd_interation_1():
    a = common.jsd()

    a.x = 1
    a.y = 2

    assert a.x + a.y == 3

    a.x = 3

    assert a.x == 3

    assert a == {"x": 3, "y": 2}

    b = a

    b.x = 4

    assert a.x == 4

    assert a is b




def test_CommonJsd_deepcopy_1():
    a = common.jsd()

    a.x = 1
    a.y = common.jsd(x=1,y=2)
    a.z = {"x": 1, "y": 2}

    b = copy.copy(a)

    assert a is not b
    assert a.y is b.y
    assert a.z is b.z

    c = copy.deepcopy(a)

    assert a is not c
    assert a.y is not c.y
    assert a.z is not c.z


