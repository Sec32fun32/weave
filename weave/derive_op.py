import copy
import inspect
import typing

from . import weave_types as types
from . import op_args
from . import registry_mem
from . import op_def
from . import errors
from . import graph
from . import box
from . import weave_internal


class DeriveOpHandler:
    """
    Subclassing this class will add a new type of derived op to the Weave1 system
    """

    handler_id: typing.ClassVar[str]

    @staticmethod
    def derived_name(name: str) -> str:
        raise NotImplementedError()

    @staticmethod
    def should_derive_op(orig_op: op_def.OpDef) -> bool:
        raise NotImplementedError()

    @staticmethod
    def make_derived_op(orig_op: op_def.OpDef) -> op_def.OpDef:
        raise NotImplementedError()

    @staticmethod
    def handle_class_decorator_update(
        derived_op: op_def.OpDef,
        base_weave_type: type[types.Type],
        orig_op_new_name: str,
    ):
        raise NotImplementedError()


# These are a list of type names that should not be mapped
disallow_mapping_type_name_list = [
    "type",
    "list",
    "ndarray",
    "ArrowArray",
    "ArrowTable",
    "ArrowTableGroupBy",
    "ArrowWeaveList",
    "dataframe",
    "sqltable",
    "projectArtifactVersions",
    "runs",
    "artifacts",
    "projectArtifactTypes",
    "invalid",
    "unknown",
    "none",
    "any",
    "groupresult",
    "dataframeTable",
    "ArrowTableGroupResult",
    "ArrowWeaveList",
]

# This class implements a nullable mappable derived op handler. It will create a new op
# that is capable of handling a List<Optional<T>> input for a given op that takes a T
class MappedDeriveOpHandler(DeriveOpHandler):
    handler_id = "mapped"

    @staticmethod
    def derived_name(name: str) -> str:
        if "-" not in name:
            return f"mapped-{name}"
        else:
            return f"mapped_{name}"

    @staticmethod
    def should_derive_op(orig_op: op_def.OpDef) -> bool:
        """Returns True if the op should be mapped to a list of inputs."""
        named_args = orig_op.input_type.named_args()

        # The argument list must be named AND have at least 1 argument.
        if len(named_args) == 0:
            return False

        first_arg = named_args[0]

        # Enforce the disallow list
        if first_arg.type.class_type_name() in disallow_mapping_type_name_list:
            return False

        # Here, we check if the first_arg is unknown. If it is, then we cannot tell
        # if it is supposed to be mapped.
        if first_arg.type == types.UnknownType():
            return False

        # If the first argument can be assigned to a list<any>, then we should not map it -
        # it will create unresolvable ambiguity between the current op and the mapped.
        if types.List(types.Any()).assign_type(first_arg.type):
            return False

        # If the first argument can be assigned a list of the first argument, then we should not map -
        # this too will create unresolvable ambiguity.
        if first_arg.type.assign_type(types.List(first_arg.type)):
            return False

        return True

    @staticmethod
    def make_derived_op(orig_op: op_def.OpDef) -> op_def.OpDef:
        mapped_op_name = MappedDeriveOpHandler.derived_name(
            orig_op.name
        )  # TODO: doesn't handle fqn
        named_args = orig_op.input_type.named_args()

        if len(named_args) == 0 or not isinstance(
            orig_op.input_type, op_args.OpNamedArgs
        ):
            raise errors.WeaveInternalError(
                f"Cannot make mapped op for op {orig_op.name} with no first named argument."
            )
        first_arg = named_args[0]
        mapped_param_name = first_arg.name

        output_type: typing.Union[types.Type, typing.Callable]
        # TODO: In all of these, we use types.optional, but this should only be
        # used if the input_type is also optional. However we don't have a
        # weave-way to check that yet :(.
        if not callable(orig_op.output_type):

            def new_output_type(input_type):
                object_type = input_type[mapped_param_name].object_type
                if types.is_optional(object_type):
                    return types.List(types.optional(object_type))
                return types.List(object_type)

            output_type = new_output_type
        else:

            def make_output_type(input_types):
                replacement = input_types[mapped_param_name].object_type

                # Remove the nulls from the inner type
                if types.is_optional(replacement):
                    replacement = types.non_none(replacement)

                # This is a special circumstance (aka "God Mode") where we are
                # inferring when an external caller is trying to weaveify this
                # function. In this specific case, we need to manually construct the
                # output_type. The main reason for this is that `merge` is not yet
                # implemented as a core op that looks the same in python and weave.
                # Therefore the `inner_input_types[mapped_param_name] = replacement`
                # line below will not work. This is a temporary fix until we can
                # implement `merge` as a core op.
                currently_weavifying = isinstance(
                    input_types, graph.Node
                ) and types.TypedDict({}).assign_type(input_types.type)
                if currently_weavifying:
                    op_dict = registry_mem.memory_registry.get_op("dict")
                    op_dict.instance = None
                    inner_input_types = input_types.merge(
                        op_dict(**{mapped_param_name: replacement})
                    )
                    try:
                        inner_res = orig_op.output_type(inner_input_types)
                    except errors.WeaveExpectedConstError as e:
                        raise errors.WeaveMakeFunctionError(
                            "function body expected const node."
                        )
                    if not isinstance(inner_res, graph.Node):
                        raise errors.WeaveMakeFunctionError(
                            "output_type function must return a node."
                        )
                    from .ops_primitives.list_ import make_list

                    return types.List.make(
                        {
                            "object_type": types.UnionType.make(
                                {
                                    "members": make_list(
                                        n_0=types.NoneType.make(), n_1=inner_res
                                    )
                                }
                            )
                        }
                    )

                inner_input_types = copy.copy(input_types)
                inner_input_types[mapped_param_name] = replacement
                inner_output_type = orig_op.output_type(inner_input_types)

                object_type = input_types[mapped_param_name].object_type

                if types.is_optional(object_type):
                    return types.List(types.optional(inner_output_type))
                return types.List(inner_output_type)

            output_type = make_output_type

        def resolve(**inputs):
            new_inputs = copy.copy(inputs)
            list_ = new_inputs.pop(mapped_param_name)
            # TODO: use the vectorization described here:
            # https://paper.dropbox.com/doc/Weave-Python-Weave0-Op-compatibility-workstream-kJ3XSDdgR96XwKPapHwPD
            return [
                orig_op.resolve_fn(x, **new_inputs)
                if not (x is None or isinstance(x, box.BoxedNone))
                or types.is_optional(first_arg.type)
                else None
                for x in list_
            ]

        # Use the function signature of the original op to compute the signature
        # of the lazy call
        resolve.sig = inspect.signature(orig_op.raw_resolve_fn)  # type: ignore
        input_type = copy.copy(orig_op.input_type.arg_types)
        input_type[mapped_param_name] = types.List(types.optional(first_arg.type))
        new_op = op_def.OpDef(
            mapped_op_name,
            op_args.OpNamedArgs(input_type),
            output_type,
            resolve,
            _mapped_refine_output_type(orig_op),
        )

        def weave_fn_body(list_, *args):
            def map_item(item):
                full_named_args = {mapped_param_name: item}
                for i, na in enumerate(named_args[1:]):
                    full_named_args[na.name] = args[i]

                # use Any type for OutputNode
                return graph.OutputNode(types.Any(), orig_op.name, full_named_args)

            return list_.map(lambda item: map_item(item))

        new_op.weave_fn = weave_internal.define_fn(input_type, weave_fn_body)
        op_version = registry_mem.memory_registry.register_op(new_op)

        return op_version

    @staticmethod
    def handle_class_decorator_update(
        derived_op: op_def.OpDef,
        base_weave_type: type[types.Type],
        orig_op_new_name: str,
    ):
        named_args = derived_op.input_type.named_args()
        if len(named_args) == 0 or not isinstance(
            derived_op.input_type, op_args.OpNamedArgs
        ):
            raise errors.WeaveDefinitionError(
                f"Expected mapped op {derived_op.name} to have named first argument."
            )
        first_arg = named_args[0]
        # Check to see if the first argument is a list of UnknownType. This is how
        # we know that the type is expected to be the class type
        first_arg_is_cls = first_arg.type == types.List(
            types.optional(types.UnknownType())
        )
        if first_arg_is_cls:
            derived_op.input_type.arg_types[first_arg.name] = types.List(
                types.optional(base_weave_type())
            )
        registry_mem.memory_registry.rename_op(
            derived_op.name, MappedDeriveOpHandler.derived_name(orig_op_new_name)
        )


def _mapped_refine_output_type(orig_op):
    refine_output_type = None

    mapped_refine_op = (
        orig_op.refine_output_type.derived_ops["mapped"]
        if (
            orig_op.refine_output_type is not None
            and "mapped" in orig_op.refine_output_type.derived_ops
        )
        else None
    )

    if mapped_refine_op:

        def mapped_refine_output_type_refiner(*args, **kwargs):
            union_members = mapped_refine_op.raw_resolve_fn(*args, **kwargs)
            return types.List(
                types.union(
                    *[types.NoneType() if mem == None else mem for mem in union_members]
                )
            )

        unioned_mapped_type_refiner_op = op_def.OpDef(
            f"{mapped_refine_op.name}_unioned",
            mapped_refine_op.input_type,
            types.Type(),
            mapped_refine_output_type_refiner,
            None,
        )
        unioned_mapped_type_refiner_op_def = registry_mem.memory_registry.register_op(
            unioned_mapped_type_refiner_op
        )
        refine_output_type = unioned_mapped_type_refiner_op_def
    return refine_output_type


def handler_for_id(handler_id: str) -> type[DeriveOpHandler]:
    for handler in DeriveOpHandler.__subclasses__():
        if handler.handler_id == handler_id:
            return handler
    raise errors.WeaveInternalError(f"Unknown derive op handler {handler_id}")


def derive_ops(op: op_def.OpDef):
    for handler in DeriveOpHandler.__subclasses__():
        if handler.should_derive_op(op) and handler.handler_id not in op.derived_ops:
            op.derived_ops[handler.handler_id] = handler.make_derived_op(op)
