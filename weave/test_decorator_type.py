import typing

import weave


def test_no_type_vars_in_dict():
    @weave.type()
    class TestNoTypeVarsInDictType:
        v: dict[str, int]

    assert not TestNoTypeVarsInDictType.WeaveType.type_attrs()


def test_type_var_in_dict_any():
    @weave.type()
    class TestTypeVarsInDictType:
        v: dict[str, typing.Any]

    assert len(TestTypeVarsInDictType.WeaveType.type_attrs()) == 1


def test_object_union_attr_is_variable():
    @weave.type()
    class ObjWithUnion:
        a: typing.Union[str, int]

    assert "a" in ObjWithUnion.WeaveType().type_vars()


def test_object_noneunion_attr_is_variable():
    @weave.type()
    class ObjWithUnion:
        a: weave.Node[typing.Union[str, int]]

    assert "a" in ObjWithUnion.WeaveType().type_vars()
