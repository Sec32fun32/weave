from ..ops import make_list, dict_, unnest
from .. import forward_graph
from ..execute import execute_forward
from .. import compile


def test_cache_control():
    target = {"t": 1, "b": [1, 2, 3, 4]}
    node_that_should_not_cache = make_list(**{"0": target})
    second_node_that_should_not_cache = unnest(node_that_should_not_cache)

    nodes = compile.compile([second_node_that_should_not_cache])
    fg = forward_graph.ForwardGraph(nodes)
    stats = execute_forward(fg, no_cache=False)
    summary = stats.summary()
    assert sum([v["cache_used"] for v in summary.values()]) == 0

    node_that_should_cache = dict_(a=second_node_that_should_not_cache)
    nodes = compile.compile([node_that_should_cache])
    fg = forward_graph.ForwardGraph(nodes)
    stats = execute_forward(fg, no_cache=False)
    summary = stats.summary()
    assert sum([v["cache_used"] for v in summary.values()]) == 1
