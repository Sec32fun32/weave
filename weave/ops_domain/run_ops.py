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
from . import history as history_util
from ..ops_primitives import _dict_utils
from .. import util
from .. import errors
from .. import io_service

from pyarrow import compute as pc
import pyarrow as pa
from pyarrow import parquet as pq

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


run_path_fragment = """
    project {
        id
        name
        entity {
            id
            name
        }
    }
    """


def _run_config_plugin(inputs: InputAndStitchProvider, inner: str):
    config_field = _make_run_config_gql_field(inputs, inner)
    return config_field + " " + run_path_fragment


@op(
    name="run-config",
    refine_output_type=refine_config_type,
    plugins=wb_gql_op_plugin(_run_config_plugin),
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


def _run_summary_plugin(inputs: InputAndStitchProvider, inner: str):
    summary_field = _make_run_summary_gql_field(inputs, inner)
    return summary_field + " " + run_path_fragment


@op(
    name="run-summary",
    refine_output_type=refine_summary_type,
    plugins=wb_gql_op_plugin(_run_summary_plugin),
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
    plugins=wb_gql_op_plugin(lambda inputs, inner: "historyKeys"),
)
def refine_history_type(run: wdt.Run) -> types.Type:
    prop_types: dict[str, types.Type] = {}
    historyKeys = run.gql["historyKeys"]["keys"]

    for key, key_details in historyKeys.items():
        if key.startswith("system/"):
            # skip system metrics for now
            continue
        type_counts: list[history_util.TypeCount] = key_details["typeCounts"]
        wt = types.union(
            *[
                history_util.history_key_type_count_to_weave_type(tc)
                for tc in type_counts
            ]
        )
        if wt == types.UnknownType():
            util.capture_exception_with_sentry_if_available(
                errors.WeaveTypeWarning(
                    f"Unable to determine history key type for key {key} with types {type_counts}"
                ),
                (str([tc["type"] for tc in type_counts]),),
            )
            wt = types.NoneType()

        # _step is a special key that is always guaranteed to be a nonnull number.
        # other keys may be undefined at particular steps so we make them optional.
        if key in ["_step", "_runtime", "_timestamp"]:
            prop_types[key] = wt
        else:
            prop_types[key] = types.optional(wt)

    return types.List(types.TypedDict(prop_types))


class SampledHistorySpec(typing.TypedDict):
    keys: list[str]
    samples: int


def _make_run_history_gql_field(inputs: InputAndStitchProvider, inner: str):
    # Must be kept in sync with compile_domain:_field_selections_hardcode_merge

    stitch_obj = inputs.stitched_obj
    key_tree = compile_table.get_projection(stitch_obj)

    # we only pushdown the top level keys for now.
    top_level_keys = get_top_level_keys(key_tree)

    if not top_level_keys:
        # If no keys, then we cowardly refuse to blindly fetch entire history table
        return "historyKeys"

    project_fragment = """
        project {
        id
        name
        entity {
            id
            name
        }
    }
    """

    return f"""
    historyKeys
    parquetHistory(liveKeys: {json.dumps(top_level_keys)}) {{
        liveData
        parquetUrls
    }}
    {project_fragment}
    """


@op(
    name="run-history",
    refine_output_type=refine_history_type,
    plugins=wb_gql_op_plugin(_make_run_history_gql_field),
    output_type=types.List(types.TypedDict({})),
)
def history(run: wdt.Run):

    # first check and see if we have actually fetched any history rows. if we have not,
    # we are in the case where we have blindly requested the entire history object.
    # we refuse to fetch that, so instead we will just inspect the historyKeys and return
    # a dummy history object that can bte used as a proxy for downstream ops (e.g., count).

    if "parquetHistory" not in run.gql:
        last_step = run.gql["historyKeys"]["lastStep"]
        history_keys = run.gql["historyKeys"]["keys"]
        for key, key_details in history_keys.items():
            if key == "_step":
                type_counts: list[history_util.TypeCount] = key_details["typeCounts"]
                count = type_counts[0]["count"]
                break
        else:
            return []

        # generate fake steps
        steps = [{"_step": i} for i in range(count)]
        steps[-1]["_step"] = last_step
        assert len(steps) == count
        return steps

    columns = list(run.gql["historyKeys"]["keys"].keys())
    return get_history(run, columns=columns)


def get_history(run: wdt.Run, columns=None):
    # we have fetched some specific rows.
    # download the files from the urls
    io = io_service.get_sync_client()
    tables = []
    for url in run.gql["parquetHistory"]["parquetUrls"]:
        local_path = io.ensure_file_downloaded(url)
        if local_path is not None:
            path = io.fs.path(local_path)
            table = pq.read_table(path, columns=columns)
            tables.append(table)
    history = pa.concat_tables(tables)

    # turn the liveset into an arrow table. the liveset is a list of dictionaries
    live_data = run.gql["parquetHistory"]["liveData"]
    for row in live_data:
        for field in history.schema:
            if field.name not in row:
                row[field.name] = None

    # sort the history by step
    table_sorted_indices = pa.compute.bottom_k_unstable(
        table, sort_keys=["_step"], k=len(table)
    )

    # get binary fields from history schema - these are serialized json
    binary_fields = [
        field.name for field in history.schema if pa.types.is_binary(field.type)
    ]

    history = history.take(table_sorted_indices).to_pylist()

    # deserialize json
    for field in binary_fields:
        for row in history:
            if row[field] is not None:
                row[field] = json.loads(row[field])

    # parquet stores step as a float, but we want it as an int
    for row in history:
        row["_step"] = int(row["_step"])

    history.extend(live_data)

    return [
        wb_util.process_run_dict_obj(
            row,
            wb_util.RunPath(
                run.gql["project"]["entity"]["name"],
                run.gql["project"]["name"],
                run.gql["name"],
            ),
        )
        for row in history
    ]


def binary_search(
    input_list: list[typing.Any], search_key: str, target: typing.Any
) -> typing.Optional[int]:
    low = 0
    high = len(input_list) - 1

    while low <= high:
        mid = (low + high) // 2
        guess = input_list[mid][search_key]

        if guess == target:
            return mid
        if guess > target:
            high = mid - 1
        else:
            low = mid + 1
    return None


def _get_history_as_of_step(run: wdt.Run, asOfStep: int):
    history = get_history(run)
    index = binary_search(history, "_step", asOfStep)
    if index is not None:
        return history[index]
    return None


@op(
    render_info={"type": "function"},
    plugins=wb_gql_op_plugin(lambda inputs, inner: "historyKeys"),
)
def _refine_history_as_of_type(run: wdt.Run, asOfStep: int) -> types.Type:
    history_type = refine_history_type.resolve_fn(run)
    if types.List().assign_type(history_type):
        return history_type.object_type  # type: ignore
    return history_type


@op(
    name="run-historyAsOf",
    refine_output_type=_refine_history_as_of_type,
    plugins=wb_gql_op_plugin(_make_run_history_gql_field),
    output_type=types.TypedDict({}),
)
def history_as_of(run: wdt.Run, asOfStep: int):
    return _get_history_as_of_step(run, asOfStep)


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
    lambda inputs: "first: 100",
)

gql_connection_op(
    "run-loggedArtifactVersions",
    wdt.RunType,
    "outputArtifacts",
    wdt.ArtifactVersionType,
    {},
    lambda inputs: "first: 100",
)


# Section 6/6: Non Standard Business Logic Ops
@op(
    name="run-link",
    plugins=wb_gql_op_plugin(
        lambda inputs, inner: """
    displayName
    project {
        id
        name
        entity {
            id
            name
        }
    }
"""
    ),
)
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
    return wdt.ArtifactVersion.from_gql(run.gql["project"][alias])
