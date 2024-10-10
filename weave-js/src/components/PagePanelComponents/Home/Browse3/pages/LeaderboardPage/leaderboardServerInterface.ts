import {isWeaveObjectRef} from '@wandb/weave/react';
import _ from 'lodash';

import {flattenObjectPreservingWeaveTypes} from '../../../Browse2/browse2Util';
import {parseRefMaybe} from '../../../Browse2/SmallRef';
import {EVALUATE_OP_NAME_POST_PYDANTIC} from '../common/heuristics';
import {TraceServerClient} from '../wfReactInterface/traceServerClient';
import {TraceObjSchema} from '../wfReactInterface/traceServerClientTypes';
import {
  convertISOToDate,
  projectIdFromParts,
} from '../wfReactInterface/tsDataModelHooks';
import {opVersionKeyToRefUri} from '../wfReactInterface/utilities';

type LeaderboardValueRecord = {
  datasetName: string;
  datasetVersion: string;
  metricType:
    | 'scorerMetric'
    | 'modelLatency'
    | 'modelCost'
    | 'modelTokens'
    | 'modelErrors';
  scorerName: string; // modelMetrics repeat the type here
  scorerVersion: string; // modelMetrics repeat the type here
  metricPath: string; // modelMetrics repeat the type here
  metricValue: number | string | boolean | null;
  modelName: string;
  modelVersion: string;
  modelType: 'object' | 'op';
  trials: number;
  createdAt: Date;
  sourceEvaluationCallId: string;
  sourceEvaluationObjectRef: string;
};

type GroupableLeaderboardValueRecord = {
  datasetGroup: string;
  scorerGroup: string;
  metricPathGroup: string;
  modelGroup: string;
  sortKey: number;
  row: LeaderboardValueRecord;
};

export type GroupedLeaderboardData2 = GroupableLeaderboardValueRecord[];
export type LeaderboardData2 = LeaderboardValueRecord[];

export type FilterAndGroupSpec = {
  datasets?: Array<{
    name: string; // "*" means all
    version: string; // "*" means all
    splitByVersion?: boolean;
    scorers?: Array<{
      name: string; // "*" means all
      version: string; // "*" means all
      splitByVersion?: boolean;
      metrics?: Array<{
        path: string; // "*" means all
        shouldMinimize?: boolean;
      }>; // null is all
    }>; // null is all
  }>; // null is all
  models?: Array<{
    name: string; // "*" means all
    version: string; // "*" means all
    splitByVersion?: boolean;
  }>; // null is all
};

export const getLeaderboardData = async (
  client: TraceServerClient,
  entity: string,
  project: string,
  spec: FilterAndGroupSpec = {}
): Promise<GroupedLeaderboardData2> => {
  // get all the evaluations
  const allEvaluationObjectsProm = client.objsQuery({
    project_id: projectIdFromParts({entity, project}),
    filter: {
      base_object_classes: ['Evaluation'],
      is_op: false,
    },
  });
  const allEvaluationCallsProm = client.callsStreamQuery({
    project_id: projectIdFromParts({entity, project}),
    filter: {
      op_names: [
        opVersionKeyToRefUri({
          entity,
          project,
          opId: EVALUATE_OP_NAME_POST_PYDANTIC,
          versionHash: '*',
        }),
      ],
    },
  });

  const allEvaluationObjectsRes = await allEvaluationObjectsProm;
  const evaluationObjectDigestMap = new Map<
    string,
    {versions: Map<string, TraceObjSchema>; versionOrder: string[]}
  >();
  allEvaluationObjectsRes.objs.forEach(obj => {
    const outerKey = obj.object_id;
    const innerKey = obj.digest;
    if (!evaluationObjectDigestMap.has(outerKey)) {
      evaluationObjectDigestMap.set(outerKey, {
        versions: new Map(),
        versionOrder: [],
      });
    }
    evaluationObjectDigestMap.get(outerKey)!.versions.set(innerKey, obj);
  });
  evaluationObjectDigestMap.forEach((value, key) => {
    value.versionOrder = Array.from(value.versions.entries())
      .sort((a, b) => a[1].version_index - b[1].version_index)
      .map(entry => entry[0]);
  });

  const allEvaluationCallsRes = await allEvaluationCallsProm;
  const data: LeaderboardData2 = [];
  allEvaluationCallsRes.calls.forEach(call => {
    const evalObjectRefUri = call.inputs.self;
    const evalObjectRef = parseRefMaybe(evalObjectRefUri ?? '');
    const modelObjectOrOpRef = parseRefMaybe(call.inputs.model ?? '');

    if (!evalObjectRef || !modelObjectOrOpRef) {
      console.warn(
        'Skipping evaluation call with missing eval object ref',
        call
      );
      return;
    }

    const evalObjectName = evalObjectRef.artifactName;
    const evalObjectVersion = evalObjectRef.artifactVersion;
    const evalObject = evaluationObjectDigestMap
      .get(evalObjectName)
      ?.versions.get(evalObjectVersion);
    if (!evalObject) {
      console.warn('Skipping evaluation call with missing eval object', call);
      return;
    }

    const datasetRef = parseRefMaybe(evalObject.val.dataset ?? '');
    if (!datasetRef) {
      console.warn('Skipping evaluation call with missing dataset ref', call);
      return;
    }
    const datasetName = datasetRef.artifactName;
    const datasetVersion = datasetRef.artifactVersion;

    const modelName = modelObjectOrOpRef.artifactName;
    const modelVersion = modelObjectOrOpRef.artifactVersion;
    if (!isWeaveObjectRef(modelObjectOrOpRef)) {
      console.warn('Skipping evaluation call with invalid model ref', call);
      return;
    }
    const modelType = modelObjectOrOpRef.weaveKind === 'op' ? 'op' : 'object';
    const trials = evalObject.val.trials ?? call.inputs.trials ?? 1;

    const recordPartial: Omit<
      LeaderboardValueRecord,
      | 'metricType'
      | 'scorerName'
      | 'scorerVersion'
      | 'metricPath'
      | 'metricValue'
    > = {
      datasetName,
      datasetVersion,
      modelName,
      modelVersion,
      modelType,
      trials,
      createdAt: convertISOToDate(call.started_at),
      sourceEvaluationCallId: call.id,
      sourceEvaluationObjectRef: evalObjectRefUri,
    };

    const modelLatency = (call.output as any)?.model_latency?.mean;
    if (modelLatency == null) {
      console.warn('Skipping model latency', call);
    } else {
      const modelLatencyRecord: LeaderboardValueRecord = {
        ...recordPartial,
        metricType: 'modelLatency',
        scorerName: 'modelLatency',
        scorerVersion: 'modelLatency',
        metricPath: 'model_latency.mean',
        metricValue: modelLatency,
      };
      data.push(modelLatencyRecord);
    }

    // TODO: add modelCost, modelTokens, modelErrors

    const scorerRefUris = (evalObject.val.scorers ?? []) as string[];
    scorerRefUris.forEach(scorerRefUri => {
      const scorerRef = parseRefMaybe(scorerRefUri);
      if (!scorerRef || !isWeaveObjectRef(scorerRef)) {
        console.warn('Skipping scorer ref', scorerRefUri);
        return;
      }
      const scorerName = scorerRef.artifactName;
      const scorerVersion = scorerRef.artifactVersion;
      // const scorerType = scorerRef.weaveKind === 'op' ? 'op' : 'object';
      const scorePayload = (call.output as any)?.[scorerName];
      if (typeof scorePayload !== 'object' || scorePayload == null) {
        console.warn(
          'Skipping scorer call with invalid score payload',
          scorerName,
          scorerVersion,
          call
        );
        return;
      }
      const flatScorePayload = flattenObjectPreservingWeaveTypes(scorePayload);
      Object.entries(flatScorePayload).forEach(([metricPath, metricValue]) => {
        const scoreRecord: LeaderboardValueRecord = {
          ...recordPartial,
          metricType: 'scorerMetric',
          scorerName,
          scorerVersion,
          metricPath,
          metricValue,
        };
        data.push(scoreRecord);
      });
    });
  });

  const filterableGroupableData = data.map(row => {
    const groupableRow: GroupableLeaderboardValueRecord = {
      datasetGroup: row.datasetName,
      scorerGroup: row.scorerName,
      modelGroup: row.modelName,
      metricPathGroup: row.metricPath,
      sortKey: -row.createdAt.getTime(),
      row,
    };

    if (!spec.datasets) {
      return {include: true, groupableRow};
    }
    if (spec.datasets.length === 0) {
      return {include: true, groupableRow};
    }
    if (spec.datasets.some(dataset => dataset.name === '*')) {
      return {include: true, groupableRow};
    }

    let datasetSpec = spec.datasets.find(
      dataset =>
        dataset.name === row.datasetName &&
        dataset.version === row.datasetVersion
    );
    datasetSpec =
      datasetSpec ||
      spec.datasets.find(
        dataset =>
          dataset.name === row.datasetName &&
          (dataset.version === '*' || dataset.version === row.datasetVersion)
      );
    datasetSpec =
      datasetSpec ||
      spec.datasets.find(
        dataset =>
          (dataset.name === '*' || dataset.name === row.datasetName) &&
          (dataset.version === '*' || dataset.version === row.datasetVersion)
      );
    if (!datasetSpec) {
      return {include: false, groupableRow};
    }
    if (datasetSpec.splitByVersion) {
      groupableRow.datasetGroup += `${row.datasetName}:${row.datasetVersion}`;
    }
    if (datasetSpec.scorers) {
      let scorerSpec = datasetSpec.scorers.find(
        scorer =>
          scorer.name === row.scorerName && scorer.version === row.scorerVersion
      );
      scorerSpec =
        scorerSpec ||
        datasetSpec.scorers.find(
          scorer =>
            scorer.name === row.scorerName &&
            (scorer.version === '*' || scorer.version === row.scorerVersion)
        );
      scorerSpec =
        scorerSpec ||
        datasetSpec.scorers.find(
          scorer =>
            (scorer.name === '*' || scorer.name === row.scorerName) &&
            (scorer.version === '*' || scorer.version === row.scorerVersion)
        );
      if (!scorerSpec) {
        return {include: false, groupableRow};
      }
      if (scorerSpec.splitByVersion) {
        groupableRow.scorerGroup += `${row.scorerName}:${row.scorerVersion}`;
      }
      if (scorerSpec.metrics) {
        const metricSpec = scorerSpec.metrics.find(
          metric => metric.path === '*' || metric.path === row.metricPath
        );
        if (!metricSpec) {
          return {include: false, groupableRow};
        }
      }
    }
    if (spec.models) {
      let modelSpec = spec.models.find(
        model =>
          model.name === row.modelName && model.version === row.modelVersion
      );
      modelSpec =
        modelSpec ||
        spec.models.find(
          model =>
            model.name === row.modelName &&
            (model.version === '*' || model.version === row.modelVersion)
        );
      modelSpec =
        modelSpec ||
        spec.models.find(
          model =>
            (model.name === '*' || model.name === row.modelName) &&
            (model.version === '*' || model.version === row.modelVersion)
        );
      if (!modelSpec) {
        return {include: false, groupableRow};
      }
      if (modelSpec.splitByVersion) {
        groupableRow.modelGroup += `${row.modelName}:${row.modelVersion}`;
      }
    }
    return {include: true, groupableRow};
  });

  const groupableData = filterableGroupableData
    .filter(entry => entry.include)
    .map(entry => entry.groupableRow);

  const finalData: GroupedLeaderboardData2 = [];
  const groupedVisitor = (
    recordList: GroupableLeaderboardValueRecord[],
    fields: string[]
  ): any => {
    if (fields.length === 0) {
      // Sort by created at descending and return the most recent record
      // Would be better to use some form of latest.
      const res = recordList.sort((a, b) => a.sortKey - b.sortKey)[0];
      finalData.push(res);
    }

    const [currentField, ...remainingFields] = fields;
    return _.values(_.groupBy(recordList, currentField)).forEach(groupedRecords =>
      groupedVisitor(groupedRecords, remainingFields)
    );
  };

  groupedVisitor(groupableData, [
    'datasetGroup',
    'scorerGroup',
    'metricPathGroup',
    'modelGroup',
  ]);

  return finalData;
};
