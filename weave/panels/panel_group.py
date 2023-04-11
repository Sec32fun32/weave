import dataclasses
import copy
import typing
import weave

from .. import weave_internal
from .. import graph
from .. import panel
from .. import panel_util

ItemsType = typing.TypeVar("ItemsType")

# I pulled in all the type information from PanelBank, but we're not
# using it all yet.


class LayoutParameters(typing.TypedDict):
    x: int
    y: int
    w: int
    h: int


class LayedOutPanel(typing.TypedDict):
    id: str
    layout: LayoutParameters


class PanelBankFlowSectionConfig(typing.TypedDict):
    snapToColumns: bool
    columnsPerPage: int
    rowsPerPage: int
    gutterWidth: int
    boxWidth: int
    boxHeight: int


class PanelBankSectionConfig(typing.TypedDict):
    id: str
    name: str
    panels: typing.List[LayedOutPanel]
    isOpen: bool
    flowConfig: PanelBankFlowSectionConfig
    type: str  # this 'grid' | 'flow' in ts
    sorted: int  # This is an enum in js


@weave.type()
class GroupConfig(typing.Generic[ItemsType]):
    showExpressions: bool = dataclasses.field(default_factory=lambda: False)
    layered: bool = dataclasses.field(default_factory=lambda: False)
    preferHorizontal: bool = dataclasses.field(default_factory=lambda: False)
    equalSize: bool = dataclasses.field(default_factory=lambda: False)
    style: str = dataclasses.field(default_factory=lambda: "")
    items: ItemsType = dataclasses.field(default_factory=dict)  # type: ignore
    grid: bool = dataclasses.field(default_factory=lambda: False)
    gridConfig: typing.Optional[PanelBankSectionConfig] = dataclasses.field(
        default_factory=lambda: None
    )
    liftChildVars: typing.Optional[bool] = dataclasses.field(
        default_factory=lambda: None
    )
    allowedPanels: typing.Optional[list[str]] = dataclasses.field(
        default_factory=lambda: None
    )
    enableAddPanel: typing.Optional[bool] = dataclasses.field(
        default_factory=lambda: None
    )
    childNameBase: typing.Optional[str] = dataclasses.field(
        default_factory=lambda: None
    )


GroupConfigType = typing.TypeVar("GroupConfigType")


@weave.type()
class Group(panel.Panel, typing.Generic[GroupConfigType]):
    id = "Group"
    config: typing.Optional[GroupConfigType] = dataclasses.field(
        default_factory=lambda: None
    )
    # items: typing.TypeVar("items") = dataclasses.field(default_factory=dict)

    def __init__(self, input_node=graph.VoidNode(), vars=None, config=None, **options):
        if vars is None:
            vars = {}
        super().__init__(input_node=input_node, vars=vars)
        self.config = config
        if self.config is None:
            self.config = GroupConfig()
        if "items" in options:
            self.config.items = options["items"]
        if "showExpressions" in options:
            self.config.showExpressions = options["showExpressions"]
        if "layered" in options:
            self.config.layered = options["layered"]
        if "preferHorizontal" in options:
            self.config.preferHorizontal = options["preferHorizontal"]
        if "equalSize" in options:
            self.config.equalSize = options["equalSize"]
        if "style" in options:
            self.config.style = options["style"]
        self._normalize()

    def _normalize(self, frame=None):
        if frame is None:
            frame = {}
        frame = copy.copy(frame)
        frame.update(self.vars)

        items = {}
        for name, p in self.config.items.items():
            injected = panel.run_variable_lambdas(p, frame)
            child = panel_util.child_item(injected)
            if not isinstance(child, graph.Node):
                child._normalize(frame)
            items[name] = child

            # We build up config one item at a time. Construct a version
            # with the current items so that we can do type_of on it (type_of
            # will fail if we have a lambda in the config).
            partial_config = dataclasses.replace(self.config, items=items)
            config_var = weave_internal.make_var_node(
                weave.type_of(partial_config), "self"
            )
            frame[name] = config_var.items[name]

        self.config.items = items

    # @property
    # def config(self):
    #     self._normalize()
    #     return {"items": {k: i.to_json() for k, i in self.items.items()}}
