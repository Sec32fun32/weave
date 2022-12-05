import pytest
from rich import print

from ..panels.panel_group2 import Group2
from ..panels.panel_slider2 import Slider2
from .. import weave_internal
import weave
from .. import storage
from .. import weave_internal


def test_panel_id():
    panel = Group2(items={})
    assert panel.id == "Group2"
    assert panel.to_json()["id"] == "Group2"


@pytest.mark.skip()
# Doesn't work because we process variables "inside-out"
def test_simple_nested_1():
    panel = Group2(
        vars={"a": weave_internal.make_const_node(weave.types.Int(), 5)},
        items={
            "item": Group2(
                vars={"b": weave_internal.make_const_node(weave.types.Int(), 9)},
                items={"item_inner": lambda a, b: a + b},
            )
        },
    )
    panel._normalize()
    assert str(panel.items["item"].items["item_inner"]) == "add(a, b)"


def test_simple_nested_outer_lambda():
    panel = Group2(
        vars={"a": weave_internal.make_const_node(weave.types.Int(), 5)},
        items={
            "item": lambda a: Group2(
                vars={"b": weave_internal.make_const_node(weave.types.Int(), 9)},
                items={"item_inner": lambda b: a + b},
            )
        },
    )
    panel._normalize()
    assert str(panel.config.items["item"].config.items["item_inner"]) == "add(a, b)"


def test_controlled_state_out():
    panel = Group2(
        items={"my_slider": Slider2(), "val": lambda my_slider: my_slider.config.value}
    )
    # panel.items['val'] will have been converted to a node, stringifying it
    # produces an expression string.
    assert str(panel.config.items["val"]) == "my_slider.config.value"


@pytest.mark.skip()
def test_nested():
    # Doesn't quite work, we get the wrong type for
    # a.items['a2'] (we get Panel, actually want Panel[number] I think?)
    panel = Group2(
        items={
            "a": Group2(items={"a1": 5, "a2": lambda a1: a1 + 5}),
            "b": Group2(
                items={"b1": lambda a: a.items["a1"], "b2": lambda a: a.items["a2"]}
            ),
        }
    )
    panel.normalize()
    assert 1 == 2


@pytest.mark.skip()
def test_synced():
    panel = Group2(
        vars={"num": 0},
        items={
            "a": lambda num: Slider2(num),
            "b": lambda num: Slider2(num),
            "c": lambda num: num,
        },
    )
    print(panel.to_json())
    assert 1 == 2


# def test_select_row():
#     panel = Group2(
#         items={"step": Slider2(), "table": panellambda my_slider: my_slider.value}
# )


def test_save_panel():
    metrics = weave.save(["a", "b"])
    data = weave.save([{"a": [0, 1], "b": [2, 3]}, {"a": [4, 5], "b": [6, 7]}])

    panel = weave.panels.Each(
        metrics,
        render=lambda metric_name: weave.panels.Plot(
            data,
            x=lambda row: row[metric_name][0],
            y=lambda row: row[metric_name][1],
        ),
    )
    # Just make sure it doesn't crash for now
    storage.save(panel)


def test_object_picker_choice_type():
    ints = weave.save([1, 2, 3], name="my-ints")
    panel = weave.panels.ObjectPicker(ints)
    panel_node = weave_internal.make_var_node(weave.type_of(panel), "panel")
    choice = panel_node.config.choice
    assert choice.type == weave.types.Function({}, weave.types.Int())


def test_facet_selected():
    data = weave.save(
        [{"guess": "dog", "truth": "cat"}, {"guess": "dog", "truth": "dog"}]
    )
    facet = weave.panels.Group2(
        equalSize=True,
        items={
            "confusion": weave.panels.Facet(
                data,
                x=lambda row: row["guess"],
                y=lambda row: row["truth"],
                select=lambda row: weave.panels.Group2(
                    layered=True,
                    items={
                        "color": weave.panels.Color(row.count() / 50),
                        "count": row.count(),
                    },
                ),
            ),
            "selected": lambda confusion: confusion.selected(),
        },
    )
    assert facet.config.items["selected"].type == data.type
