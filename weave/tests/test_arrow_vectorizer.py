import pytest
import typing

from .. import box
from ..ops_primitives import Number, Boolean
from .. import api as weave
from .. import ops
from .. import weave_types as types
from .. import weave_internal
from ..ops_primitives import dict_, list_

from ..language_features.tagging import tag_store, tagged_value_type, make_tag_getter_op

from .. import ops_arrow as arrow


string_ops_test_cases = [
    ("eq-scalar", lambda x: x == "bc", [True, False, False]),
    ("ne-scalar", lambda x: x != "bc", [False, True, True]),
    ("contains-scalar", lambda x: x.__contains__("b"), [True, False, False]),
    ("in-scalar", lambda x: x.in_("bcd"), [True, True, False]),
    ("len-scalar", lambda x: x.len(), [2, 2, 2]),
    ("add-scalar", lambda x: x + "q", ["bcq", "cdq", "dfq"]),
    ("append-scalar", lambda x: x.append("qq"), ["bcqq", "cdqq", "dfqq"]),
    ("prepend-scalar", lambda x: x.prepend("qq"), ["qqbc", "qqcd", "qqdf"]),
    ("split-scalar", lambda x: x.split("c"), [["b", ""], ["", "d"], ["df"]]),
    (
        "partition-scalar",
        lambda x: x.partition("c"),
        [["b", "c", ""], ["", "c", "d"], ["df", "", ""]],
    ),
    ("startswith-scalar", lambda x: x.startswith("b"), [True, False, False]),
    ("endswith-scalar", lambda x: x.endswith("f"), [False, False, True]),
    ("replace-scalar", lambda x: x.replace("c", "q"), ["bq", "qd", "df"]),
    ("nest-list", lambda x: list_.make_list(a=x), [["bc"], ["cd"], ["df"]]),
    ("nest-dict", lambda x: dict_(a=x), [{"a": "bc"}, {"a": "cd"}, {"a": "df"}]),
]


@pytest.mark.parametrize(
    "name,weave_func,expected_output",
    string_ops_test_cases
    + [
        ("pick", lambda x: dict_(bc=1, cd=2, df=3)[x], [1, 2, 3]),
    ],
)
def test_arrow_vectorizer_string_scalar(name, weave_func, expected_output):
    l = weave.save(arrow.to_arrow(["bc", "cd", "df"]))
    fn = weave_internal.define_fn({"x": weave.types.String()}, weave_func).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"x": l})
    assert list(weave.use(called)) == expected_output


@pytest.mark.parametrize(
    "name,weave_func,expected_output",
    string_ops_test_cases,
)
def test_arrow_vectorizer_string_scalar_tagged(name, weave_func, expected_output):

    expected_value_type = weave.type_of(expected_output[0])

    list = ["bc", "cd", "df"]
    for i, elem in enumerate(list):
        taggable = box.box(elem)
        list[i] = tag_store.add_tags(taggable, {"mytag": f"test{i + 1}"})

    tag_getter_op = make_tag_getter_op.make_tag_getter_op("mytag", types.String())

    awl = arrow.to_arrow(list)
    l = weave.save(awl)
    fn = weave_internal.define_fn({"x": awl.object_type}, weave_func).val
    vec_fn = arrow.vectorize(fn)

    called = weave_internal.call_fn(vec_fn, {"x": l})
    assert weave.use(called).to_pylist_notags() == expected_output

    item_node = arrow.ops.index(called, 0)

    def make_exp_tag(t: types.Type):
        return tagged_value_type.TaggedValueType(
            types.TypedDict({"mytag": types.String()}),
            t,
        )

    expected_type_obj_type = make_exp_tag(expected_value_type)
    # The general test here is not general enough to check these properly.
    # Specifcially, the general test assumes the vecotrize lambdas contians all
    # tag flow ops. However, list and dict constructors are explicitly (and
    # correctly) not tag flow ops and therefore the tags are only present on the
    # elements of the list and dict.
    if name == "nest-dict":
        item_node = item_node["a"]
        expected_type_obj_type = types.TypedDict(
            {
                "a": make_exp_tag(expected_value_type.property_types["a"]),
                **expected_value_type.property_types,
            }
        )
    elif name == "nest-list":
        item_node = item_node[0]
        expected_type_obj_type = types.List(
            make_exp_tag(expected_value_type.object_type)
        )

    # check that tags are propagated
    assert weave.use(tag_getter_op(item_node)) == "test1"

    # NOTE: This optionality is needed because some arrow ops eagerly declare
    # optional returns. See number.py and string.py for commentary on the subject.
    assert arrow.ArrowWeaveListType(types.optional(expected_type_obj_type)).assign_type(
        called.type
    )


string_alnum_test_cases = [
    (
        "isAlpha-scalar",
        lambda x: x.isalpha(),
        [False, True, False, False, False, False],
    ),
    (
        "isNumeric-scalar",
        lambda x: x.isnumeric(),
        [False, False, False, True, False, False],
    ),
    (
        "isAlnum-scalar",
        lambda x: x.isalnum(),
        [False, True, True, True, False, False],
    ),
    (
        "lower-scalar",
        lambda x: x.lower(),
        ["b22?c", "cd", "df2", "212", "", "?>!@#"],
    ),
    (
        "upper-scalar",
        lambda x: x.upper(),
        ["B22?C", "CD", "DF2", "212", "", "?>!@#"],
    ),
    (
        "slice-scalar",
        lambda x: x.slice(1, 2),
        ["2", "d", "F", "1", "", ">"],
    ),
]


@pytest.mark.parametrize("name,weave_func,expected_output", string_alnum_test_cases)
def test_arrow_vectorizer_string_alnum(name, weave_func, expected_output):
    l = weave.save(arrow.to_arrow(["B22?c", "cd", "DF2", "212", "", "?>!@#"]))
    fn = weave_internal.define_fn({"x": weave.types.String()}, weave_func).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"x": l})
    assert weave.use(called).to_pylist_raw() == expected_output


@pytest.mark.parametrize(
    "name,weave_func,expected_output",
    string_alnum_test_cases,
)
def test_arrow_vectorizer_string_alnum_tagged(name, weave_func, expected_output):

    # NOTE: This optionality is needed because some arrow ops eagerly declare
    # optional returns. See number.py and string.py for commentary on the subject.
    expected_value_type = types.optional(weave.type_of(expected_output[0]))

    list = ["B22?c", "cd", "DF2", "212", "", "?>!@#"]
    for i, elem in enumerate(list):
        taggable = box.box(elem)
        list[i] = tag_store.add_tags(taggable, {"mytag": f"test{i + 1}"})

    tag_getter_op = make_tag_getter_op.make_tag_getter_op("mytag", types.String())

    awl = arrow.to_arrow(list)
    l = weave.save(awl)
    fn = weave_internal.define_fn({"x": awl.object_type}, weave_func).val
    vec_fn = arrow.vectorize(fn)

    called = weave_internal.call_fn(vec_fn, {"x": l})
    assert weave.use(called).to_pylist_notags() == expected_output

    # check that tags are propagated
    assert weave.use(tag_getter_op(arrow.ops.index(called, 0))) == "test1"

    assert arrow.ArrowWeaveListType(
        tagged_value_type.TaggedValueType(
            types.TypedDict({"mytag": types.String()}),
            expected_value_type,
        )
    ).assign_type(called.type)


@pytest.mark.parametrize(
    "name,weave_func,expected_output",
    [
        ("strip-scalar", lambda x: x.strip(), ["c", "cd", "DF2", "212", ""]),
        ("lstrip-scalar", lambda x: x.lstrip(), ["c ", "cd", "DF2", "212 ", ""]),
        ("rstrip-scalar", lambda x: x.rstrip(), ["  c", "cd", " DF2", "212", ""]),
    ],
)
def test_arrow_vectorizer_string_strip(name, weave_func, expected_output):
    l = weave.save(arrow.to_arrow(["  c ", "cd", " DF2", "212 ", ""]))
    fn = weave_internal.define_fn({"x": weave.types.String()}, weave_func).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"x": l})
    assert weave.use(called).to_pylist_raw() == expected_output


number_ops_test_cases = [
    ("add", lambda x: x + 2, [3.0, 4.0, 5.0]),
    ("add-vec", lambda x: x + x, [2.0, 4.0, 6.0]),
    ("subtract", lambda x: x - 1, [0.0, 1.0, 2.0]),
    ("multiply", lambda x: x * 2, [2.0, 4.0, 6.0]),
    ("divide", lambda x: x / 2, [0.5, 1.0, 1.5]),
    ("pow", lambda x: x**2, [1.0, 4.0, 9.0]),
    ("ne", lambda x: x != 2, [True, False, True]),
    ("eq", lambda x: x == 2, [False, True, False]),
    ("gt", lambda x: x > 2, [False, False, True]),
    ("lt", lambda x: x < 2, [True, False, False]),
    ("ge", lambda x: x >= 2, [False, True, True]),
    ("le", lambda x: x <= 2, [True, True, False]),
    ("neg", lambda x: -x, [-1.0, -2.0, -3.0]),
    ("toString", lambda x: x.toString(), ["1", "2", "3"]),
]


@pytest.mark.parametrize(
    "name,weave_func,expected_output",
    number_ops_test_cases,
)
def test_arrow_vectorizer_number_ops(name, weave_func, expected_output):
    l = weave.save(arrow.to_arrow([1.0, 2.0, 3.0]))

    fn = weave_internal.define_fn({"x": weave.types.Float()}, weave_func).val

    vec_fn = arrow.vectorize(fn)

    # TODO:  make it nicer to call vec_fn, we shouldn't need to jump through hoops here

    called = weave_internal.call_fn(vec_fn, {"x": l})

    assert weave.use(called).to_pylist_raw() == expected_output


@pytest.mark.parametrize(
    "name,weave_func,expected_output",
    number_ops_test_cases,
)
def test_arrow_vectorizer_number_ops_tagged(name, weave_func, expected_output):

    expected_value_type = weave.type_of(expected_output[0])

    # This special condition is needed because the expected output is a list of
    # booleans is optional booleans. See the comment at the top of `ops_arrow/number.py`
    # for more details.
    if types.Boolean().assign_type(expected_value_type):
        expected_value_type = types.optional(expected_value_type)

    list = [1.0, 2.0, 3.0]
    for i, elem in enumerate(list):
        taggable = box.box(elem)
        list[i] = tag_store.add_tags(taggable, {"mytag": f"test{i + 1}"})

    tag_getter_op = make_tag_getter_op.make_tag_getter_op("mytag", types.String())

    awl = arrow.to_arrow(list)
    l = weave.save(awl)
    fn = weave_internal.define_fn({"x": awl.object_type}, weave_func).val
    vec_fn = arrow.vectorize(fn)

    called = weave_internal.call_fn(vec_fn, {"x": l})
    assert weave.use(called).to_pylist_notags() == expected_output

    # check that tags are propagated
    assert weave.use(tag_getter_op(arrow.ops.index(called, 0))) == "test1"

    assert arrow.ArrowWeaveListType(
        tagged_value_type.TaggedValueType(
            types.TypedDict({"mytag": types.String()}),
            expected_value_type,
        )
    ).assign_type(called.type)


string_vector_ops_test_cases = [
    ("eq-vector", lambda x, y: x == y, [False, False, True]),
    ("ne-vector", lambda x, y: x != y, [True, True, False]),
    ("contains-vector", lambda x, y: x.__contains__(y), [False, False, True]),
    ("in-vector", lambda x, y: x.in_(y), [True, False, True]),
    ("add-vector", lambda x, y: x + y, ["bccbc", "cdaef", "dfdf"]),
    ("append-vector", lambda x, y: x.append(y), ["bccbc", "cdaef", "dfdf"]),
    ("prepend-vector", lambda x, y: x.prepend(y), ["cbcbc", "aefcd", "dfdf"]),
    ("split-vector", lambda x, y: y.split(x), [["c", ""], ["aef"], ["", ""]]),
    (
        "partition-vector",
        lambda x, y: y.partition(x),
        [["c", "bc", ""], ["aef", "", ""], ["", "df", ""]],
    ),
    (
        "startswith-vector",
        lambda x, y: y.startswith(x),
        [False, False, True],
    ),
    ("endswith-vector", lambda x, y: y.endswith(x), [True, False, True]),
]


@pytest.mark.parametrize(
    "name,weave_func,expected_output", string_vector_ops_test_cases
)
def test_arrow_vectorizer_string_vector(name, weave_func, expected_output):
    l = weave.save(arrow.to_arrow(["bc", "cd", "df"]))
    l2 = weave.save(arrow.to_arrow(["cbc", "aef", "df"]))

    fn = weave_internal.define_fn(
        {"x": weave.types.String(), "y": weave.types.String()}, weave_func
    ).val

    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"x": l, "y": l2})
    assert weave.use(called).to_pylist_raw() == expected_output


@pytest.mark.parametrize(
    "name,weave_func,expected_output",
    string_vector_ops_test_cases,
)
def test_arrow_vectorizer_string_vector_ops_tagged(name, weave_func, expected_output):

    # NOTE: This optionality is needed because some arrow ops eagerly declare
    # optional returns. See number.py and string.py for commentary on the subject.
    expected_value_type = types.optional(weave.type_of(expected_output[0]))

    list = ["bc", "cd", "df"]
    for i, elem in enumerate(list):
        taggable = box.box(elem)
        list[i] = tag_store.add_tags(taggable, {"mytag": f"test{i + 1}"})

    list2 = ["cbc", "aef", "df"]
    for i, elem in enumerate(list2):
        taggable = box.box(elem)
        list2[i] = tag_store.add_tags(taggable, {"mytag2": f"test{i + 1}"})

    awl = arrow.to_arrow(list)
    awl2 = arrow.to_arrow(list2)

    l = weave.save(awl)
    l2 = weave.save(awl2)
    fn = weave_internal.define_fn(
        {"x": awl.object_type, "y": awl2.object_type}, weave_func
    ).val
    vec_fn = arrow.vectorize(fn)

    called = weave_internal.call_fn(vec_fn, {"x": l, "y": l2})
    assert weave.use(called).to_pylist_notags() == expected_output

    # if x is first, expect x tag to be propagated. if y is first, expect y tag to be propagated.
    tag_name: typing.Optional[str] = None
    for name, node in called.iteritems_op_inputs():
        if name == "self":
            tag_name = next(k for k in node.type.object_type.tag.property_types)

    if tag_name is None:
        raise ValueError("tag_getter_op not found")

    tag_getter_op = make_tag_getter_op.make_tag_getter_op(
        tag_name,
        types.String(),
    )

    # check that tags are propagated
    assert weave.use(tag_getter_op(arrow.ops.index(called, 0))) == "test1"

    assert arrow.ArrowWeaveListType(
        tagged_value_type.TaggedValueType(
            types.TypedDict({tag_name: types.String()}),
            expected_value_type,
        )
    ).assign_type(called.type)


nullable_number_ops_test_cases = [
    ("add", lambda x: x + 2, [3.0, None, 5.0]),
    ("add-vec", lambda x: x + x, [2.0, None, 6.0]),
    ("subtract", lambda x: x - 1, [0.0, None, 2.0]),
    ("multiply", lambda x: x * 2, [2.0, None, 6.0]),
    ("divide", lambda x: x / 2, [0.5, None, 1.5]),
    ("pow", lambda x: x**2, [1.0, None, 9.0]),
    ("ne", lambda x: x != 2, [True, True, True]),
    ("eq", lambda x: x == 2, [False, False, False]),
    ("gt", lambda x: x > 2, [False, None, True]),
    ("lt", lambda x: x < 2, [True, None, False]),
    ("ge", lambda x: x >= 2, [False, None, True]),
    ("le", lambda x: x <= 2, [True, None, False]),
    ("neg", lambda x: -x, [-1.0, None, -3.0]),
    ("toString", lambda x: x.toString(), ["1", None, "3"]),
]


@pytest.mark.parametrize(
    "name,weave_func,expected_output",
    nullable_number_ops_test_cases,
)
def test_arrow_vectorizer_nullable_number_ops(name, weave_func, expected_output):
    l = weave.save(arrow.to_arrow([1.0, None, 3.0]))

    fn = weave_internal.define_fn({"x": weave.types.Float()}, weave_func).val

    vec_fn = arrow.vectorize(fn)

    # TODO:  make it nicer to call vec_fn, we shouldn't need to jump through hoops here

    called = weave_internal.call_fn(vec_fn, {"x": l})

    assert weave.use(called).to_pylist_raw() == expected_output


string_ops_nullable_test_cases = [
    ("eq-scalar", lambda x: x == "bc", [True, False, False]),
    ("ne-scalar", lambda x: x != "bc", [False, True, True]),
    ("contains-scalar", lambda x: x.__contains__("b"), [True, None, False]),
    ("in-scalar", lambda x: x.in_("bcd"), [True, None, False]),
    ("len-scalar", lambda x: x.len(), [2, None, 2]),
    ("add-scalar", lambda x: x + "q", ["bcq", None, "dfq"]),
    ("append-scalar", lambda x: x.append("qq"), ["bcqq", None, "dfqq"]),
    ("prepend-scalar", lambda x: x.prepend("qq"), ["qqbc", None, "qqdf"]),
    ("split-scalar", lambda x: x.split("c"), [["b", ""], None, ["df"]]),
    (
        "partition-scalar",
        lambda x: x.partition("c"),
        [["b", "c", ""], None, ["df", "", ""]],
    ),
    ("startswith-scalar", lambda x: x.startswith("b"), [True, None, False]),
    ("endswith-scalar", lambda x: x.endswith("f"), [False, None, True]),
    ("replace-scalar", lambda x: x.replace("c", "q"), ["bq", None, "df"]),
    ("nest-list", lambda x: list_.make_list(a=x), [["bc"], [None], ["df"]]),
    ("nest-dict", lambda x: dict_(a=x), [{"a": "bc"}, {"a": None}, {"a": "df"}]),
]


@pytest.mark.parametrize(
    "name,weave_func,expected_output",
    string_ops_nullable_test_cases,
)
def test_arrow_vectorizer_string_nullable_scalar_ops_tagged(
    name, weave_func, expected_output
):
    expected_value_type = weave.type_of(expected_output).object_type

    list = ["bc", None, "df"]
    for i, elem in enumerate(list):
        taggable = box.box(elem)
        list[i] = tag_store.add_tags(taggable, {"mytag": f"test{i + 1}"})

    tag_getter_op = make_tag_getter_op.make_tag_getter_op("mytag", types.String())

    awl = arrow.to_arrow(list)
    l = weave.save(awl)
    fn = weave_internal.define_fn({"x": awl.object_type}, weave_func).val
    vec_fn = arrow.vectorize(fn)

    print("VEC", vec_fn)
    called = weave_internal.call_fn(vec_fn, {"x": l})
    print("CALLED TYPE", called.type)
    assert weave.use(called).to_pylist_notags() == expected_output

    item_node = arrow.ops.index(called, 0)

    def make_exp_tag(t: types.Type):
        return tagged_value_type.TaggedValueType(
            types.TypedDict({"mytag": types.String()}),
            t,
        )

    expected_type_obj_type = make_exp_tag(expected_value_type)
    # The general test here is not general enough to check these properly.
    # Specifcially, the general test assumes the vecotrize lambdas contians all
    # tag flow ops. However, list and dict constructors are explicitly (and
    # correctly) not tag flow ops and therefore the tags are only present on the
    # elements of the list and dict.
    if name == "nest-dict":
        item_node = item_node["a"]
        expected_type_obj_type = types.TypedDict(
            {
                **expected_value_type.property_types,
                "a": make_exp_tag(
                    types.optional(expected_value_type.property_types["a"])
                ),
            }
        )
    elif name == "nest-list":
        item_node = item_node[0]
        expected_type_obj_type = types.List(
            make_exp_tag(types.optional(expected_value_type.object_type))
        )

    # check that tags are propagated
    assert weave.use(tag_getter_op(item_node)) == "test1"

    # NOTE: This optionality is needed because some arrow ops eagerly declare
    # optional returns. See number.py and string.py for commentary on the subject.
    assert arrow.ArrowWeaveListType(types.optional(expected_type_obj_type)).assign_type(
        called.type
    )


@pytest.mark.parametrize(
    "name,input_datal,input_datar,weave_func,expected_output",
    [
        (
            "merge",
            [{"b": "c"}, None, {"b": "q"}],
            [{"c": 4}, {"c": 5}, {"c": 6}],
            lambda x, y: x.merge(y),
            [{"b": "c", "c": 4}, None, {"b": "q", "c": 6}],
        ),
        (
            "merge-overwrite",
            [{"b": "c"}, None, {"b": "q"}],
            [{"b": "g"}, {"b": "q"}, {"b": "a"}],
            lambda x, y: x.merge(y),
            [{"b": "g"}, None, {"b": "a"}],
        ),
        (
            "merge-dicts",
            [{"b": "c"}, None, {"b": "q"}],
            [{"c": {"a": 2}}, {"c": {"a": 3}}, {"c": {"a": 4}}],
            lambda x, y: x.merge(y),
            [
                {"b": "c", "c": {"a": 2}},
                None,
                {"b": "q", "c": {"a": 4}},
            ],
        ),
    ],
)
def test_arrow_typeddict_nullable_merge(
    input_datal, input_datar, name, weave_func, expected_output
):
    l = weave.save(arrow.to_arrow(input_datal))
    r = weave.save(arrow.to_arrow(input_datar))

    fn = weave_internal.define_fn(
        {
            "x": weave.type_of(input_datal).object_type,
            "y": weave.type_of(input_datar).object_type,
        },
        weave_func,
    ).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"x": l, "y": r})
    awl = weave.use(called)
    assert awl.to_pylist_raw() == expected_output
    assert called.type == arrow.ArrowWeaveListType(
        weave.type_of(expected_output).object_type
    )
    assert awl.object_type == weave.type_of(expected_output).object_type


nullable_pick_cases = [
    (
        "pick",
        [None, {"a": 2.0, "b": "G"}, {"a": 3.0, "b": "q"}],
        lambda x: x.pick("a"),
        [None, 2.0, 3.0],
    ),
    (
        "pick-nested",
        [
            {"a": None, "c": "d"},
            {"a": {"b": 2.0}, "c": "G"},
            {"a": {"b": 3.0}, "c": "q"},
        ],
        lambda x: x.pick("a").pick("b"),
        [None, 2.0, 3.0],
    ),
]


@pytest.mark.parametrize(
    "name,input_data,weave_func,expected_output", nullable_pick_cases
)
def test_arrow_typeddict_pick_nullable(input_data, name, weave_func, expected_output):
    l = weave.save(arrow.to_arrow(input_data))
    fn = weave_internal.define_fn(
        {"x": weave.type_of(input_data).object_type}, weave_func
    ).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"x": l})
    assert weave.use(called).to_pylist_raw() == expected_output
    assert called.type == arrow.ArrowWeaveListType(
        weave.type_of(expected_output).object_type
    )


@pytest.mark.parametrize(
    "name,weave_func,expected_output",
    [
        ("floor", lambda x: Number.floor(x), [1.0, 2.0, 3.0]),
        ("ceil", lambda x: Number.ceil(x), [2.0, 3.0, 4.0]),
    ],
)
def test_arrow_floor_ceil_vectorized(name, weave_func, expected_output):
    l = weave.save(arrow.to_arrow([1.1, 2.5, 3.9]))
    fn = weave_internal.define_fn({"x": weave.types.Float()}, weave_func).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"x": l})
    assert weave.use(called).to_pylist_raw() == expected_output


pick_cases = [
    (
        "pick",
        [{"a": 1.0, "b": "c"}, {"a": 2.0, "b": "G"}, {"a": 3.0, "b": "q"}],
        lambda x: x.pick("a"),
        [1.0, 2.0, 3.0],
    ),
    (
        "pick-nested",
        [
            {"a": {"b": 1.0}, "c": "d"},
            {"a": {"b": 2.0}, "c": "G"},
            {"a": {"b": 3.0}, "c": "q"},
        ],
        lambda x: x.pick("a").pick("b"),
        [1.0, 2.0, 3.0],
    ),
]


@pytest.mark.parametrize("name,input_data,weave_func,expected_output", pick_cases)
def test_arrow_typeddict_pick(input_data, name, weave_func, expected_output):
    l = weave.save(arrow.to_arrow(input_data))
    fn = weave_internal.define_fn(
        {"x": weave.type_of(input_data).object_type}, weave_func
    ).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"x": l})
    assert weave.use(called).to_pylist_raw() == expected_output
    assert called.type == arrow.ArrowWeaveListType(
        weave.type_of(expected_output).object_type
    )


@pytest.mark.parametrize("name,input_data,weave_func,expected_output", pick_cases)
def test_arrow_typeddict_pick_tagged(input_data, name, weave_func, expected_output):

    # tag each dict and one of its values
    for i, elem in enumerate(input_data):
        taggable = box.box(elem)
        input_data[i] = tag_store.add_tags(
            taggable, {"dict_tag": f"{input_data}[{i}] = {elem}"}
        )
        input_data[i]["a"] = tag_store.add_tags(
            box.box(input_data[i]["a"]),
            {"first_level_tag": f"{input_data}[{i}]['a'] = {elem['a']}"},
        )
        if name == "pick-nested":
            input_data[i]["a"]["b"] = tag_store.add_tags(
                box.box(input_data[i]["a"]["b"]),
                {"second_level_tag": f"{input_data}[{i}]['a']['b'] = {elem['a']['b']}"},
            )

    l = weave.save(arrow.to_arrow(input_data))
    fn = weave_internal.define_fn(
        {"x": weave.type_of(input_data).object_type}, weave_func
    ).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"x": l})

    assert weave.use(called).to_pylist_notags() == expected_output
    expected_output_object_type = tagged_value_type.TaggedValueType(
        types.TypedDict(
            property_types={
                "dict_tag": types.String(),
                "first_level_tag": types.String(),
                **(
                    {"second_level_tag": types.String()}
                    if name == "pick-nested"
                    else {}
                ),
            }
        ),
        types.Float(),
    )
    assert called.type == arrow.ArrowWeaveListType(expected_output_object_type)

    tag_getter_op = make_tag_getter_op.make_tag_getter_op(
        "first_level_tag", types.String()
    )

    for i, elem in enumerate(input_data):
        tag = f"{input_data}[{i}]['a'] = {elem['a']}"
        assert weave.use(tag_getter_op(arrow.ops.index(called, i))) == tag


@pytest.mark.parametrize(
    "name,input_datal,input_datar,weave_func,expected_output",
    [
        (
            "merge",
            [{"b": "c"}, {"b": "G"}, {"b": "q"}],
            [{"c": 4}, {"c": 5}, {"c": 6}],
            lambda x, y: x.merge(y),
            [{"b": "c", "c": 4}, {"b": "G", "c": 5}, {"b": "q", "c": 6}],
        ),
        (
            "merge-overwrite",
            [{"b": "c"}, {"b": "G"}, {"b": "q"}],
            [{"b": "g"}, {"b": "q"}, {"b": "a"}],
            lambda x, y: x.merge(y),
            [{"b": "g"}, {"b": "q"}, {"b": "a"}],
        ),
        (
            "merge-dicts",
            [{"b": "c"}, {"b": "G"}, {"b": "q"}],
            [{"c": {"a": 2}}, {"c": {"a": 3}}, {"c": {"a": 4}}],
            lambda x, y: x.merge(y),
            [
                {"b": "c", "c": {"a": 2}},
                {"b": "G", "c": {"a": 3}},
                {"b": "q", "c": {"a": 4}},
            ],
        ),
    ],
)
def test_arrow_typeddict_merge(
    input_datal, input_datar, name, weave_func, expected_output
):
    l = weave.save(arrow.to_arrow(input_datal))
    r = weave.save(arrow.to_arrow(input_datar))
    fn = weave_internal.define_fn(
        {
            "x": weave.type_of(input_datal).object_type,
            "y": weave.type_of(input_datar).object_type,
        },
        weave_func,
    ).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"x": l, "y": r})
    awl = weave.use(called)
    assert awl.to_pylist_raw() == expected_output
    assert called.type == arrow.ArrowWeaveListType(
        weave.type_of(expected_output).object_type
    )
    assert awl.object_type == weave.type_of(expected_output).object_type


def test_arrow_typeddict_simple_merge_tagged():

    input_datal = [{"b": "c"}, {"b": "G"}, {"b": "q"}]
    input_datar = [{"c": 4}, {"c": 5}, {"c": 6}]
    weave_func = lambda x, y: x.merge(y)
    expected_output = [{"b": "c", "c": 4}, {"b": "G", "c": 5}, {"b": "q", "c": 6}]

    for i, elem in enumerate(input_datal):
        input_datal[i]["b"] = tag_store.add_tags(box.box(elem["b"]), {"tag": "a"})

    l = weave.save(arrow.to_arrow(input_datal))
    r = weave.save(arrow.to_arrow(input_datar))
    fn = weave_internal.define_fn(
        {
            "x": types.TypedDict({"b": types.String()}),
            "y": types.TypedDict({"c": types.Int()}),
        },
        weave_func,
    ).val
    vec_fn = arrow.vectorize(fn)
    # here we call refine graph so we can have called be a RuntimeOutputNode,
    # which allows the dispatch we us in the tag getter op assert
    called = weave_internal.refine_graph(
        weave_internal.call_fn(vec_fn, {"x": l, "y": r})
    )
    awl = weave.use(called)
    assert awl.to_pylist_notags() == expected_output

    tag_getter_op = make_tag_getter_op.make_tag_getter_op("tag", types.String())
    tag = weave.use(tag_getter_op(called[0]["b"]))
    assert tag == "a"

    assert called.type == arrow.ArrowWeaveListType(
        types.TypedDict(
            {
                "b": tagged_value_type.TaggedValueType(
                    types.TypedDict({"tag": types.String()}), types.String()
                ),
                "c": types.Int(),
            }
        )
    )


def test_arrow_typeddict_overwrite_merge_tagged():

    input_datal = [{"b": "c"}, {"b": "G"}, {"b": "q"}]
    input_datar = [{"b": "g"}, {"b": "q"}, {"b": "a"}]
    weave_func = lambda x, y: x.merge(y)
    expected_output = [{"b": "g"}, {"b": "q"}, {"b": "a"}]

    for i, elem in enumerate(input_datar):
        input_datar[i]["b"] = tag_store.add_tags(box.box(elem["b"]), {"tag": "a"})

    l = weave.save(arrow.to_arrow(input_datal))
    r = weave.save(arrow.to_arrow(input_datar))
    fn = weave_internal.define_fn(
        {
            "x": types.TypedDict({"b": types.String()}),
            "y": types.TypedDict({"b": types.String()}),
        },
        weave_func,
    ).val
    vec_fn = arrow.vectorize(fn)
    # here we call refine graph so we can have called be a RuntimeOutputNode,
    # which allows the dispatch we us in the tag getter op assert
    called = weave_internal.refine_graph(
        weave_internal.call_fn(vec_fn, {"x": l, "y": r})
    )
    awl = weave.use(called)
    assert awl.to_pylist_notags() == expected_output

    tag_getter_op = make_tag_getter_op.make_tag_getter_op("tag", types.String())
    tag = weave.use(tag_getter_op(called[0]["b"]))
    assert tag == "a"

    assert called.type == arrow.ArrowWeaveListType(
        types.TypedDict(
            {
                "b": tagged_value_type.TaggedValueType(
                    types.TypedDict({"tag": types.String()}), types.String()
                ),
            }
        )
    )


def test_arrow_typeddict_dicts_merge_tagged():
    input_datal = [{"b": "c"}, {"b": "G"}, {"b": "q"}]
    input_datar = [{"c": {"a": 2}}, {"c": {"a": 3}}, {"c": {"a": 4}}]
    weave_func = lambda x, y: x.merge(y)
    expected_output = [
        {"b": "c", "c": {"a": 2}},
        {"b": "G", "c": {"a": 3}},
        {"b": "q", "c": {"a": 4}},
    ]

    for i, elem in enumerate(input_datar):
        input_datar[i]["c"]["a"] = tag_store.add_tags(
            box.box(elem["c"]["a"]), {"tag": "a"}
        )

    l = weave.save(arrow.to_arrow(input_datal))
    r = weave.save(arrow.to_arrow(input_datar))
    fn = weave_internal.define_fn(
        {
            "x": types.TypedDict({"b": types.String()}),
            "y": types.TypedDict({"c": types.TypedDict({"a": types.Int()})}),
        },
        weave_func,
    ).val
    vec_fn = arrow.vectorize(fn)
    # here we call refine graph so we can have called be a RuntimeOutputNode,
    # which allows the dispatch we us in the tag getter op assert
    called = weave_internal.refine_graph(
        weave_internal.call_fn(vec_fn, {"x": l, "y": r})
    )
    awl = weave.use(called)
    assert awl.to_pylist_notags() == expected_output

    tag_getter_op = make_tag_getter_op.make_tag_getter_op("tag", types.String())
    tag = weave.use(tag_getter_op(called[0]["c"]["a"]))
    assert tag == "a"

    assert called.type == arrow.ArrowWeaveListType(
        types.TypedDict(
            {
                "b": types.String(),
                "c": types.TypedDict(
                    {
                        "a": tagged_value_type.TaggedValueType(
                            types.TypedDict({"tag": types.String()}), types.Int()
                        )
                    }
                ),
            }
        )
    )


def test_arrow_typeddict_nested_merge_tagged():
    """Tests that nested merging is disabled."""
    input_datal = [{"a": {"c": 1}}, {"a": {"c": 2}}, {"a": {"c": 3}}]
    input_datar = [{"a": {"b": 2}}, {"a": {"b": 4}}, {"a": {"b": 6}}]
    weave_func = lambda x, y: x.merge(y)
    expected_output = [
        {"a": {"b": 2}},
        {"a": {"b": 4}},
        {"a": {"b": 6}},
    ]

    for i, elem in enumerate(input_datal):
        input_datal[i]["a"]["c"] = tag_store.add_tags(
            box.box(elem["a"]["c"]), {"tag": "a"}
        )

    l = weave.save(arrow.to_arrow(input_datal))
    r = weave.save(arrow.to_arrow(input_datar))
    fn = weave_internal.define_fn(
        {
            "x": weave.type_of(input_datal).object_type,
            "y": weave.type_of(input_datar).object_type,
        },
        weave_func,
    ).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"x": l, "y": r})
    awl = weave.use(called)
    assert awl.to_pylist_notags() == expected_output

    assert called.type == arrow.ArrowWeaveListType(
        types.TypedDict(
            {
                "a": types.TypedDict(
                    {
                        "b": types.Int(),
                    }
                )
            }
        )
    )


def test_arrow_dict_tagged():
    to_tag = box.box([1, 2, 3])
    for i, elem in enumerate(to_tag):
        taggable = box.box(elem)
        to_tag[i] = tag_store.add_tags(taggable, {"a": f"{elem}"})
    tag_store.add_tags(to_tag, {"outer": "tag"})
    a = weave.save(arrow.to_arrow(to_tag))
    b = weave.save(arrow.to_arrow(["a", "b", "c"]))
    expected_output = [{"a": 1, "b": "a"}, {"a": 2, "b": "b"}, {"a": 3, "b": "c"}]
    weave_func = lambda a, b: ops.dict_(a=a, b=b)
    fn = weave_internal.define_fn(
        {"a": a.type.object_type, "b": b.type.object_type},
        weave_func,
    ).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"a": a, "b": b})

    # this is needed becasue the argtypes of fn do not include the tag types on a and b. so when we call
    # vec fn on a and b, the type of called does not include the tags on a and b. refining the graph
    # causes the type system to look at the types of a and b and recompute the type of called accordingly.
    called = weave_internal.refine_graph(called)
    awl = weave.use(called)
    assert awl.to_pylist_notags() == expected_output

    # tags should not flow to output list because the op has no named arguments,
    # just varargs.
    assert not isinstance(weave.type_of(awl), tagged_value_type.TaggedValueType)

    assert called.type == arrow.ArrowWeaveListType(
        types.TypedDict(
            {
                "a": tagged_value_type.TaggedValueType(
                    types.TypedDict({"outer": types.String(), "a": types.String()}),
                    types.Int(),
                ),
                "b": types.String(),
            }
        )
    )

    tag_getter_op = make_tag_getter_op.make_tag_getter_op("a", types.String())
    tag_node = tag_getter_op(called[0]["a"])
    assert weave.use(tag_node) == "1"

    tag_getter_op = make_tag_getter_op.make_tag_getter_op("outer", types.String())
    tag_node = tag_getter_op(called[0]["a"])
    assert weave.use(tag_node) == "tag"


def test_arrow_dict():
    a = weave.save(arrow.to_arrow([1, 2, 3]))
    b = weave.save(arrow.to_arrow(["a", "b", "c"]))
    expected_output = [{"a": 1, "b": "a"}, {"a": 2, "b": "b"}, {"a": 3, "b": "c"}]
    weave_func = lambda a, b: ops.dict_(a=a, b=b)
    fn = weave_internal.define_fn(
        {"a": weave.types.Int(), "b": weave.types.String()},
        weave_func,
    ).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"a": a, "b": b})
    awl = weave.use(called)
    assert awl.to_pylist_raw() == expected_output
    assert called.type == arrow.ArrowWeaveListType(
        weave.type_of(expected_output).object_type
    )
    assert awl.object_type == weave.type_of(expected_output).object_type


def test_vectorize_works_recursively_on_weavifiable_op():

    # this op is weavifiable because it just calls add
    @weave.op()
    def add_one(x: int) -> int:
        return x + 1

    weave_fn = weave_internal.define_fn(
        {"x": weave.types.Int()}, lambda x: add_one(x)
    ).val
    vectorized = arrow.vectorize(weave_fn)
    expected = vectorized.to_json()
    print("test_vectorize_works_recursively_on_weavifiable_op.expected", expected)
    assert expected == {
        "nodeType": "output",
        "type": {
            "type": "ArrowWeaveList",
            "_base_type": {"type": "list"},
            "objectType": "int",
        },
        "fromOp": {
            "name": "ArrowWeaveListNumber-add",
            "inputs": {
                "self": {
                    "nodeType": "var",
                    "type": {
                        "type": "ArrowWeaveList",
                        "_base_type": {"type": "list"},
                        "objectType": "int",
                    },
                    "varName": "x",
                },
                "other": {"nodeType": "const", "type": "int", "val": 1},
            },
        },
    }


def test_vectorize_inner_lambdas():
    l = weave.save(arrow.to_arrow([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
    inner_fn = weave_internal.define_fn(
        {"row": l.type.object_type.object_type}, lambda row: row + 1
    )
    fn = weave_internal.define_fn(
        {"row": l.type.object_type}, lambda row: row.map(inner_fn)
    ).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"row": l})
    assert list(weave.use(called)) == [[2, 3, 4], [5, 6, 7], [8, 9, 10]]


def test_unboxing_in_broadcasting():
    col1 = weave.save(arrow.to_arrow([1, 2, 3]))
    col2 = box.box(True)
    col2 = tag_store.add_tags(col2, {"col2_tag": "col2_val"})
    col2 = weave.save(col2)

    fn_body = lambda v: ops.dict_(col1=v, col2=col2)
    fn = weave_internal.define_fn({"v": types.Int()}, fn_body).val
    vectorized_fn = arrow.vectorize(fn)
    called_fn = weave_internal.call_fn(vectorized_fn, {"v": col1})
    result = weave.use(called_fn)

    answer = [
        {"col1": 1, "col2": True},
        {"col1": 2, "col2": True},
        {"col1": 3, "col2": True},
    ]

    for i in range(3):
        assert result._index(i) == answer[i]

    tag_getter = make_tag_getter_op.make_tag_getter_op("col2_tag")
    tag_getter_result = weave.use(tag_getter(arrow.ops.index(called_fn, 0)["col2"]))
    assert tag_getter_result == "col2_val"


@pytest.mark.parametrize(
    "name,weave_func,expected_output",
    [
        ("bool-and-scalar", lambda x: Boolean.bool_and(x, True), [False, None, True]),
        ("bool-or-scalar", lambda x: Boolean.bool_or(x, True), [True, None, True]),
        ("bool-not", lambda x: Boolean.bool_not(x), [True, None, False]),
    ],
)
def test_vectorized_bool_ops(name, weave_func, expected_output):
    expected_value_type = weave.type_of(expected_output).object_type

    list = [False, None, True]
    for i, elem in enumerate(list):
        taggable = box.box(elem)
        list[i] = tag_store.add_tags(taggable, {"mytag": f"test{i + 1}"})

    tag_getter_op = make_tag_getter_op.make_tag_getter_op("mytag", types.String())

    awl = arrow.to_arrow(list)
    l = weave.save(awl)
    fn = weave_internal.define_fn({"x": awl.object_type}, weave_func).val
    vec_fn = arrow.vectorize(fn)

    called = weave_internal.call_fn(vec_fn, {"x": l})
    assert weave.use(called).to_pylist_notags() == expected_output

    item_node = arrow.ops.index(called, 0)

    def make_exp_tag(t: types.Type):
        return tagged_value_type.TaggedValueType(
            types.TypedDict({"mytag": types.String()}),
            t,
        )

    expected_type_obj_type = make_exp_tag(expected_value_type)
    # check that tags are propagated
    assert weave.use(tag_getter_op(item_node)) == "test1"

    # NOTE: This optionality is needed because some arrow ops eagerly declare
    # optional returns. See number.py and string.py for commentary on the subject.
    assert arrow.ArrowWeaveListType(types.optional(expected_type_obj_type)).assign_type(
        called.type
    )


def test_vectorize_index_simple():
    l = weave.save(arrow.to_arrow([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
    fn = weave_internal.define_fn({"row": l.type.object_type}, lambda row: row[0]).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"row": l})
    assert list(weave.use(called)) == [1, 4, 7]


def test_vectorize_index_out_of_bounds():
    l = weave.save(arrow.to_arrow([[1, 2, 3], [1, 2], [4, 5, 6], [], [7, 8, 9]]))
    fn = weave_internal.define_fn({"row": l.type.object_type}, lambda row: row[2]).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"row": l})
    assert list(weave.use(called)) == [3, None, 6, None, 9]


def test_vectorize_index_nested():
    l = weave.save(arrow.to_arrow([[[1, 2, 3]], [[4, 5, 6]], [[7, 8, 9]]]))
    fn = weave_internal.define_fn(
        {"row": l.type.object_type}, lambda row: row[0][0]
    ).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"row": l})
    assert list(weave.use(called)) == [1, 4, 7]


def test_vectorize_index_dependent():
    l = weave.save(arrow.to_arrow([[1, 1, 2, 3], [2, 4, 5, 6], [3, 7, 8, 9]]))
    fn = weave_internal.define_fn(
        {"row": l.type.object_type}, lambda row: row[row[0]]
    ).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"row": l})
    assert list(weave.use(called)) == [1, 5, 9]


def test_vectorize_special_pick():
    l = weave.save(arrow.to_arrow(["a", None, "b", None, "c"]))
    dict_node = weave_internal.make_const_node(
        types.Dict(types.String(), types.String()),
        {
            "a": 1,
            "b": 2,
            "c": 3,
            "d": 4,
        },
    )
    fn = weave_internal.define_fn(
        {"row": l.type.object_type}, lambda row: dict_node[row]
    ).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"row": l})
    assert list(weave.use(called)) == [1, None, 2, None, 3]


def test_vectorize_function_with_const_first_arg():
    string = "hello"
    data = ["hello", "world", "hello", "world", "hello", "world"]
    awl_node = weave.save(arrow.to_arrow(data))
    string_node = weave_internal.make_const_node(types.String(), string)
    fn = weave_internal.define_fn(
        {"row": types.String()}, lambda row: string_node == row
    ).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"row": awl_node})
    assert weave.use(called).to_pylist_raw() == [True, False, True, False, True, False]


def test_isnone():
    a = [1, None, False, 0, "", "a"]
    awl = arrow.to_arrow(a)
    l = weave.save(awl)
    fn = weave_internal.define_fn({"x": awl.object_type}, lambda x: x.isNone()).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"x": l})
    assert weave.use(called).to_pylist_notags() == [
        False,
        True,
        False,
        False,
        False,
        False,
    ]


@pytest.mark.parametrize(
    "weave_func, expected",
    [
        (lambda x: Number.__eq__(5, x), [False, False, False, False, True]),
        (lambda x: Number.__ne__(5, x), [True, True, True, True, False]),
    ],
)
def test_right_equals_not_equals_elements_tagged(weave_func, expected):
    # make an arrow weave list with tagged elements
    data = [1, 2, 3, 4, 5]
    for i in range(len(data)):
        data[i] = tag_store.add_tags(box.box(data[i]), {"mytag": "test" + str(i)})
    awl = arrow.to_arrow(data)
    l = weave.save(awl)
    fn = weave_internal.define_fn({"x": awl.object_type}, weave_func).val
    vec_fn = arrow.vectorize(fn)
    called = weave_internal.call_fn(vec_fn, {"x": l})
    assert weave.use(called).to_pylist_notags() == expected


def test_map_each():
    d = [[{"a": 5, "b": 6}, {"a": 7, "b": 8}], [{"a": 9, "b": 10}, {"a": 11, "b": 12}]]
    awl = arrow.to_weave_arrow(d)
    called_map = awl.map(lambda x: x["a"])
    vec_fn = arrow.vectorize(called_map.from_op.inputs["map_fn"].val)
    # Should vectorize as AWL-mapEach
    assert vec_fn.from_op.name == "ArrowWeaveList-mapEach"
    result = weave.use(called_map)
    assert result.to_pylist_tagged() == [[5, 7], [9, 11]]


def test_map_each2():
    d = [[1, 2], [3, 4]]
    awl = arrow.to_weave_arrow(d)
    called_map = awl.map(lambda x: x + 2)
    vec_fn = arrow.vectorize(called_map.from_op.inputs["map_fn"].val)
    # Should vectorize as AWL-mapEach
    assert vec_fn.from_op.name == "ArrowWeaveList-mapEach"
    result = weave.use(called_map)
    assert result.to_pylist_tagged() == [[3, 4], [5, 6]]


# def test_map_each3():
#     d = [[1, 2], [3, 4]]
#     awl = arrow.to_weave_arrow(d)
#     # Not allowed to be called by type system... interesting
#     called_map = awl.map(lambda x: x + x)
#     vec_fn = arrow.vectorize(called_map.from_op.inputs["map_fn"].val)
#     # Should vectorize as AWL-mapEach
#     assert vec_fn.from_op.name == "ArrowWeaveList-mapEach"
#     result = weave.use(called_map)
#     assert result.to_pylist_tagged() == [[3, 4], [5, 6]]


# def test_map_each4():
#     d = [
#         [{"a": 5, "b": "a"}, {"a": 7, "b": "a"}],
#         [{"a": 9, "b": "a"}, {"a": 11, "b": "a"}],
#     ]
#     awl = arrow.to_weave_arrow(d)
#     called_map = awl.map(lambda x: x[x["b"]])
#     vec_fn = arrow.vectorize(called_map.from_op.inputs["map_fn"].val)
#     # Should vectorize as AWL-mapEach
#     assert vec_fn.from_op.name == "ArrowWeaveList-mapEach"
#     result = weave.use(called_map)
#     assert result.to_pylist_tagged() == [[5, 7], [9, 11]]
