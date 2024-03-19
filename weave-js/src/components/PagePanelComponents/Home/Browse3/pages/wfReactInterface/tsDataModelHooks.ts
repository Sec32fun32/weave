/**
 * This file defines `tsWFDataModelHooks` which conforms to the the
 * `WFDataModelHooksInterface`, providing access to the Weaveflow data model
 * backed by the "Trace Server" engine.
 */

import {isSimpleTypeShape, union} from '@wandb/weave/core/model/helpers';
import * as _ from 'lodash';
import {useCallback, useEffect, useMemo, useRef, useState} from 'react';

import * as Types from '../../../../../../core/model/types';
import {useDeepMemo} from '../../../../../../hookUtils';
// import {refStringToRefDict} from '../wfInterface/naive';
import {callCache} from './cache';
import {WANDB_ARTIFACT_REF_PREFIX, WEAVE_REF_PREFIX} from './constants';
import * as traceServerClient from './traceServerClient';
import {useGetTraceServerClientContext} from './traceServerClientContext';
import {
  opVersionRefOpCategory,
  refStringToRefDict,
  refUriToOpVersionKey,
  typeNameToCategory,
} from './utilities';
import {
  CallFilter,
  CallKey,
  CallSchema,
  Loadable,
  LoadableWithError,
  ObjectVersionFilter,
  ObjectVersionKey,
  ObjectVersionSchema,
  OpCategory,
  OpVersionFilter,
  OpVersionKey,
  OpVersionSchema,
  RawSpanFromStreamTableEra,
  RefMutation,
  TableQuery,
  WFDataModelHooksInterface,
} from './wfDataModelHooksInterface';

const projectIdFromParts = ({
  entity,
  project,
}: {
  entity: string;
  project: string;
}) => `${entity}/${project}`;

const makeTraceServerEndpointHook = <
  FN extends keyof traceServerClient.TraceServerClient,
  Input extends any[],
  Output
>(
  traceServerFnName: FN,
  preprocessFn: (
    ...input: Input
  ) => Parameters<traceServerClient.TraceServerClient[FN]>[0],
  postprocessFn: (
    res: Awaited<ReturnType<traceServerClient.TraceServerClient[FN]>>,
    ...input: Input
  ) => Output
) => {
  const useTraceServerRequest = (
    ...input: Input
  ): LoadableWithError<Output> => {
    input = useDeepMemo(input);
    const getTsClient = useGetTraceServerClientContext();
    const client = getTsClient();
    const [state, setState] = useState<LoadableWithError<Output>>({
      loading: true,
      result: null,
      error: null,
    });

    useEffect(() => {
      setState({loading: true, result: null, error: null});
      const req = preprocessFn(...input);
      client[traceServerFnName](req as any)
        .then(res => {
          const output = postprocessFn(res as any, ...input);
          setState({loading: false, result: output, error: null});
        })
        .catch(err => {
          setState({loading: false, result: null, error: err});
        });
    }, [client, input]);

    return state;
  };
  return useTraceServerRequest;
};

const useMakeTraceServerEndpoint = <
  FN extends keyof traceServerClient.TraceServerClient,
  Input extends any[],
  Output
>(
  traceServerFnName: FN,
  preprocessFn: (
    ...input: Input
  ) => Parameters<traceServerClient.TraceServerClient[FN]>[0],
  postprocessFn: (
    res: Awaited<ReturnType<traceServerClient.TraceServerClient[FN]>>
  ) => Output
) => {
  const getTsClient = useGetTraceServerClientContext();
  const client = getTsClient();
  const traceServerRequest = useCallback(
    (...input: Input): Promise<Output> => {
      return client[traceServerFnName](preprocessFn(...input) as any).then(
        res => {
          return postprocessFn(res as any);
        }
      );
    },
    [client, postprocessFn, preprocessFn, traceServerFnName]
  );
  return traceServerRequest;
};

const useCall = (key: CallKey | null): Loadable<CallSchema | null> => {
  const getTsClient = useGetTraceServerClientContext();
  const loadingRef = useRef(false);
  const cachedCall = key ? callCache.get(key) : null;
  const [callRes, setCallRes] =
    useState<traceServerClient.TraceCallReadRes | null>(null);
  const deepKey = useDeepMemo(key);
  useEffect(() => {
    if (deepKey) {
      setCallRes(null);
      loadingRef.current = true;
      getTsClient()
        .callRead({
          project_id: projectIdFromParts(deepKey),
          id: deepKey.callId,
        })
        .then(res => {
          loadingRef.current = false;
          setCallRes(res);
        });
    }
  }, [deepKey, getTsClient]);

  return useMemo(() => {
    if (key == null) {
      return {
        loading: false,
        result: null,
      };
    }
    if (cachedCall != null) {
      return {
        loading: false,
        result: cachedCall,
      };
    }
    const result = callRes ? traceCallToUICallSchema(callRes.call) : null;
    if (callRes == null || loadingRef.current) {
      return {
        loading: true,
        result: null,
      };
    } else {
      if (result) {
        callCache.set(key, result);
      }
      return {
        loading: false,
        result,
      };
    }
  }, [cachedCall, callRes, key]);
};
const useCalls = (
  entity: string,
  project: string,
  filter: CallFilter,
  limit?: number,
  opts?: {skip?: boolean}
): Loadable<CallSchema[]> => {
  const getTsClient = useGetTraceServerClientContext();
  const loadingRef = useRef(false);
  const currentCancelRef = useRef<() => void>();
  const [callRes, setCallRes] =
    useState<traceServerClient.TraceCallsQueryRes | null>(null);
  const deepFilter = useDeepMemo(filter);
  useEffect(() => {
    if (opts?.skip) {
      return;
    }
    if (currentCancelRef.current) {
      currentCancelRef.current();
      currentCancelRef.current = undefined;
    }
    setCallRes(null);
    loadingRef.current = true;
    const req = {
      project_id: projectIdFromParts({entity, project}),
      filter: {
        op_version_refs: deepFilter.opVersionRefs,
        input_object_version_refs: deepFilter.inputObjectVersionRefs,
        output_object_version_refs: deepFilter.outputObjectVersionRefs,
        parent_ids: deepFilter.parentIds,
        trace_ids: deepFilter.traceId ? [deepFilter.traceId] : undefined,
        call_ids: deepFilter.callIds,
        trace_roots_only: deepFilter.traceRootsOnly,
        wb_run_ids: deepFilter.runIds,
        wb_user_ids: deepFilter.userIds,
      },
      limit,
    };
    const onSuccess = (res: traceServerClient.TraceCallsQueryRes) => {
      loadingRef.current = false;
      setCallRes(res);
    };
    const onError = (e: any) => {
      loadingRef.current = false;
      console.error(e);
      setCallRes({calls: []});
    };
    const {cancel} = traceServerClient.chunkedCallsQuery(
      getTsClient(),
      req,
      onSuccess,
      onError
    );
    currentCancelRef.current = cancel;
    return cancel;
  }, [entity, project, deepFilter, limit, opts?.skip, getTsClient]);

  return useMemo(() => {
    if (opts?.skip) {
      return {
        loading: false,
        result: [],
      };
    }
    const allResults = (callRes?.calls ?? []).map(traceCallToUICallSchema);
    const result = allResults.filter((row: any) => {
      return (
        deepFilter.opCategory == null ||
        (row.opVersionRef &&
          deepFilter.opCategory.includes(
            opVersionRefOpCategory(row.opVersionRef) as OpCategory
          ))
      );
    });

    if (callRes == null || loadingRef.current) {
      return {
        loading: true,
        result: [],
      };
    } else {
      allResults.forEach(call => {
        callCache.set(
          {
            entity,
            project,
            callId: call.callId,
          },
          call
        );
      });
      return {
        loading: false,
        result,
      };
    }
  }, [callRes, deepFilter.opCategory, entity, project, opts?.skip]);
};

const useOpVersion = (
  // Null value skips
  key: OpVersionKey | null
): Loadable<OpVersionSchema | null> => {
  const result = useOpVersions(
    key?.entity ?? '',
    key?.project ?? '',
    {
      opIds: [key?.opId ?? ''],
    },
    undefined,
    {
      skip: key == null,
    }
  );
  return {
    loading: result.loading,
    result: result.result?.find(
      obj => obj.versionHash === key?.versionHash
    ) as OpVersionSchema | null,
  };
};

const useOpVersions = makeTraceServerEndpointHook(
  'objsQuery',
  (
    entity: string,
    project: string,
    filter: OpVersionFilter,
    limit?: number,
    opts?: {skip?: boolean}
  ) => ({
    project_id: projectIdFromParts({entity, project}),
    // entity,
    // project,
    filter: {
      object_names: filter.opIds,
      latest_only: filter.latestOnly,
      is_op: true,
    },
  }),
  (res): OpVersionSchema[] =>
    res.objs.map(obj => {
      const [entity, project] = obj.project_id.split('/');
      return {
        entity,
        project,
        opId: obj.name,
        versionHash: obj.digest,
        typeName: obj.type,
        name: obj.name,
        path: 'obj',
        createdAtMs: convertISOToDate(obj.created_at).getTime(),
        category: null,
        versionIndex: obj.version_index,
        value: obj.val,
      };
    })
);

const useObjectVersion = (
  // Null value skips
  key: ObjectVersionKey | null
): Loadable<ObjectVersionSchema | null> => {
  const result = useRootObjectVersions(
    key?.entity ?? '',
    key?.project ?? '',
    {
      objectIds: [key?.objectId ?? ''],
    },
    undefined,
    {
      skip: key == null,
    }
  );
  return {
    loading: result.loading,
    result: {
      ...key,
      ...result.result?.find(obj => obj.versionHash === key?.versionHash),
    } as ObjectVersionSchema | null,
  };
};

const useRootObjectVersions = makeTraceServerEndpointHook(
  'objsQuery',
  (
    entity: string,
    project: string,
    filter: ObjectVersionFilter,
    limit?: number,
    opts?: {skip?: boolean}
  ) => ({
    project_id: projectIdFromParts({entity, project}),
    filter: {
      object_names: filter.objectIds,
      latest_only: filter.latestOnly,
      is_op: false,
    },
  }),
  (
    res,
    inputEntity,
    inputProject,
    filter,
    limit,
    opts
  ): ObjectVersionSchema[] =>
    res.objs
      .map(obj => {
        const [entity, project] = obj.project_id.split('/');
        return {
          scheme: 'weave',
          entity,
          project,
          objectId: obj.name,
          versionHash: obj.digest,
          typeName: obj.type,
          name: obj.name,
          path: 'obj',
          createdAtMs: convertISOToDate(obj.created_at).getTime(),
          category: null,
          versionIndex: obj.version_index,
          val: obj.val,
        };
      })
      .filter(obj => {
        const objCat = typeNameToCategory(obj.typeName);
        return (
          filter.category == null ||
          (objCat != null && filter.category.includes(objCat))
        );
      })
);

const useObjectOrOpVersions = makeTraceServerEndpointHook(
  'objsQuery',
  (
    entity: string,
    project: string,
    filter: ObjectVersionFilter,
    limit?: number,
    opts?: {skip?: boolean}
  ) => ({
    // entity,
    // project,
    project_id: projectIdFromParts({entity, project}),
    filter: {
      object_names: filter.objectIds,
      latest_only: filter.latestOnly,
    },
  }),
  (res): ObjectVersionSchema[] =>
    res.objs.map(obj => {
      const [entity, project] = obj.project_id.split('/');
      return {
        scheme: 'weave',
        entity,
        project,
        objectId: obj.name,
        versionHash: obj.digest,
        typeName: obj.type,
        name: obj.name,
        path: 'obj',
        createdAtMs: convertISOToDate(obj.created_at).getTime(),
        category: null,
        versionIndex: obj.version_index,
        val: obj.val,
      };
    })
);

const useChildCallsForCompare = (
  entity: string,
  project: string,
  parentCallIds: string[] | undefined,
  selectedOpVersionRef: string | null,
  selectedObjectVersionRef: string | null
): {
  loading: boolean;
  result: CallSchema[];
} => {
  // This should be moved to the trace server soon. Doing in memory join for
  // feature completeness now.
  const skipParent =
    parentCallIds == null ||
    parentCallIds.length === 0 ||
    selectedObjectVersionRef == null;

  const parentCalls = useCalls(
    entity,
    project,
    {
      callIds: parentCallIds,
      inputObjectVersionRefs: selectedObjectVersionRef
        ? [selectedObjectVersionRef]
        : [],
    },
    undefined,
    {skip: skipParent}
  );

  const subParentCallIds = useMemo(() => {
    return (parentCalls.result ?? []).map(call => call.callId);
  }, [parentCalls.result]);

  const skipChild =
    subParentCallIds.length === 0 || selectedOpVersionRef == null;

  const childCalls = useCalls(
    entity,
    project,
    {
      parentIds: subParentCallIds,
      opVersionRefs: selectedOpVersionRef ? [selectedOpVersionRef] : [],
    },
    undefined,
    {skip: skipChild}
  );

  const result = useMemo(() => {
    const loading = parentCalls.loading || childCalls.loading;
    if (loading) {
      return {loading, result: []};
    }
    if (skipChild || skipParent) {
      return {loading: false, result: []};
    }

    return {loading: false, result: childCalls.result ?? []};
  }, [
    childCalls.loading,
    childCalls.result,
    parentCalls.loading,
    skipChild,
    skipParent,
  ]);

  return result;
};

const applyExtra = (
  value: any,
  refExtraTuples: Array<{edgeType: string; edgeName: string}>
): any => {
  const tuple0 = refExtraTuples[0];
  if (refExtraTuples.length === 0) {
    return value;
  }
  if (tuple0.edgeType === 'atr' || tuple0.edgeType === 'key') {
    return applyExtra(value?.[tuple0.edgeName], refExtraTuples.slice(1));
  } else if (tuple0.edgeType === 'ndx') {
    return applyExtra(value?.[tuple0.edgeName], refExtraTuples.slice(1));
  } else {
    throw new Error('unhandled edge type ' + tuple0.edgeType);
  }
};

const useRefsData = (
  refUris: string[],
  tableQuery?: TableQuery
): Loadable<any[]> => {
  // Bad implementations! Fetches all versions of all objects in the refUris, and finds the specific
  // versions on the client-side. Also doesn't yet do ref-walking
  const parsed = useMemo(() => refUris.map(refStringToRefDict), [refUris]);
  const ref0 = parsed[0];
  const artifactNames = parsed.map(p => p.artifactName);
  const objVersionsResult = useObjectOrOpVersions(ref0.entity, ref0.project, {
    objectIds: artifactNames,
  });
  const result = useMemo(() => {
    if (!objVersionsResult.loading) {
      return {
        loading: false,
        result: parsed.map(p => {
          const rootValue = objVersionsResult.result?.find(
            o =>
              o.versionHash === p.versionCommitHash &&
              o.objectId === p.artifactName
          )?.val;
          return applyExtra(rootValue, p.refExtraTuples);
        }),
        error: null,
      };
    } else {
      return {
        loading: true,
        result: null,
        error: null,
      };
    }
  }, [objVersionsResult.loading, objVersionsResult.result, parsed]);
  return result;
};

const useApplyMutationsToRef = (): ((
  refUri: string,
  edits: RefMutation[]
) => Promise<string>) => {
  throw new Error('Not implemented');
};

const useGetRefsType = (): ((refUris: string[]) => Promise<Types.Type[]>) => {
  // NOT DRY!
  const objectOrOpVersions = useMakeTraceServerEndpoint(
    'objsQuery',
    (
      entity: string,
      project: string,
      filter: ObjectVersionFilter,
      limit?: number,
      opts?: {skip?: boolean}
    ) => ({
      // entity,
      // project,
      project_id: projectIdFromParts({entity, project}),
      filter: {
        object_names: filter.objectIds,
        latest_only: filter.latestOnly,
      },
    }),
    (res): ObjectVersionSchema[] =>
      res.objs.map(obj => {
        const [entity, project] = obj.project_id.split('/');
        return {
          scheme: 'weave',
          entity,
          project,
          objectId: obj.name,
          versionHash: obj.digest,
          typeName: obj.type,
          name: obj.name,
          path: 'obj',
          createdAtMs: convertISOToDate(obj.created_at).getTime(),
          category: null,
          versionIndex: obj.version_index,
          val: obj.val,
        };
      })
  );
  return async (refUris: string[]) => {
    if (refUris.length === 0) {
      return [];
    }
    // Bad implementations! Fetches all versions of all objects in the refUris, and finds the specific
    // versions on the client-side. Also doesn't yet do ref-walking
    const parsed = refUris.map(refStringToRefDict);
    const ref0 = parsed[0];
    const artifactNames = parsed.map(p => p.artifactName);
    const objVersionsResult = await objectOrOpVersions(
      ref0.entity,
      ref0.project,
      {
        objectIds: artifactNames,
      }
    );
    const result = parsed.map(p => {
      const rootValue = objVersionsResult.find(
        o =>
          o.versionHash === p.versionCommitHash && o.objectId === p.artifactName
      )?.val;
      return applyExtra(rootValue, p.refExtraTuples);
    });
    return result.map(weaveTypeOf);
  };
};

const mergeTypes = (a: Types.Type, b: Types.Type): Types.Type => {
  // TODO: this should match the python merge_types implementation.
  if (_.isEqual(a, b)) {
    return a;
  }
  if (isSimpleTypeShape(a) && isSimpleTypeShape(b)) {
    if (a === b) {
      return a;
    } else {
      return union([a, b]);
    }
  }
  if (!isSimpleTypeShape(a) && !isSimpleTypeShape(b)) {
    if (a.type === 'typedDict' && b.type === 'typedDict') {
      const allKeysDict = Object.assign({}, a.propertyTypes, b.propertyTypes);
      const nextPropTypes = _.mapValues(allKeysDict, (value, key) => {
        const selfPropType = a.propertyTypes[key] ?? 'none';
        const otherPropType = b.propertyTypes[key] ?? 'none';
        return mergeTypes(selfPropType, otherPropType);
      });
      return {
        type: 'typedDict',
        propertyTypes: nextPropTypes,
      };
    } else if (a.type === 'list' && b.type === 'list') {
      return {
        type: 'list',
        objectType: mergeTypes(a.objectType, b.objectType),
      };
    } else {
      console.warn('unhandled type merge ' + a.type + ' ' + b.type);
    }
  }
  return union([a, b]);
};

const mergeAllTypes = (types: Types.Type[]): Types.Type => {
  return types.reduce(mergeTypes);
};

const weaveTypeOf = (o: any): Types.Type => {
  if (o == null) {
    return 'none';
  } else if (_.isArray(o)) {
    return {
      type: 'list',
      objectType:
        o.length === 0 ? 'unknown' : mergeAllTypes(o.map(weaveTypeOf)),
    };
  } else if (_.isObject(o)) {
    if ('_type' in o) {
      return {
        type: o._type,
        _base_type: {type: 'Object'},
        _is_object: true,
        ..._.mapValues(_.omit(o, ['_type']), weaveTypeOf),
      } as any;
    } else {
      return {
        type: 'typedDict',
        propertyTypes: _.mapValues(o, weaveTypeOf),
      } as any;
    }
  } else if (_.isString(o)) {
    if (o.startsWith(WANDB_ARTIFACT_REF_PREFIX)) {
      return {
        type: 'WandbArtifactRef',
      };
    } else if (o.startsWith(WEAVE_REF_PREFIX)) {
      return {type: 'Ref'};
    }
    return 'string';
  } else if (_.isNumber(o)) {
    return 'number'; // TODO
  } else if (_.isBoolean(o)) {
    return 'boolean';
  }
  throw new Error('Type conversion not implemeneted for value: ' + o);
};

const useRefsType = (refUris: string[]): Loadable<Types.Type[]> => {
  const dataResult = useRefsData(refUris);
  const finalRes = useMemo(() => {
    if (!dataResult.loading) {
      return {
        loading: false,
        result: dataResult.result?.map(weaveTypeOf) ?? [],
        error: null,
      };
    } else {
      return {
        loading: true,
        result: null,
        error: null,
      };
    }
  }, [dataResult.loading, dataResult.result]);
  return finalRes;
};

/// Converters ///

const traceCallToLegacySpan = (
  traceCall: traceServerClient.TraceCallSchema
): RawSpanFromStreamTableEra => {
  const startDate = convertISOToDate(traceCall.start_datetime);
  const endDate = traceCall.end_datetime
    ? convertISOToDate(traceCall.end_datetime)
    : null;
  let statusCode = 'UNSET';
  if (traceCall.exception) {
    statusCode = 'ERROR';
  } else if (traceCall.end_datetime) {
    statusCode = 'SUCCESS';
  }
  let latencyS = 0;
  if (startDate && endDate) {
    latencyS = (endDate.getTime() - startDate.getTime()) / 1000;
  }
  const summary = {
    latency_s: latencyS,
    ...(traceCall.summary ?? {}),
  };
  return {
    name: traceCall.name,
    inputs: traceCall.inputs,
    output: traceCall.outputs,
    status_code: statusCode,
    exception: traceCall.exception,
    attributes: traceCall.attributes,
    summary,
    span_id: traceCall.id,
    trace_id: traceCall.trace_id,
    parent_id: traceCall.parent_id,
    timestamp: startDate.getTime(),
    start_time_ms: startDate.getTime(),
    end_time_ms: endDate?.getTime(),
  };
};

const projectIdToParts = (projectId: string) => {
  const [entity, project] = projectId.split('/');
  return {entity, project};
};

const traceCallToUICallSchema = (
  traceCall: traceServerClient.TraceCallSchema
): CallSchema => {
  const {entity, project} = projectIdToParts(traceCall.project_id);
  return {
    entity,
    project,
    callId: traceCall.id,
    traceId: traceCall.trace_id,
    parentId: traceCall.parent_id ?? null,
    spanName:
      traceCall.name.startsWith(WANDB_ARTIFACT_REF_PREFIX) ||
      traceCall.name.startsWith(WEAVE_REF_PREFIX)
        ? refUriToOpVersionKey(traceCall.name).opId
        : traceCall.name,
    opVersionRef:
      traceCall.name.startsWith(WANDB_ARTIFACT_REF_PREFIX) ||
      traceCall.name.startsWith(WEAVE_REF_PREFIX)
        ? traceCall.name
        : null,
    rawSpan: traceCallToLegacySpan(traceCall),
    rawFeedback: {},
    userId: traceCall.wb_user_id ?? null,
    runId: traceCall.wb_run_id ?? null,
  };
};

/// Utility Functions ///

const convertISOToDate = (iso: string) => {
  return new Date(iso);
};

// Export //

export const tsWFDataModelHooks: WFDataModelHooksInterface = {
  useCall,
  useCalls,
  useOpVersion,
  useOpVersions,
  useObjectVersion,
  useRootObjectVersions,
  useRefsData,
  useApplyMutationsToRef,
  derived: {
    useChildCallsForCompare,
    useGetRefsType,
    useRefsType,
  },
};
