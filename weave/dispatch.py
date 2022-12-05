"""Functions for determining which op is being called."""
from dataclasses import dataclass
import functools
import logging
import typing

from . import language_nullability
from .language_features.tagging.make_tag_getter_op import is_tag_getter

from . import errors
from . import weave_types as types
from . import op_def
from . import op_args
from . import registry_mem
from . import graph
from . import errors
from . import op_aliases
from . import pyfunc_type_util


class OpAmbiguityError(Exception):
    pass


# I originally wrote this thinking that we could always choose the more specific
# op, defined as the one that's input types are strict subtypes of the other.
# But consider mapped_add(List[number], number) and
# arrow_mapped_add(ArrowList[number], union[number, ArrowList[number]])
# (this is how we've actually defined those currently)
# ArrowList[number] is a subtype of number, but number is a subtype of
# union[number, ArrowList[number]].
# arrow_mapped_add is more specific in the first arg, but less specific in the
# second!
# So for now, we only consider the first argument.
# TODO: Solve. I see three potential solutions
#   1. Make mapped ops automatically handle arrays in their second argument
#   2. Split arrow ops into two ops, for array/scalar in second arg
#   3. Figure out some clever way to resolve the above ambiguity here
def op_args_is_subtype(lhs: op_args.OpArgs, rhs: op_args.OpArgs) -> bool:
    """Returns true if rhs is subtype of lhs"""
    if isinstance(lhs, op_args.OpNamedArgs) and isinstance(rhs, op_args.OpNamedArgs):
        if len(lhs.arg_types) != len(rhs.arg_types):
            return False
        for self_type, other_type in list(
            zip(lhs.initial_arg_types.values(), rhs.initial_arg_types.values())
        )[:1]:
            if not self_type.assign_type(other_type):
                return False
        return True
    elif isinstance(lhs, op_args.OpNamedArgs) and isinstance(rhs, op_args.OpVarArgs):
        return all(t.assign_type(rhs.arg_type) for t in lhs.initial_arg_types.values())
    elif isinstance(lhs, op_args.OpVarArgs) and isinstance(rhs, op_args.OpNamedArgs):
        return all(lhs.arg_type.assign_type(t) for t in rhs.initial_arg_types.values())
    elif isinstance(lhs, op_args.OpVarArgs) and isinstance(rhs, op_args.OpVarArgs):
        return lhs.arg_type.assign_type(rhs.arg_type)
    else:
        raise errors.WeaveInternalError("unknown op_args types: %s, %s" % (lhs, rhs))


def resolve_op_ambiguity(candidates: list[op_def.OpDef]) -> op_def.OpDef:
    # Currently we deprioritize all tag getter ops below standard ops
    tag_getter_candidates = []
    non_tag_getter_candidates = []
    for candidate in candidates:
        if is_tag_getter(candidate):
            tag_getter_candidates.append(candidate)
        else:
            non_tag_getter_candidates.append(candidate)

    def cmp(a: op_def.OpDef, b: op_def.OpDef) -> int:
        b_is_subtype = op_args_is_subtype(a.input_type, b.input_type)
        a_is_subtype = op_args_is_subtype(b.input_type, a.input_type)
        if a_is_subtype and b_is_subtype:
            raise OpAmbiguityError(
                "Ambiguous ops %s, %s. Ops' input types are equivalent"
                % (a.name, b.name)
            )
        if a_is_subtype:
            return -1
        if b_is_subtype:
            return 1
        raise OpAmbiguityError(
            "Ambiguous ops %s, %s. Ops' input types first arguments must be subset in one direction or the other."
            % (a.name, b.name)
        )

    if len(non_tag_getter_candidates) > 0:
        if len(tag_getter_candidates) > 0:
            logging.warning(
                f"Op dispatch candidates contained {len(non_tag_getter_candidates)} non tag-getters and {len(tag_getter_candidates)} tag getters. Ignoring tag getters to avoid ambigious dispatch."
            )
        ordered = sorted(non_tag_getter_candidates, key=functools.cmp_to_key(cmp))
    else:
        ordered = sorted(tag_getter_candidates, key=functools.cmp_to_key(cmp))

    return ordered[0]


def get_ops_by_name(fq_op_name: str) -> list[op_def.OpDef]:
    """Returns a single op that matches the given name and raw inputs (inputs can be python objects or nodes)"""
    shared_name_ops: list[op_def.OpDef]

    if fq_op_name.startswith("local-artifact://"):
        # If the incoming op is a locally-defined op, then we are just going to look at the derived op space.
        # We don't need to search the whole registry since by definition it is user-defined
        op = registry_mem.memory_registry.get_op(fq_op_name)
        derived_ops = list(op.derived_ops.values())
        shared_name_ops = [op] + derived_ops
    # Else, we lookup all the ops with the same common name
    else:
        shared_name_ops = registry_mem.memory_registry.find_ops_by_common_name(
            op_def.common_name(fq_op_name)
        )
    return shared_name_ops


def choose_op_for_args(
    op_choices: list[op_def.OpDef],
    args: list[types.Type],
    kwargs: dict[str, types.Type],
) -> typing.Optional[op_def.OpDef]:
    candidates: list[op_def.OpDef] = []
    for op in op_choices:
        param_dict = op.input_type.create_param_dict(args, kwargs)
        param_dict = language_nullability.adjust_assignable_param_dict_for_dispatch(
            op, param_dict
        )
        if op.input_type.params_are_valid(param_dict):
            candidates.append(op)
    if not candidates:
        return None
    return resolve_op_ambiguity(candidates)


def dispatch_by_name_and_type(
    common_name: str, args: typing.Any, kwargs: typing.Any
) -> typing.Any:
    ops = get_ops_by_name(common_name)
    if len(ops) == 0:
        err = errors.WeaveDispatchError(
            f'Cannot dispatch op "{common_name}"; no matching op found'
        )
        try:
            import sentry_sdk
        except ImportError:
            raise err
        else:
            with sentry_sdk.push_scope() as scope:
                scope.fingerprint = [common_name]
                raise err

    return dispatch_ops_by_type(ops, args, kwargs)


def dispatch_ops_by_type(
    ops: list[op_def.OpDef], args: list[typing.Any], kwargs: dict[str, typing.Any]
) -> "RuntimeOutputNode":
    arg_types = [type_of_input_param(arg) for arg in args]
    kwarg_types = {k: type_of_input_param(v) for k, v in kwargs.items()}
    op = choose_op_for_args(ops, arg_types, kwarg_types)
    if op is None:
        if len(ops) == 0:
            raise errors.WeaveDispatchError(
                f"dispatch_ops_by_type called with no ops. args: {args}, kwargs: {kwargs}"
            )
        raise errors.WeaveDispatchError(
            "No implementation of (%s) found for arg types: %s %s"
            % (op_aliases.get_op_aliases(ops[0].common_name), arg_types, kwarg_types)
        )
    params = op.input_type.create_param_dict(args, kwargs)
    return op(**params)


def get_op_for_input_types(fq_op_name, arg_types, kwarg_types):  # type: ignore
    ops = get_ops_by_name(fq_op_name)
    return choose_op_for_args(ops, arg_types, kwarg_types)


def type_of_input_param(v: typing.Any) -> types.Type:
    if isinstance(v, graph.Node):
        # Check if its a Node first, sometimes we mixin a callables with Node!
        if isinstance(v, graph.ConstNode) and not isinstance(v.type, types.Const):
            return types.Const(v.type, v.val)
        return v.type
    elif callable(v):
        input_type = pyfunc_type_util.determine_input_type(v, None, True)
        output_type = pyfunc_type_util.determine_output_type(v, None, True)
        if not isinstance(input_type, op_args.OpNamedArgs):
            raise errors.WeaveInternalError("Function conversion requires named args")
        if callable(output_type):
            raise errors.WeaveInternalError(
                "Function conversion does not support callable output types"
            )
        return types.Function(
            input_type.arg_types,
            output_type,
        )
    else:
        return types.Const(types.TypeRegistry.type_of(v), v)


@dataclass
class BoundPotentialOpDefs:
    self_node: graph.Node
    potential_ops: list[op_def.OpDef]

    def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> "RuntimeOutputNode":
        return dispatch_ops_by_type(
            self.potential_ops, [self.self_node] + list(args), kwargs
        )


def dispatch_dunder(
    name: str,
) -> typing.Callable[
    [graph.Node, list[typing.Any], dict[str, typing.Any]], "RuntimeOutputNode"
]:
    def dispatch_dunder_inner(
        self_node: graph.Node, *args: typing.Any, **kwargs: typing.Any
    ) -> "RuntimeOutputNode":
        return dispatch_by_name_and_type(name, [self_node] + list(args), kwargs)

    return dispatch_dunder_inner


class DispatchMixin:
    # Little hack, storage._get_ref expects to be able to check whether
    # any object hasattr('_ref') including nodes. Set it here so that
    # our __getattr__ op method doesn't handle that check.
    _ref = None
    # ipython tries to figure out if we have implemented a __getattr__
    # by checking for this attribute. But the weave.op() decorator makes
    # __getattr__ behave oddly, its now a lazy getattr that will always return
    # something. So add the attribute here to tell ipython that yes we do
    # have a __getattr__. This fixes Node._ipython_display()_ not getting fired.
    _ipython_canary_method_should_not_exist_ = None

    # Needed for storage.to_python hacks. Remove after those hacks are fixed.
    # TODO: fix
    to_pylist_notags = None
    as_py = None

    def __dir__(self) -> list[str]:
        ops = registry_mem.memory_registry.find_chainable_ops(self.type)
        return [o.common_name for o in ops]

    def __getattr__(self, attr: str) -> typing.Any:
        node_self = typing.cast(graph.Node, self)
        if attr.startswith("__") and attr.endswith("__"):
            return getattr(super(), attr)

        # First, we check if the attribute matches a known op name...
        ops_with_name = registry_mem.memory_registry.find_ops_by_common_name(attr)
        ops_with_name_and_arg = []
        for op in ops_with_name:
            named_args = op.input_type.named_args()
            if len(
                named_args
            ) > 0 and language_nullability.adjust_input_type_for_mixin_dispatch(
                named_args[0].type
            ).assign_type(
                node_self.type
            ):
                ops_with_name_and_arg.append(op)
        if len(ops_with_name_and_arg) > 0:
            if len(ops_with_name_and_arg) == 1:
                # If there's only one candidate, we can just return it.
                return op_def.BoundOpDef(node_self, ops_with_name_and_arg[0])
            else:
                # Otherwise, we need to wait til we know the rest of the args
                # before we can decide which op to use.
                return BoundPotentialOpDefs(node_self, ops_with_name_and_arg)
        if node_self.type.__class__ == types.Type:
            # We are doing attribute access on a Weave Type. Let them all through
            # for now.
            obj_getattr = registry_mem.memory_registry.get_op("Object-__getattr__")
            return obj_getattr(node_self, attr)
        self_type = node_self.type
        if not isinstance(self_type, types.ObjectType):
            raise errors.WeaveDispatchError(
                'No ops called "%s" are chainable for type "%s"'
                % (attr, node_self.type)
            )
        # Definitely an ObjectType
        if attr in self_type.property_types():
            obj_getattr = registry_mem.memory_registry.get_op("Object-__getattr__")
            return obj_getattr(node_self, attr)
        raise errors.WeaveDispatchError(
            'No ops or attributes called "%s" available on type "%s"'
            % (attr, node_self.type)
        )

    __call__ = dispatch_dunder("__call__")
    __getitem__ = dispatch_dunder("__getitem__")
    __len__ = dispatch_dunder("__len__")
    __add__ = dispatch_dunder("__add__")
    __sub__ = dispatch_dunder("__sub__")
    __mul__ = dispatch_dunder("__mul__")
    __truediv__ = dispatch_dunder("__truediv__")
    __floordiv__ = dispatch_dunder("__floordiv__")
    __pow__ = dispatch_dunder("__pow__")
    __mod__ = dispatch_dunder("__mod__")
    __round__ = dispatch_dunder("__round__")
    __ge__ = dispatch_dunder("__ge__")
    __gt__ = dispatch_dunder("__gt__")
    __le__ = dispatch_dunder("__le__")
    __lt__ = dispatch_dunder("__lt__")
    __eq__ = dispatch_dunder("__eq__")  # type: ignore
    __ne__ = dispatch_dunder("__ne__")  # type: ignore
    __neg__ = dispatch_dunder("__neg__")
    __contains__ = dispatch_dunder("__contains__")


class RuntimeOutputNode(graph.OutputNode, DispatchMixin):
    pass


class RuntimeVarNode(graph.VarNode, DispatchMixin):
    pass


class RuntimeConstNode(graph.ConstNode, DispatchMixin):
    pass
