import pytest
from rich import print

from ..panels.panel_group import Group
from ..panels.panel_slider import Slider
from .. import weave_internal
import weave
from .. import storage
from .. import weave_internal


def test_panel_id():
    panel = Group(items={})
    assert panel.id == "Group"
    assert panel.to_json()["id"] == "Group"


@pytest.mark.skip()
# Doesn't work because we process variables "inside-out"
def test_simple_nested_1():
    panel = Group(
        vars={"a": weave_internal.make_const_node(weave.types.Int(), 5)},
        items={
            "item": Group(
                vars={"b": weave_internal.make_const_node(weave.types.Int(), 9)},
                items={"item_inner": lambda a, b: a + b},
            )
        },
    )
    panel._normalize()
    assert str(panel.items["item"].items["item_inner"]) == "add(a, b)"


def test_simple_nested_outer_lambda():
    panel = Group(
        vars={"a": weave_internal.make_const_node(weave.types.Int(), 5)},
        items={
            "item": lambda a: Group(
                vars={"b": weave_internal.make_const_node(weave.types.Int(), 9)},
                items={"item_inner": lambda b: a + b},
            )
        },
    )
    panel._normalize()
    assert str(panel.config.items["item"].config.items["item_inner"]) == "add(a, b)"


@pytest.mark.skip()
def test_nested():
    # Doesn't quite work, we get the wrong type for
    # a.items['a2'] (we get Panel, actually want Panel[number] I think?)
    panel = Group(
        items={
            "a": Group(items={"a1": 5, "a2": lambda a1: a1 + 5}),
            "b": Group(
                items={"b1": lambda a: a.items["a1"], "b2": lambda a: a.items["a2"]}
            ),
        }
    )
    panel.normalize()
    assert 1 == 2


@pytest.mark.skip()
def test_synced():
    panel = Group(
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
#     panel = Group(
#         items={"step": Slider2(), "table": panellambda my_slider: my_slider.value}
# )


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
    facet = weave.panels.Group(
        equalSize=True,
        items={
            "confusion": weave.panels.Facet(
                data,
                x=lambda row: row["guess"],
                y=lambda row: row["truth"],
                select=lambda row: weave.panels.Group(
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


def test_board():
    # Just make sure it runs for now.
    weave.panels.Board(
        {
            "nums": weave.ops.range(0, 3, 1),
        },
        [weave.panels.BoardPanel(id="panel0", panel=lambda nums: nums)],
    )
