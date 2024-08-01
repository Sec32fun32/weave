from weave import registry_mem


def make_error_message(missing_ops, section_name):
    error_msg = f"{len(missing_ops)} Missing {section_name} Ops: \n"
    missing_ops.sort()
    no_prefix_ops = [op for op in missing_ops if "-" not in op]
    prefixed_ops = [op for op in missing_ops if "-" in op]
    error_msg += "* No Prefix:\n" + "\n".join(
        [f"  * [ ] `{op}`" for op in no_prefix_ops]
    )
    curr_prefix = None
    for op in prefixed_ops:
        op_prefix = op.split("-")[0]
        error_msg += "\n"
        if op_prefix != curr_prefix:
            curr_prefix = op_prefix
            error_msg += "* " + op_prefix + ":\n"
        error_msg += f"  * [ ] `{op}`"
    return error_msg


def test_op_coverage():
    ops = registry_mem.memory_registry.list_ops()
    all_py_names = set([op.name for op in ops])
    missing_visible_ops = list(
        visible_js_ops - js_op_exceptions - js_ops_with_new_names - all_py_names
    )
    missing_hidden_ops = list(
        hidden_js_ops - js_op_exceptions - js_ops_with_new_names - all_py_names
    )
    total_missing = len(missing_visible_ops) + len(missing_hidden_ops)
    error_msg = (
        f"**{total_missing} Missing Ops**\n\n"
        + make_error_message(missing_visible_ops, "Visible")
        + "\n\n"
        + make_error_message(missing_hidden_ops, "Hidden")
    )

    assert total_missing == 0, error_msg


js_ops_with_new_names = set(
    [
        "pick",
        "index",
        "dict-pick",
        "file-directUrlAsOf",
        "file-artifactVersion",
        "file-directUrl",
    ]
)

js_op_exceptions = set(
    [
        # Special Ops to support Weave1
        "type-__newType__",
        # We don't need to support converter panels (it is handled by the engine)
        "panel-projection",
        "panel-merge",
        "panel-runs-table",
        "panel-table",
        # Hidden ops with no product usage
        "if",
        "mapcount",
        "throwError",
        "get-tag",
        "internal-lambdaClosureArgBridge",
        "artifactMembership-id",
        "artifactType-sequences",
        "artifactType-portfolios",
        "artifactVersion-defaultFile",
        "artifactVersion-fileReturnType",
        "artifactVersion-state",
        "artifactVersion-updateAliasActions",
        "date_round-day",
        "date_round-hour",
        "date_round-minute",
        "date_round-quarter",
        "date_round-year",
        "date-sub",
        "dates-Equal",
        "dates-min",
        "entity-internalId",
        "Geo-selected",
        "Scatter-selected",
        "local-snowflaketable",
        "localArtifact-get",
        "number-roundtenth",
        "number-roundthousand",
        "number-roundHundredth",
        "op-non_none",
        "org-members",
        "project-reports",
        "project-run",  # This is used in the demo compute graph... surprised nowhere else
        "report-name",
        "report-description",
        "report-stargazers",
        "root-allEntities",
        "root-featuredreports",
        "root-localArtifact",
        "root_number-range",
        "tablerow-table",
        "type-string",
        "typedDict-values",
        "user-id",
        "user-runs",
        # Hidden ops only used in other op resolvers
        "list-PCA",
        "list-UMAP",
        "list-tSNE",
        "artifactVersion-historyStep",
        "root_number-binsfixed",
    ]
)


visible_js_ops = set(
    [
        "numbers-sum",
        "numbers-avg",
        "numbers-argmax",
        "numbers-argmin",
        "numbers-stddev",
        "numbers-min",
        "numbers-max",
        "number-add",
        "number-sub",
        "number-mult",
        "number-div",
        "number-modulo",
        "number-powBinary",
        "number-equal",
        "number-notEqual",
        "number-less",
        "number-greater",
        "number-lessEqual",
        "number-greaterEqual",
        "number-toString",
        "number-abs",
        "number-toTimestamp",
        "number-negate",
        "string-equal",
        "string-notEqual",
        "string-len",
        "string-add",
        "string-append",
        "string-prepend",
        "string-split",
        "string-partition",
        "string-startsWith",
        "string-endsWith",
        "string-isAlpha",
        "string-isNumeric",
        "string-isAlnum",
        "string-lower",
        "string-upper",
        "string-slice",
        "string-replace",
        "string-findAll",
        "string-contains",
        "string-strip",
        "string-lStrip",
        "string-rStrip",
        "string-levenshtein",
        "and",
        "or",
        "boolean-not",
        "boolean-not",
        "isNone",
        "pick",
        "entity-name",
        "entity-link",
        "file-size",
        "file-digest",
        "file-table",
        "file-joinedTable",
        "file-partitionedTable",
        "file-contents",
        "tag-project",
        "project-createdAt",
        "project-name",
        "project-runs",
        "project-artifactType",
        "project-artifactTypes",
        "project-artifact",
        "project-artifactVersion",
        "root-project",
        "tag-run",
        "run-name",
        "run-jobType",
        "run-user",
        "run-createdAt",
        "run-heartbeatAt",
        "run-config",
        "run-summary",
        "run-history",
        "run-loggedArtifactVersion",
        "run-loggedArtifactVersions",
        "run-usedArtifactVersions",
        "run-runtime",
        "artifactVersion-name",
        "artifactVersion-versionId",
        "artifactVersion-size",
        "artifactVersion-createdAt",
        "artifactVersion-files",
        "artifactVersion-file",
        "artifactVersion-usedBy",
        "artifactVersion-metadata",
        "artifactVersion-aliases",
        "artifactVersion-link",
        "asset-file",
        "count",
        "joinToStr",
        "index",
        "sort",
        "filter",
        "dropna",
        "map",
        "join",
        "concat",
        "contains",
        "artifact-name",
        "artifact-versions",
        "artifact-link",
        "artifactType-name",
        "artifactType-artifacts",
        "artifactType-artifactVersions",
        "table-rows",
        "partitionedtable-rows",
        "partitionedtable-rowsType",
        "partitionedtable-file",
        "joinedtable-rows",
        "joinedtable-rowsType",
        "joinedtable-file",
        "local-sqlconnection",
        "user-username",
        "panel-merge",
        "panel-table",
        "panel-projection",
        "panel-runs-table",
    ]
)

hidden_js_ops = set(
    [
        "list",
        "dict",
        "number-pow",
        "number-floor",
        "number-roundthousand",
        "number-roundHundredth",
        "number-roundtenth",
        "number-toFixed",
        "number-toByteString",
        "root_number-binsfixed",
        "numbers-binsequal",
        "number-bin",
        "root_number-range",
        "number-sin",
        "throwError",
        "string-in",
        "date-sub",
        "date-toNumber",
        "dates-min",
        "dates-equal",
        "date_round-year",
        "date_round-quarter",
        "date_round-month",
        "date_round-week",
        "date_round-day",
        "date_round-hour",
        "date_round-minute",
        "boolean-equal",
        "boolean-notEqual",
        "type-string",
        "dict-pick",
        "typedDict-values",
        "object-keytypes",
        "merge",
        "entity-internalId",
        "entity-isTeam",
        "entity-projects",
        "entity-portfolios",
        "entity-org",
        "file-type",
        "file-dir",
        "file-path",
        "file-directUrl",
        "file-directUrlAsOf",
        "file-media",
        "file-artifactVersion",
        "project-internalId",
        "project-entity",
        "project-link",
        "project-run",
        "project-filteredRuns",
        "project-reports",
        "project-artifacts",
        "project-runQueues",
        "root-entity",
        "root-artifactVersion",
        "root-org",
        "root-user",
        "root-viewer",
        "root-featuredreports",
        "root-allProjects",
        "root-allReports",
        "root-allArtifacts",
        "root-allEntities",
        "rpt_weekly_users_by_country_by_repo",
        "rpt_weekly_repo_users_by_persona",
        "rpt_weekly_engaged_user_count_by_repo",
        "rpt_repo_gpu_backends",
        "rpt_versus_other_repos",
        "rpt_runtime_buckets",
        "rpt_user_model_train_freq",
        "rpt_runs_versus_other_repos",
        "rpt_product_usage",
        "run-internalId",
        "run-id",
        "run-link",
        "run-project",
        "run-jobtype",
        "_run-historykeyinfo",
        "run-historyAsOf",
        "artifactVersion-state",
        "artifactVersion-digest",
        "artifactVersion-description",
        "artifactVersion-id",
        "artifactVersion-defaultFile",
        "artifactVersion-referenceCount",
        "artifactVersion-createdBy",
        "artifactVersion-createdByUser",
        "artifactVersion-hash",
        "artifactVersion-artifactSequence",
        "artifactVersion-artifactType",
        "artifactVersion-updateAliasActions",
        "artifactVersion-artifactCollections",
        "artifactVersion-memberships",
        "artifactVersion-historyStep",
        "artifactVersion-isWeaveObject",
        "artifactVersion-historyMetrics",
        "asset-artifactVersion",
        "mapcount",
        "offset",
        "limit",
        "list-createIndexCheckpointTag",
        "tag-indexCheckpoint",
        "mapEach",
        "groupby",
        "group-groupkey",
        "joinAll",
        "tag-joinObj",
        "unnest",
        "unique",
        "flatten",
        "list-tSNE",
        "list-UMAP",
        "list-PCA",
        "table-2DProjection",
        "range",
        "get-tag",
        "if",
        "internal-lambdaClosureArgBridge",
        "artifact-id",
        "artifact-description",
        "artifact-aliases",
        "artifact-type",
        "artifact-lastMembership",
        "artifact-createdAt",
        "artifact-project",
        "artifact-memberships",
        "artifact-membershipForAlias",
        "artifact-isPortfolio",
        "artifactAlias-alias",
        "artifactAlias-artifact",
        "artifactMembership-id",
        "artifactMembership-collection",
        "artifactMembership-artifactVersion",
        "artifactMembership-createdAt",
        "artifactMembership-commitHash",
        "artifactMembership-versionIndex",
        "artifactMembership-aliases",
        "artifactMembership-link",
        "artifactType-sequences",
        "artifactType-portfolios",
        "table-rowsType",
        "tablerow-table",
        "dir-pathReturnType",
        "dir-path",
        "dir-_as_w0_dict_",
        "localpathReturnType",
        "localpath",
        "root-localArtifact",
        "root-string",
        "localArtifact-get",
        "file-readcsv",
        "file-pandasreadcsv",
        "local-snowflaketable",
        "sqlconnection-tables",
        "sqlconnection-tablesType",
        "sqlconnection-table",
        "getReturnType",
        "get",
        "save",
        "artifactVersion-fileReturnType",
        "Ref-get",
        "execute",
        "function-__call__",
        "Scatter-selected",
        "Geo-selected",
        "Facet-selected",
        "Object-__getattr__",
        "type-__newType__",
        "op_get_tag_type",
        "op_make_type_tagged",
        "op_make_type_key_tag",
        "op-non_none",
        "none-coalesce",
        "org-members",
        "org-reports",
        "org-projects",
        "org-artifacts",
        "org-name",
        "org-teams",
        "report-name",
        "report-link",
        "report-description",
        "report-createdAt",
        "report-project",
        "report-creator",
        "report-viewcount",
        "report-stargazers",
        "runQueue-id",
        "user-id",
        "user-name",
        "user-email",
        "user-link",
        "user-runs",
        "user-entities",
        "normalizeUserCounts",
    ]
)
