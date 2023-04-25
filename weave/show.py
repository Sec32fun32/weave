import json
import random
import string
import urllib
import typing

from IPython.display import display
from IPython.display import IFrame

from . import context
from . import graph
from . import panel
from . import node_ref
from . import weave_types as types
from . import weavejs_fixes
from . import storage
from . import util
from . import errors
from . import usage_analytics
from . import ref_base
from . import artifact_fs
from . import ops


def make_varname_for_type(t: types.Type):
    if isinstance(t, types.List) and isinstance(t.object_type, types.TypedDict):
        return "table"
    return t.name


def make_container(
    obj: typing.Union[panel.Panel, graph.Node], name: str
) -> panel.Panel:
    from weave.panels import Group

    return Group(preferHorizontal=True, showExpressions=True, items={name: obj})


def make_show_obj(obj: typing.Any) -> tuple[graph.Node, str]:
    node: graph.Node
    if obj is None:
        return graph.VoidNode(), "panel0"
    elif isinstance(obj, panel.Panel):
        return obj, obj.id + "0"
    elif isinstance(obj, graph.Node):
        ref = node_ref.node_to_ref(obj)
        if ref is not None and isinstance(ref, artifact_fs.FilesystemArtifactRef):
            name = ref.name
        else:
            name = make_varname_for_type(obj.type)

        return obj, name
    elif isinstance(obj, ref_base.Ref):
        if isinstance(obj, artifact_fs.FilesystemArtifactRef):
            name = obj.name
            uri = obj.branch_uri
        else:
            name = make_varname_for_type(obj.type)
            uri = obj.uri
        return ops.get(uri), name

    if types.TypeRegistry.has_type(obj):
        names = util.find_names(obj)

        ref = storage.save(obj, name=names[-1])
        node = ops.get(ref.uri)
        return node, make_varname_for_type(ref.type)

    raise errors.WeaveTypeError(
        "%s not yet supported. Create a weave.Type to add support." % type(obj)
    )


# Broken out into to separate function for testing
def _show_params(obj):
    # Get a weave node (expression) that will return the object, and something to call it
    node, var_name = make_show_obj(obj)

    # Place the node inside a root group, so the user can add panels.
    ui_root = make_container(node, var_name)

    # Name the panel artifact after the object's variable name for now,
    # and only create a new one if the name is not take yet.
    # If the name exists, we'll render whatever is already stored there!
    panel_name = "dashboard-" + var_name
    panel_ref = storage.get_local_version_ref(panel_name, "latest")
    if panel_ref is None:
        panel_ref = storage.save(ui_root, name=f"{panel_name}:latest")

    # convert panel_ref to a a get expression.
    show_node = ops.get(panel_ref.branch_uri)

    return {"weave_node": weavejs_fixes.fixup_node(show_node)}


def show_url(obj=None):
    params = _show_params(obj)
    panel_url = f"{context.get_frontend_url()}/__frontend/weave_jupyter?fullScreen"
    if "weave_node" in params:
        panel_url += "&expNode=%s" % urllib.parse.quote(
            json.dumps(params["weave_node"].to_json())
        )
    if "panel_id" in params:
        panel_url += "&panelId=%s" % urllib.parse.quote(params["panel_id"])
    if "panel_config" in params:
        panel_url += "&panelConfig=%s" % urllib.parse.quote(
            json.dumps(params["panel_config"])
        )
    return panel_url


def show(obj=None, height=400):
    if not util.is_notebook():
        raise RuntimeError(
            "`weave.show()` can only be called within notebooks. To extract the value of "
            "a weave node, try `weave.use()`."
        )

    usage_analytics.show_called()
    panel_url = show_url(obj)

    iframe = IFrame(panel_url, "100%", "%spx" % height)
    display(iframe)


def _ipython_display_method_(self):
    show(self)


# Inject _ipython_display_ methods on classes we want to automatically
# show when the last expression in a notebook cell produces them.
graph.Node._ipython_display_ = _ipython_display_method_  # type: ignore
panel.Panel._ipython_display_ = _ipython_display_method_  # type: ignore
ref_base.Ref._ipython_display_ = _ipython_display_method_  # type: ignore
