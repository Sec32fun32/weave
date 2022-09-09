import copy
import typing

from weave.weavejs_fixes import fixup_node

from . import errors
from . import op_args
from . import context_state
from . import weave_types as types
from . import uris
from . import weave_internal


class OpDef:
    """An Op Definition.

    Must be immediately passed to Register.register_op() after construction.
    """

    name: str
    input_type: op_args.OpArgs
    output_type: typing.Union[
        types.Type,
        typing.Callable[[typing.Dict[str, types.Type]], types.Type],
    ]
    refine_output_type: typing.Optional["OpDef"]
    setter = str
    call_fn: typing.Any
    version: typing.Optional[str]
    is_builtin: bool = False

    def __init__(
        self,
        name: str,
        input_type: op_args.OpArgs,
        output_type: typing.Union[
            types.Type,
            typing.Callable[[typing.Dict[str, types.Type]], types.Type],
        ],
        resolve_fn,
        refine_output_type: typing.Optional["OpDef"] = None,
        setter=None,
        render_info=None,
        pure=True,
        is_builtin: typing.Optional[bool] = None,
    ):
        self.name = name
        self.input_type = input_type
        self.output_type = output_type
        self.refine_output_type = refine_output_type
        self.resolve_fn = resolve_fn
        self.setter = setter
        self.render_info = render_info
        self.pure = pure
        self.is_builtin = (
            is_builtin
            if is_builtin is not None
            else context_state.get_loading_built_ins()
        )
        self.version = None
        self.lazy_call = None
        self.eager_call = None
        self.call_fn = None
        self.instance = None

    def __get__(self, instance, owner):
        # This is part of Python's descriptor protocol, and when this op_def
        # is fetched as a member of a class
        self.instance = instance
        return self

    def __call__(self, *args, **kwargs):
        if self.instance is not None:
            return self.call_fn(self.instance, *args, **kwargs)
        return self.call_fn(*args, **kwargs)

    @property
    def uri(self):
        return self.name

    @property
    def simple_name(self):
        return uris.WeaveURI.parse(self.name).full_name

    @property
    def is_mutation(self):
        return getattr(self.resolve_fn, "is_mutation", False)

    @property
    def is_async(self):
        return not callable(self.output_type) and self.output_type.name == "Run"

    def to_dict(self):
        output_type = self.output_type
        if callable(output_type):
            # TODO: Consider removing the ability for an output_type to
            # be a function - they all must be Types or ConstNodes. Probably
            # this can be done after all the existing ops can safely be converted.
            # Once that change happens, we can do this conversion in the constructor.
            output_type = callable_output_type_to_dict(
                self.input_type, output_type, self.uri
            )
        else:
            output_type = output_type.to_dict()

        # Make callable input_type args into types.Any() for now.
        input_type = self.input_type
        if not isinstance(input_type, op_args.OpNamedArgs):
            raise errors.WeaveSerializeError(
                "serializing op with non-named-args input_type not yet implemented"
            )
        arg_types = copy.copy(input_type.arg_types)
        for arg_name, arg_type in arg_types.items():
            if callable(arg_type):
                arg_types[arg_name] = types.Any()
        input_types = op_args.OpNamedArgs(arg_types).to_dict()

        serialized = {
            "name": self.uri,
            "input_types": input_types,
            "output_type": output_type,
        }
        if self.render_info is not None:
            serialized["render_info"] = self.render_info
        if self.refine_output_type is not None:
            serialized["refine_output_type_op_name"] = self.refine_output_type.name

        return serialized

    def __str__(self):
        return "<OpDef: %s>" % self.name


def is_op_def(obj):
    return isinstance(obj, OpDef)


def callable_output_type_to_dict(input_type, output_type, op_name):
    if not isinstance(input_type, op_args.OpNamedArgs):
        print(f"Failed to transform op {op_name}: Requires named args")
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
        print(f"Failed to transform op {op_name}: Invalid output type function")
        return types.Any().to_dict()
