import pytest
from PIL import Image


from .. import context_state as _context

from weave.ecosystem.wandb import geom

from .. import api as weave
from ..ops_primitives import ops_arrow
from .. import errors


def test_mapped_method_on_custom_type():
    segment = geom.LineSegment(0.0, 0.1, 0.9, 1.1)

    len = weave.use(segment.length())
    assert len == 1.81

    mid = weave.use(segment.midpoint())
    assert mid.x == 0.45
    assert mid.y == 0.6

    segments = ops_arrow.to_arrow(
        [
            geom.LineSegment(0.0, 0.1, 0.9, 1.1),
            geom.LineSegment(0.0, 0.2, 0.4, 1.1),
        ]
    )
    lens = weave.use(segments.map(lambda seg: seg.length()))
    assert weave.use(lens[0]) == 1.81
    assert weave.use(lens[1]) == pytest.approx(0.97)

    # mid = weave.use(segments.midpoint())
    # mid = weave.use(segments.map(lambda seg: seg.midpoint()))
    # assert mid[0].x == 0.45
    # assert mid[0].y == 0.6
    # assert mid[1].x == 0.2
    # assert mid[1].y == pytest.approx(0.65)


def test_mapped_method_returning_custom_type():
    segments = ops_arrow.to_arrow(
        [
            geom.LineSegment(0.0, 0.1, 0.9, 1.1),
            geom.LineSegment(0.0, 0.2, 0.4, 1.1),
        ]
    )

    mid = weave.use(segments.map(lambda seg: seg.midpoint()))

    assert weave.use(mid[0].x) == 0.45
    assert weave.use(mid[0].y) == 0.6
    assert weave.use(mid[1].x) == 0.2
    assert weave.use(mid[1].y) == pytest.approx(0.65)


def test_mapped_on_fully_custom_type():
    data = [
        {"a": 5, "im": Image.linear_gradient("L").rotate(0)},
        {"a": 6, "im": Image.linear_gradient("L").rotate(4)},
    ]
    arrow_arr = ops_arrow.to_arrow(data)

    assert weave.use(arrow_arr.map(lambda row: row["im"].width_())).to_pylist() == [
        256,
        256,
    ]


def test_mapped_pick():
    data = [
        {"a": 5, "b": 9},
        {"a": 6, "b": 10},
    ]
    arrow_arr = ops_arrow.to_arrow(data)

    assert weave.use(arrow_arr.pick("b")).to_pylist() == [9, 10]


def test_constructor():
    expected = geom.Point2d(0.5, 0.6)
    point2d_node = geom.Point2d.constructor({"x": 0.5, "y": 0.6})
    assert weave.use(point2d_node) == expected

    with pytest.raises(KeyError):
        weave.use(geom.Point2d.constructor({"x": 0.5}))
