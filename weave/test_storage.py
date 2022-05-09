import numpy as np
import json
import pytest
import re

import wandb

from . import api as weave
from . import weave_types as types
from . import storage
from .weave_internal import make_const_node


class SomeObj:
    def __init__(self, some_int, some_str):
        self.some_int = some_int
        self.some_str = some_str


class SomeObjType(weave.types.ObjectType):
    instance_class = SomeObj
    instance_classes = SomeObj

    name = "test-storage-someobj"

    def property_types(self):
        return {
            "some_int": weave.types.Int(),
            "some_str": weave.types.String(),
        }


class SomeCustomObj:
    def __init__(self, obj):
        self.obj = obj


class SomeCustomObjType(types.Type):
    name = "test-storage-somecustomobj"
    instance_classes = SomeCustomObj
    instance_class = SomeCustomObj

    def save_instance(self, obj, artifact, name):
        with artifact.new_file(f"{name}.json") as f:
            json.dump(obj.obj, f)

    @classmethod
    def load_instance(cls, artifact, name, extra=None):
        with artifact.open(f"{name}.json") as f:
            return SomeCustomObj(json.load(f))


def test_dict():
    obj = {"x": 14}
    obj_id = storage.save(obj, "my-dict")
    obj2 = storage.get(obj_id)
    assert obj == obj2


def test_nested_dict():
    obj = {"a": 1, "b": {"c": 2}}
    obj_id = storage.save(obj, "my-dict")
    obj2 = storage.get(obj_id)
    assert obj == obj2


def test_doubly_nested_dict():
    np_array = np.array([[4, 5], [6, 7]])
    obj = {"a": np_array, "b": {"c": np_array, "d": 3}}
    obj_id = storage.save(obj, "my-dict")
    obj2 = storage.get(obj_id)
    assert obj.keys() == obj2.keys()
    assert np.array_equal(obj["a"], obj2["a"])
    assert np.array_equal(obj["b"]["c"], obj2["b"]["c"])
    assert obj["b"]["d"] == obj2["b"]["d"]


def test_list_with_arrays():
    obj = [{"a": np.array([4, 5]), "b": "b0"}, {"a": np.array([9, 10]), "b": "b1"}]
    obj_id = storage.save(obj, "my-list-with-arrays")
    obj2 = storage.get(obj_id)
    assert np.array_equal(obj[0]["a"], obj2[0]["a"])
    assert np.array_equal(obj[1]["a"], obj2[1]["a"])
    assert obj[0]["b"] == obj[0]["b"]
    assert obj[1]["b"] == obj[1]["b"]


def test_numpy():
    np_array = np.array([[4, 5], [6, 7]])
    obj_id = storage.save(np_array, "my-arr")
    np_array2 = storage.get(obj_id)
    assert np.array_equal(np_array, np_array2)


def test_custom_obj():
    obj = SomeCustomObj({"a": 5})
    obj_id = storage.save(obj, "my-obj")
    obj2 = storage.get(obj_id)
    assert obj.obj == obj2.obj


@pytest.mark.skip(reason="wb table doesnt work right now")
def test_wandb_table():
    obj = SomeCustomObj({"a": 5})
    obj_id = storage.save(obj, "my-obj")
    obj2 = storage.get(obj_id)
    assert obj.obj == obj2.obj
    table = wandb.Table(["x", "y"])
    table.add_data(1, 2)
    table_id = storage.save(table, "my-table")
    table2 = storage.get(table_id)
    assert table._eq_debug(table2)


@pytest.mark.skip(reason="cross obj refs dont work right now")
def test_cross_obj_ref():
    d1 = {"a": 5, "b": SomeCustomObj(14)}
    d1_id = storage.save(d1, "my-d1")
    d2 = storage.get(d1_id)
    d3 = {"f": 5, "c": d2["b"]}
    d3_id = storage.save(d3, "my-d3")
    d4 = storage.get(d3_id)
    assert d4.keys() == d3.keys()
    assert d3["f"] == d4["f"]
    assert d3["c"].obj == d4["c"].obj


@pytest.mark.skip(reason="cross obj refs dont work right now")
def test_cross_obj_outer_ref():
    d1 = {"a": 5, "b": SomeCustomObj(14)}
    d1_id = storage.save(d1, "my-d1")
    d2 = storage.get(d1_id)
    d3 = {"f": 5, "c": d2}
    d3_id = storage.save(d3, "my-d3")
    d4 = storage.get(d3_id)
    assert d4.keys() == d3.keys()
    assert d3["f"] == d4["f"]
    assert d3["c"]["a"] == d4["c"]["a"]
    assert d3["c"]["b"].obj == d4["c"]["b"].obj


def test_ref_type():
    obj = {"x": 14}
    ref = storage.save(obj, "my-dict")
    python_ref = storage.to_python(ref)
    assert python_ref == {
        "_type": {
            "objectType": {"propertyTypes": {"x": "int"}, "type": "typedDict"},
            "type": "ref-type",
        },
        "_val": "my-dict/6036cbf3a05809f1a3f174a1485b1770",
    }
    ref2 = storage.from_python(python_ref)
    obj2 = storage.deref(ref2)
    assert obj == obj2


def test_trace():
    nine = make_const_node(storage.types.Number(), 9)
    res = weave.use((nine + 3) * 4)
    assert res == 48
    mult_run = storage.get_obj_creator(storage._get_ref(res))
    assert mult_run._op_name == "number-mult"
    assert re.match("run-number-add-.*-output/.*$", str(mult_run._inputs["lhs"]))
    assert mult_run._inputs["rhs"] == 4
    add_run = storage.get_obj_creator(mult_run._inputs["lhs"])
    assert add_run._op_name == "number-add"
    assert add_run._inputs == {"lhs": 9, "rhs": 3}


def test_boxing():
    ref = storage.save(5)
    val = storage.get(str(ref))
    assert val == 5
    assert val._ref is not None


def test_saveload_type():
    t = types.TypedDict({"a": types.Int(), "b": types.String()})
    t_type = types.TypeRegistry.type_of(t)
    ref = storage.save(t)
    t2 = ref.get()
    assert t == t2


def test_list_obj():
    list_obj = [SomeObj(1, "a"), SomeObj(2, "b")]
    ref = storage.save(list_obj, "my-listobj")
    list_obj2 = storage.get(ref)
    assert list_obj[0].some_int == list_obj2[0].some_int
    assert list_obj[0].some_str == list_obj2[0].some_str
    assert list_obj[1].some_int == list_obj2[1].some_int
    assert list_obj[1].some_str == list_obj2[1].some_str
