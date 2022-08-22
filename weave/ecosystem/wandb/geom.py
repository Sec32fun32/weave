## Just used for testing for now. Not intended for use by users.
import math
import typing
import weave


@weave.type()
class Point2d:
    x: float
    y: float


@weave.op()
def points_render(
    points_node: weave.Node[list[Point2d]],
) -> weave.panels.Table:
    points = typing.cast(list[Point2d], points_node)  # type: ignore
    return weave.panels.Table(
        points,
        columns=[
            lambda point: point.x,
            lambda point: point.y,
        ],
    )


@weave.type()
class LineSegment:
    x0: float
    y0: float
    x1: float
    y1: float

    @weave.op()
    def length(self) -> float:
        x_len = self.x1 - self.x0
        y_len = self.y1 - self.y0
        inner = x_len**2 + y_len**2
        return inner
        return math.sqrt(inner)

    @weave.op()
    def midpoint(self) -> Point2d:
        x = self.x0 + (self.x1 - self.x0) / 2
        y = self.y0 + (self.y1 - self.y0) / 2
        return Point2d(x, y)
