import collections
import copy
import typing
import inspect

from weave.weavejs_fixes import fixup_node

from . import errors
from . import op_args
from . import context_state
from . import weave_types as types
from . import uris
from . import graph
from . import weave_internal
from . import pyfunc_type_util
from . import engine_trace
from .language_features.tagging import (
    process_opdef_resolve_fn,
    process_opdef_output_type,
)
from . import language_autocall


def common_name(name: str) -> str:
    return name.split("-")[-1]


class OpDef:
    """An Op Definition.

    Must be immediately passed to Register.register_op() after construction.
    """

    input_type: op_args.OpArgs
    raw_output_type: typing.Union[
        types.Type,
        typing.Callable[[typing.Dict[str, types.Type]], types.Type],
    ]
    refine_output_type: typing.Optional["OpDef"]
    setter = str
    version: typing.Optional[str]
    location: typing.Optional[uris.WeaveURI]
    is_builtin: bool = False
    weave_fn: typing.Optional[graph.Node]
    _decl_locals: typing.Dict[str, typing.Any]
    instance: typing.Union[None, graph.Node]
    pure: bool
    raw_resolve_fn: typing.Callable
    _output_type: typing.Optional[
        typing.Union[
            types.Type,
            typing.Callable[[typing.Dict[str, types.Type]], types.Type],
        ]
    ]

    # This is required to be able to determine which ops were derived from this
    # op. Particularly in cases where we need to rename or lookup when
    # versioned, we cannot rely just on naming structure alone.
    derived_ops: typing.Dict[str, "OpDef"]

    def __init__(
        self,
        name: str,
        input_type: op_args.OpArgs,
        output_type: typing.Union[
            types.Type,
            typing.Callable[[typing.Dict[str, types.Type]], types.Type],
        ],
        resolve_fn: typing.Callable,
        refine_output_type: typing.Optional["OpDef"] = None,
        setter=None,
        render_info=None,
        pure=True,
        is_builtin: typing.Optional[bool] = None,
        weave_fn: typing.Optional[graph.Node] = None,
        _decl_locals=None,  # These are python locals() from the enclosing scope.
    ):
        self.name = name
        self.input_type = input_type
        self.raw_output_type = output_type
        self.refine_output_type = refine_output_type
        self.raw_resolve_fn = resolve_fn  # type: ignore
        self.setter = setter
        self.render_info = render_info
        self.pure = pure
        self.is_builtin = (
            is_builtin
            if is_builtin is not None
            else context_state.get_loading_built_ins()
        )
        self._decl_locals = _decl_locals
        self.version = None
        self.location = None
        self.instance = None
        self.derived_ops = {}
        self.weave_fn = weave_fn
        self._output_type = None

    def __get__(self, instance, owner):
        return BoundOpDef(instance, self)

    def __call__(_self, *args, **kwargs):
        # Uses _self instead of self, because self is a typical op argument!
        if context_state.eager_mode():
            return _self.eager_call(*args, **kwargs)
        else:
            return _self.lazy_call(*args, **kwargs)

    def lazy_call(_self, *args, **kwargs):
        bound_params = _self.bind_params(args, kwargs)
        # Don't try to refine if there are variable nodes, we are building a
        # function in that case!
        final_output_type: types.Type
        if _self.refine_output_type and not any(
            graph.expr_vars(arg_node) for arg_node in bound_params.values()
        ):
            called_refine_output_type = _self.refine_output_type(**bound_params)
            tracer = engine_trace.tracer()  # type: ignore
            with tracer.trace("refine.%s" % _self.uri):
                # api's use auto-creates client. TODO: Fix inline import
                from . import api

                final_output_type = api.use(called_refine_output_type)  # type: ignore
            from . import registry_mem

            final_output_type = (
                process_opdef_output_type.process_opdef_refined_output_type(
                    final_output_type, bound_params, _self
                )
            )
        elif callable(_self.output_type):
            new_input_type: dict[str, types.Type] = {}
            for k, n in bound_params.items():
                if isinstance(n, graph.ConstNode) and not isinstance(
                    n.type, types.Const
                ):
                    new_input_type[k] = types.Const(n.type, n.val)
                else:
                    new_input_type[k] = n.type

            new_input_type = language_autocall.update_input_types(
                _self.input_type, new_input_type
            )

            final_output_type = _self.output_type(new_input_type)
        else:
            final_output_type = _self.output_type
        from . import dispatch

        return dispatch.RuntimeOutputNode(final_output_type, _self.uri, bound_params)

    def eager_call(_self, *args, **kwargs):
        if _self.is_async:
            output_node = _self.lazy_call(*args, **kwargs)
            return weave_internal.use(output_node)
        else:
            return _self.resolve_fn(*args, **kwargs)

    def resolve_fn(__self, *args, **kwargs):
        res = __self.raw_resolve_fn(*args, **kwargs)
        return process_opdef_resolve_fn.process_opdef_resolve_fn(
            __self, res, args, kwargs
        )

    @property
    def output_type(
        self,
    ) -> typing.Union[
        types.Type,
        typing.Callable[[typing.Dict[str, types.Type]], types.Type],
    ]:
        if self._output_type is None:
            if self.name in [
                "op_get_tag_type",
                "op_make_type_tagged",
                "op_make_type_key_tag",
            ]:
                self._output_type = self.raw_output_type
            else:
                self._output_type = process_opdef_output_type.process_opdef_output_type(
                    self.raw_output_type, self
                )
        return self._output_type

    @property
    def concrete_output_type(self) -> types.Type:
        if callable(self.output_type):
            if isinstance(self.input_type, op_args.OpVarArgs):
                return self.output_type({})
            elif isinstance(self.input_type, op_args.OpNamedArgs):
                try:
                    return self.output_type(self.input_type.to_dict())
                except AttributeError:
                    return types.UnknownType()
            else:
                raise NotImplementedError("Unknown input type for op %s" % self.name)
        return self.output_type

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        if name.count("-") > 1:
            raise errors.WeaveDefinitionError(
                "Op names must have at most one hyphen. Got: %s" % name
            )
        self._name = name

    @property
    def common_name(self):
        return common_name(self.name)

    @property
    def uri(self):
        return self.location.uri if self.location is not None else self.name

    @property
    def simple_name(self):
        return uris.WeaveURI.parse(self.name).full_name

    @property
    def is_mutation(self):
        return getattr(self.raw_resolve_fn, "is_mutation", False)

    @property
    def is_async(self):
        return (
            not callable(self.raw_output_type)
            and self.concrete_output_type.name == "Run"
        )

    def to_dict(self):
        output_type = self.raw_output_type
        if callable(output_type):
            # Don't try to send ops with callable output types yet, code path
            # not ready.
            output_type = "any"

            # TODO: Consider removing the ability for an output_type to
            # be a function - they all must be Types or ConstNodes. Probably
            # this can be done after all the existing ops can safely be converted.
            # Once that change happens, we can do this conversion in the constructor.
            # output_type = callable_output_type_to_dict(
            #     self.input_type, output_type, self.uri
            # )
        else:
            output_type = output_type.to_dict()

        # Make callable input_type args into types.Any() for now.
        input_type = self.input_type
        if isinstance(input_type, op_args.OpVarArgs):
            # This is what we do on the frontend.
            input_types = {"manyX": "invalid"}
        else:
            arg_types = copy.copy(input_type.arg_types)
            for arg_name, arg_type in arg_types.items():
                if callable(arg_type):
                    arg_types[arg_name] = types.Any()
            input_types = op_args.OpNamedArgs(arg_types).to_dict()

        serialized = {
            # To_dict() is used to send the op list to WeaveJS.
            # We should send the full URI, not just the name, but WeaveJS
            # doesn't handle that yet, so for now, send the name.
            "name": graph.op_full_name(self),
            "input_types": input_types,
            "output_type": output_type,
        }
        if self.render_info is not None:
            serialized["render_info"] = self.render_info
        if self.refine_output_type is not None:
            serialized["refine_output_type_op_name"] = self.refine_output_type.name

        return serialized

    def __repr__(self):
        return "<OpDef: %s %s>" % (self.name, self.version)

    def bind_params(
        self, args: list[typing.Any], kwargs: dict[str, typing.Any]
    ) -> collections.OrderedDict[str, graph.Node]:
        sig = pyfunc_type_util.get_signature(self.raw_resolve_fn)
        bound_params = sig.bind(*args, **kwargs)
        bound_params_with_constants = collections.OrderedDict()
        for k, v in bound_params.arguments.items():
            param = sig.parameters[k]
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                for sub_k, sub_v in v.items():
                    if not isinstance(sub_v, graph.Node):
                        sub_v = weave_internal.const(sub_v)
                    bound_params_with_constants[sub_k] = sub_v
            else:
                if not isinstance(self.input_type, op_args.OpNamedArgs):
                    raise errors.WeaveDefinitionError(
                        f"Error binding params to {self.uri} - found named params in signature, but op does not have named param args"
                    )
                param_input_type = self.input_type.arg_types[k]
                if callable(param_input_type):
                    already_bound_types = {
                        k: n.type for k, n in bound_params_with_constants.items()
                    }
                    already_bound_types = language_autocall.update_input_types(
                        self.input_type, already_bound_types
                    )
                    try:
                        param_input_type = param_input_type(already_bound_types)
                    except AttributeError as e:
                        raise errors.WeaveInternalError(
                            f"callable input_type of {self.uri} failed to accept already_bound_types of {already_bound_types}"
                        )
                if not isinstance(v, graph.Node):
                    if callable(v):
                        if not isinstance(param_input_type, types.Function):
                            raise errors.WeaveInternalError(
                                "callable passed as argument, but type is not Function. Op: %s"
                                % self.uri
                            )

                        # Allow passing in functions with fewer arguments then the op
                        # declares. E.g. for List.map I pass either of these:
                        #    lambda row, index: ...
                        #    lambda row: ...
                        sig = inspect.signature(v)
                        vars = {}
                        for name in list(param_input_type.input_types.keys())[
                            : len(sig.parameters)
                        ]:
                            vars[name] = param_input_type.input_types[name]

                        v = weave_internal.define_fn(vars, v)
                    else:
                        val_type = types.TypeRegistry.type_of(v)
                        # TODO: should type-check v here.
                        v = graph.ConstNode(val_type, v)
                bound_params_with_constants[k] = v
        return bound_params_with_constants


class BoundOpDef(OpDef):
    bind_self: typing.Optional[graph.Node]

    def __init__(self, bind_self: typing.Optional[graph.Node], op_def: OpDef) -> None:
        self.bind_self = bind_self
        self.op_def = op_def

    def __call__(self, *args, **kwargs):
        if self.bind_self is None:
            return self.op_def(*args, **kwargs)
        else:
            return self.op_def(self.bind_self, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.op_def, name)


def is_op_def(obj):
    return isinstance(obj, OpDef)


def callable_output_type_to_dict(input_type, output_type, op_name):
    if not isinstance(input_type, op_args.OpNamedArgs):
        # print(f"Failed to transform op {op_name}: Requires named args")
        return types.Any().to_dict()
    try:
        # TODO: Make this transformation more sophisticated once the type hierarchy is settled
        arg_types = {
            "input_types": types.TypedDict(
                {k: types.Type() for k, _ in input_type.arg_types.items()}
            )
        }
        return fixup_node(weave_internal.define_fn(arg_types, output_type)).to_json()
    except errors.WeaveMakeFunctionError as e:
        # print(f"Failed to transform op {op_name}: Invalid output type function")
        return types.Any().to_dict()
