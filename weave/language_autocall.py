# Language feature: Automatic function calling
#
# A Weave Node is a Function. If there are no variables in the Node's DAG,
# the node can be executed.
#
# If you have a Node[Function[..., int]], you may pass it in positions that
# expect int. We automatically insert an .execute() op when this type of
# call is detected.
#
# TODO: resolve ambiguities:
#   - should it work recursively? (Node[Function[..., Function[..., int]]])
#   - does this cause invalid type/name overlap and collisions?

# There is also a compile pass for this in compile.py

import typing

from . import weave_types as types
from . import op_args


def is_function_like(type_: types.Type) -> bool:
    return types.Function({}, types.Any()).assign_type(type_)


def update_input_types(
    op_input_type: typing.Optional[op_args.OpArgs],
    actual_input_types: dict[str, types.Type],
) -> dict[str, types.Type]:
    if not isinstance(op_input_type, op_args.OpNamedArgs):
        return actual_input_types
    expected_input_types = op_input_type.arg_types
    result: dict[str, types.Type] = {}
    try:
        for k, t in actual_input_types.items():
            expected_input_type = expected_input_types[k]
            if is_function_like(t) and not is_function_like(expected_input_type):
                t = typing.cast(types.Function, t)
                result[k] = t.output_type
            else:
                result[k] = t
    except KeyError:
        return actual_input_types
    return result


def node_methods_class(
    type_: types.Type,
) -> tuple[typing.Optional[type], typing.Optional[str]]:
    if not isinstance(type_, types.Function):
        return None, None
    function_output_type = type_.output_type
    if not hasattr(function_output_type, "NodeMethodsClass"):
        return None, None
    return (
        function_output_type.NodeMethodsClass,
        function_output_type.__class__.__name__,
    )
