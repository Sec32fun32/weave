import typing

import logging
from .lazy import _make_output_node
from . import op_args
from . import weave_types as types
from . import graph
from . import graph_editable
from . import registry_mem
from . import errors
from . import dispatch
from . import graph_debug
from . import engine_trace

# These call_* functions must match the actual op implementations.
# But we don't want to import the op definitions themselves here, since
# those depend on the decorators, which aren't defined in the engine.


def call_run_await_final_output(run_node: graph.Node) -> graph.OutputNode:
    run_node_type = typing.cast(types.RunType, run_node.type)
    return graph.OutputNode(run_node_type.output, "run-await", {"self": run_node})


# We don't want to import the op definitions themselves here, since
# those depend on the decorators, which aren't defined in the engine.
def _call_execute(function_node: graph.Node) -> graph.OutputNode:
    function_node_type = typing.cast(types.Function, function_node.type)
    return graph.OutputNode(
        function_node_type.output_type, "execute", {"node": function_node}
    )


# Helper function to get the type of a node safely respecting constant types.
# TODO: This should be moved into the core node logic
def node_type(node: graph.Node) -> types.Type:
    if isinstance(node, graph.ConstNode) and not isinstance(node.type, types.Const):
        return types.Const(node.type, node.val)
    return node.type


def apply_type_based_dispatch(
    edit_g: graph_editable.EditGraph,
) -> None:
    """
    This method is responsible for attempting to re-dispatch ops based on their
    types. This is useful to solve for mappability, JS/Py differences, or any
    case where the provided op may not be the true op needed given the provided
    types. Importantly, it does rely on paramter ordering.
    """
    # Topological order guarantees that all parents have been processed before the children
    for orig_node in edit_g.topologically_ordered_nodes:
        node = edit_g.get_node(orig_node)
        node_inputs = {k: edit_g.get_node(v) for k, v in node.from_op.inputs.items()}
        input_types = {k: node_type(v) for k, v in node_inputs.items()}
        found_op = dispatch.get_op_for_input_types(node.from_op.name, [], input_types)
        if found_op is None:
            # There is a parallel spot in lazy.py which has a similar comment
            # This indicates that we believe there is no valid op to accept the incoming types.
            # Before productionizing Weave, we should throw here - for now since assignability is
            # still a bit off, we are a bit more relaxed.
            logging.warning(
                f"Compile Dispatch - Unable to find a valid op for {node.from_op.name}."
            )
            # raise errors.WeaveInternalError(
            #     f"Could not find op for input types {input_types} for node {node.from_op.name}"
            # )
            continue

        params = found_op.bind_params(
            [], found_op.input_type.create_param_dict([], node_inputs)
        )
        named_param_types = {k: node_type(v) for k, v in params.items()}
        new_node = _make_output_node(
            found_op.uri,
            params,
            found_op.input_type,
            found_op.return_type_of_arg_types(named_param_types),
            found_op.refine_output_type,
        )
        should_replace = new_node.from_op.name != node.from_op.name or any(
            v in edit_g.replacements for v in orig_node.from_op.inputs.values()
        )
        if not node.type.assign_type(new_node.type):
            logging.warn(
                "Compile phase [dispatch] Changed output type for node %s from %s to %s. This indicates an incompability between WeaveJS and Weave Python",
                node,
                node.type,
                new_node.type,
            )
            should_replace = True

        if should_replace:
            edit_g.replace(orig_node, new_node)


def await_run_outputs_edit_graph(
    edit_g: graph_editable.EditGraph,
) -> None:
    """Automatically insert Run.await_final_output steps as needed."""

    for orig_edge, edge in edit_g.edges_with_replacements:
        actual_input_type = edge.output_of.type
        op_def = registry_mem.memory_registry.get_op(edge.input_to.from_op.name)
        if op_def.name == "tag-indexCheckpoint" or op_def.name == "Object-__getattr__":
            # These are supposed to be a passthrough op, we don't want to convert
            # it. TODO: Find a more general way, maybe by type inspection?
            continue
        if not isinstance(op_def.input_type, op_args.OpNamedArgs):
            # Not correct... we'd want to walk these too!
            # TODO: fix
            continue
        # If the Node type is RunType, but the Op argument it is passed to
        # is not a RunType, insert an await_final_output operation to convert
        # the Node from a run to the run's output.
        try:
            expected_input_type = op_def.input_type.arg_types[edge.input_name]
        except KeyError:
            raise errors.WeaveInternalError(
                "OpDef (%s) missing input_name: %s" % (op_def.name, edge.input_name)
            )
        if isinstance(actual_input_type, types.RunType) and not isinstance(
            expected_input_type, types.RunType
        ):
            if not expected_input_type.assign_type(actual_input_type.output):
                raise Exception(
                    "invalid type chaining for run. input_type: %s, op_input_type: %s"
                    % (actual_input_type, expected_input_type)
                )
            new_inputs = dict(edge.input_to.from_op.inputs)
            new_inputs[edge.input_name] = call_run_await_final_output(edge.output_of)
            edit_g.replace(
                edge.input_to,
                graph.OutputNode(
                    edge.input_to.type, edge.input_to.from_op.name, new_inputs
                ),
            )


def execute_edit_graph(edit_g: graph_editable.EditGraph) -> None:
    """In cases where an input is a Node, execute the Node"""

    for orig_edge, edge in edit_g.edges_with_replacements:
        actual_input_type = edge.output_of.type
        op_def = registry_mem.memory_registry.get_op(edge.input_to.from_op.name)
        if not isinstance(op_def.input_type, op_args.OpNamedArgs):
            # Not correct... we'd want to walk these too!
            # TODO: fix
            continue
        # If the Node type is RunType, but the Op argument it is passed to
        # is not a RunType, insert an await_final_output operation to convert
        # the Node from a run to the run's output.
        try:
            expected_input_type = op_def.input_type.arg_types[edge.input_name]
        except KeyError:
            raise errors.WeaveInternalError(
                "OpDef (%s) missing input_name: %s" % (op_def.name, edge.input_name)
            )
        if isinstance(actual_input_type, types.Function) and not isinstance(
            expected_input_type, types.Function
        ):
            if not expected_input_type.assign_type(actual_input_type.output_type):
                raise Exception(
                    "invalid type chaining for Node. input_type: %s, op_input_type: %s"
                    % (actual_input_type, expected_input_type)
                )
            new_inputs = dict(edge.input_to.from_op.inputs)

            new_inputs[edge.input_name] = _call_execute(edge.output_of)
            edit_g.replace(
                orig_edge.input_to,
                graph.OutputNode(
                    edge.input_to.type, edge.input_to.from_op.name, new_inputs
                ),
            )


def _compile_phase(
    g: graph_editable.EditGraph,
    phase_name: str,
    phase_fn: typing.Callable[[graph_editable.EditGraph], None],
):
    phase_fn(g)
    edit_log = g.checkpoint()
    logging.info("Compile phase [%s] Made %s edits", phase_name, len(edit_log))
    if edit_log:
        loggable_nodes = graph_debug.combine_common_nodes(g.to_standard_graph())
        logging.info(
            "Compile phase [%s] Result nodes:\n%s",
            phase_name,
            "\n".join(graph_debug.node_expr_str_full(n) for n in loggable_nodes),
        )


def compile(nodes: typing.List[graph.Node]) -> typing.List[graph.Node]:
    """
    This method is used to "compile" a list of nodes. Here we can add any
    optimizations or graph rewrites
    """
    tracer = engine_trace.tracer()
    with tracer.trace("compile"):
        logging.info("Starting compilation of graph with %s leaf nodes" % len(nodes))

        # Convert the nodes to an editable graph data structure
        g = graph_editable.EditGraph(nodes)

        # Each of the following lines is a transformation pass of the graph:
        # 1: Adjust any Op calls based on type-based dispatching
        _compile_phase(g, "dispatch", apply_type_based_dispatch)

        # 2: Add Await nodes for Runs
        _compile_phase(g, "await", await_run_outputs_edit_graph)

        # 3: Execute function nodes
        _compile_phase(g, "execute", execute_edit_graph)

        # Reconstruct a node list that matches the original order from the transformed graph
        n = g.to_standard_graph()

        logging.info("Compilation complete")

    return n
