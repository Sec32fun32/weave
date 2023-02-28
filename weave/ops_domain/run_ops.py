# W&B API Weave Ops: Runs
#
# Run projection pushdown strategy
# --------------------------------
#
# Its important for performance
# that we only select the run user data (config/summary/history) columns that
# we need. We can use the stitched graph to do that for the relevant ops, any
# pick ops connected to config/summary are used to determine the keys argument
# to the graphql field.
#
# But we also need to consider refinement. There are two different ways
# refinment will happen: explicit where there is a request for a refinement
# op like refine_summary_type in the graph, and implicit, which is all other cases.
# In the explicit case we must fetch all columns so we can produce the full
# type.
#
# The implicit case always happens, because compile refines all ops in the
# graph to fix incoming Weave0 graphs for compatibility with Weave1. But this
# refinement only needs to provide the subset of the type that will be used
# for dispatch. Ie we can compute the type of only the summary fields needed
# by the query.
#
# So the correct strategy is: if a refinement descendent is explicitly requested,
# select all fields. Otherwise, select the fields described by pick descendents.
#
# We do not yet perform projection pushdown for history. Currently to fetch
# specific history columns from the W&B API, you need to use the sampledHistory
# graphql field. But it's incorrect to make a request for one "historySpec"
# containing all the required keys, because the W&B backend will return
# only rows that have all keys present. We can instead request one spec
# for each history key, always also including the _step key, and then zip
# the results back together ourselves. If we do so we'll have to do it unsampled.
# It may be better to just move to the Runs2 strategy where Weave is directly
# responsible for scanning the data instead of using the sampledHistory field.

import json
import typing
import logging
from .. import compile_table
from ..compile_domain import wb_gql_op_plugin, InputAndStitchProvider
from ..api import op
from .. import weave_types as types
from . import wb_domain_types as wdt
from ..language_features.tagging.make_tag_getter_op import make_tag_getter_op
from .wandb_domain_gql import (
    gql_prop_op,
    gql_direct_edge_op,
    gql_connection_op,
    _make_alias,
)
from . import wb_util
from ..ops_primitives import _dict_utils

from ..compile_table import KeyTree

# number of rows of example data to look at to determine history type
ROW_LIMIT_FOR_TYPE_INTERROGATION = 10

# Section 1/6: Tag Getters
run_tag_getter_op = make_tag_getter_op("run", wdt.RunType, op_name="tag-run")

# Section 2/6: Root Ops
# None

# Section 3/6: Attribute Getters
gql_prop_op(
    "run-jobType",
    wdt.RunType,
    "jobType",
    types.String(),
)

gql_prop_op(
    "run-jobtype",
    wdt.RunType,
    "jobType",
    types.String(),
)

run_name = gql_prop_op(
    "run-name",
    wdt.RunType,
    "displayName",
    types.String(),
)

gql_prop_op(
    "run-internalId",
    wdt.RunType,
    "id",
    types.String(),
)

gql_prop_op(
    "run-id",
    wdt.RunType,
    "name",
    types.String(),
)

gql_prop_op(
    "run-createdAt",
    wdt.RunType,
    "createdAt",
    types.Timestamp(),
)
gql_prop_op(
    "_run-historykeyinfo",
    wdt.RunType,
    "historyKeys",
    types.Dict(types.String(), types.Any()),
)

gql_prop_op(
    "run-runtime",
    wdt.RunType,
    "computeSeconds",
    types.Number(),
)

gql_prop_op(
    "run-heartbeatAt",
    wdt.RunType,
    "heartbeatAt",
    types.Timestamp(),
)


def get_top_level_keys(key_tree: KeyTree) -> list[str]:
    top_level_keys = list(
        map(
            _dict_utils.unescape_dots,
            set(
                next(iter(_dict_utils.split_escaped_string(key)))
                for key in key_tree.keys()
            ),
        )
    )
    return top_level_keys


def config_to_values(config: dict) -> dict:
    """
    Unfortunately config values from wandb have their data located at the .value
    property inside of the config object.
    """
    return {
        key: value["value"] if isinstance(value, dict) and "value" in value else value
        for key, value in config.items()
    }


@op(
    render_info={"type": "function"},
    plugins=wb_gql_op_plugin(lambda inputs, inner: "config"),
)
def refine_config_type(run: wdt.Run) -> types.Type:
    config_field_s = None
    try:
        # If config was explicitly requested, this will be the case.
        config_field_s = run.gql["config"]
    except KeyError:
        # Otherwise we'll be refining implicitly in compile, but we only need
        # to provide the summary requested by the rest of the graph.
        config_field_s = run.gql["configSubset"]
    if not config_field_s:
        config_field_s = "{}"

    return wb_util.process_run_dict_type(config_to_values(json.loads(config_field_s)))


def _make_run_config_gql_field(inputs: InputAndStitchProvider, inner: str):
    # Must be kept in sync with compile_domain:_field_selections_hardcode_merge
    stitch_obj = inputs.stitched_obj
    key_tree = compile_table.get_projection(stitch_obj)
    # we only pushdown the top level keys for now.

    top_level_keys = get_top_level_keys(key_tree)
    if not top_level_keys:
        # If no keys, then we must select the whole object
        return "configSubset: config"
    return f"configSubset: config(keys: {json.dumps(top_level_keys)})"


@op(
    name="run-config",
    refine_output_type=refine_config_type,
    plugins=wb_gql_op_plugin(_make_run_config_gql_field),
)
def config(run: wdt.Run) -> dict[str, typing.Any]:
    return wb_util.process_run_dict_obj(
        config_to_values(json.loads(run.gql["configSubset"] or "{}")),
        wb_util.RunPath(
            run.gql["project"]["entity"]["name"],
            run.gql["project"]["name"],
            run.gql["name"],
        ),
    )


@op(
    render_info={"type": "function"},
    # When refine_summary_type is explicitly requested in the graph, we ask for
    # the entire summaryMetrics field.
    plugins=wb_gql_op_plugin(lambda inputs, inner: "summaryMetrics"),
)
def refine_summary_type(run: wdt.Run) -> types.Type:
    summary_field_s = None
    try:
        # If summary was explicitly requested, this will be the case.
        summary_field_s = run.gql["summaryMetrics"]
    except KeyError:
        # Otherwise we'll be refining implicitly in compile, but we only need
        # to provide the summary requested by the rest of the graph.
        summary_field_s = run.gql["summaryMetricsSubset"]
    if not summary_field_s:
        summary_field_s = "{}"

    return wb_util.process_run_dict_type(json.loads(summary_field_s))


def _make_run_summary_gql_field(inputs: InputAndStitchProvider, inner: str):
    # Must be kept in sync with compile_domain:_field_selections_hardcode_merge

    stitch_obj = inputs.stitched_obj
    key_tree = compile_table.get_projection(stitch_obj)

    # we only pushdown the top level keys for now.
    top_level_keys = get_top_level_keys(key_tree)
    if not top_level_keys:
        # If no keys, then we must select the whole object
        return "summaryMetricsSubset: summaryMetrics"
    return f"summaryMetricsSubset: summaryMetrics(keys: {json.dumps(top_level_keys)})"


@op(
    name="run-summary",
    refine_output_type=refine_summary_type,
    plugins=wb_gql_op_plugin(_make_run_summary_gql_field),
)
def summary(run: wdt.Run) -> dict[str, typing.Any]:
    return wb_util.process_run_dict_obj(
        json.loads(run.gql["summaryMetricsSubset"] or "{}"),
        wb_util.RunPath(
            run.gql["project"]["entity"]["name"],
            run.gql["project"]["name"],
            run.gql["name"],
        ),
    )


@op(
    render_info={"type": "function"},
    plugins=wb_gql_op_plugin(
        lambda inputs, inner: "historyKeys, history(samples: 1000)"
    ),
)
def _refine_history_type(run: wdt.Run) -> types.Type:
    # The Weave0 implementation loads the entire history & the historyKeys. This
    # is very inefficient and actually incomplete. Here, for performance
    # reasons, we will simply sample the first 1000 rows and use that to determine
    # the type. This means that some columns will not be perfectly typed. Once
    # we have fully implemented a mapping from historyKeys to Weave types, we
    # can remove the history scan. Critically, Table types could be artifact
    # tables or run tables. In Weave0 we need to figure this out eagerly.
    # However, i think we can defer this and that will be the last thing to
    # remove needing to read any history.
    prop_types: dict[str, types.Type] = {}
    historyKeys = run.gql["historyKeys"]["keys"]
    example_history_rows = run.gql["history"][:ROW_LIMIT_FOR_TYPE_INTERROGATION]
    keys_needing_type = set()

    for key, key_details in historyKeys.items():
        key_types = [tc["type"] for tc in key_details["typeCounts"]]
        if len(key_types) == 1:
            if key_types[0] == "number":
                prop_types[key] = types.Number()
                continue
            elif key_types[0] == "string":
                prop_types[key] = types.String()
                continue
        # TODO: We need to finish the historyKeys -> Weave type mapping
        logging.warning(
            f"Unable to determine history key type for key {key} with types {key_types}"
        )
        keys_needing_type.add(key)

    if len(keys_needing_type) > 0:
        example_row_types = [
            wb_util.process_run_dict_type(json.loads(row or "{}")).property_types
            for row in example_history_rows
        ]
        for key in keys_needing_type:
            cell_types = []
            for row_type in example_row_types:
                if key in row_type:
                    cell_types.append(row_type[key])
                else:
                    cell_types.append(types.NoneType())
            prop_types[key] = types.union(*cell_types)

    return types.List(types.TypedDict(prop_types))


@op(
    name="run-history",
    refine_output_type=_refine_history_type,
    plugins=wb_gql_op_plugin(
        lambda inputs, inner: "historyKeys, history(samples: 1000)"
    ),
)
def history(run: wdt.Run) -> list[dict[str, typing.Any]]:
    return [
        wb_util.process_run_dict_obj(
            json.loads(row),
            wb_util.RunPath(
                run.gql["project"]["entity"]["name"],
                run.gql["project"]["name"],
                run.gql["name"],
            ),
        )
        for row in run.gql["history"]
    ]


def _history_as_of_plugin(inputs, inner):
    min_step = (
        inputs.raw["asOfStep"]
        if "asOfStep" in inputs.raw and inputs.raw["asOfStep"] != None
        else 0
    )
    max_step = min_step + 1
    alias = _make_alias(str(inputs.raw["asOfStep"]), prefix="history")
    return f"{alias}: history(minStep: {min_step}, maxStep: {max_step})"


@op(
    render_info={"type": "function"},
    plugins=wb_gql_op_plugin(_history_as_of_plugin),
)
def _refine_history_as_of_type(run: wdt.Run, asOfStep: int) -> types.Type:
    alias = _make_alias(str(asOfStep), prefix="history")
    return wb_util.process_run_dict_type(json.loads(run.gql[alias] or "{}"))


@op(
    name="run-historyAsOf",
    refine_output_type=_refine_history_as_of_type,
    plugins=wb_gql_op_plugin(_history_as_of_plugin),
)
def history_as_of(run: wdt.Run, asOfStep: int) -> dict[str, typing.Any]:
    alias = _make_alias(str(asOfStep), prefix="history")
    return json.loads(run.gql[alias] or "{}")


# Section 4/6: Direct Relationship Ops
gql_direct_edge_op(
    "run-user",
    wdt.RunType,
    "user",
    wdt.UserType,
)

gql_direct_edge_op(
    "run-project",
    wdt.RunType,
    "project",
    wdt.ProjectType,
)

# Section 5/6: Connection Ops
gql_connection_op(
    "run-usedArtifactVersions",
    wdt.RunType,
    "inputArtifacts",
    wdt.ArtifactVersionType,
    {},
    lambda inputs: "first: 50",
)

gql_connection_op(
    "run-loggedArtifactVersions",
    wdt.RunType,
    "outputArtifacts",
    wdt.ArtifactVersionType,
    {},
    lambda inputs: "first: 50",
)


# Section 6/6: Non Standard Business Logic Ops
@op(name="run-link", plugins=wb_gql_op_plugin(lambda inputs, inner: "displayName"))
def link(run: wdt.Run) -> wdt.Link:
    return wdt.Link(
        run.gql["displayName"],
        f'/{run.gql["project"]["entity"]["name"]}/{run.gql["project"]["name"]}/runs/{run.gql["name"]}',
    )


def run_logged_artifact_version_gql_plugin(inputs, inner):
    artifact_name = inputs.raw["artifactVersionName"]
    alias = _make_alias(artifact_name, prefix="artifact")
    if ":" not in artifact_name:
        artifact_name += ":latest"
    artifact_name = json.dumps(artifact_name)
    return f"""
    project {{
        {alias}: artifact(name: {artifact_name}) {{
            {wdt.ArtifactVersion.REQUIRED_FRAGMENT}
            {inner}
        }}
    }}"""


@op(
    name="run-loggedArtifactVersion",
    plugins=wb_gql_op_plugin(run_logged_artifact_version_gql_plugin),
)
def run_logged_artifact_version(
    run: wdt.Run, artifactVersionName: str
) -> wdt.ArtifactVersion:
    alias = _make_alias(artifactVersionName, prefix="artifact")
    return wdt.ArtifactVersion(run.gql["project"][alias])
