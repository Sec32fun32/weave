import {useMemo} from 'react';

import {flattenObjectPreservingWeaveTypes} from '../../../Browse2/browse2Util';
import {parseRefMaybe} from '../../../Browse2/SmallRef';
import {EVALUATE_OP_NAME_POST_PYDANTIC} from '../common/heuristics';
import {useWFHooks} from '../wfReactInterface/context';
import {
  objectVersionKeyToRefUri,
  opVersionKeyToRefUri,
} from '../wfReactInterface/utilities';
import { useEvalCallsForConfig } from './leaderboardConfigQuery';
import {LeaderboardConfigType} from './LeaderboardConfigType';

export type LeaderboardData = {
  metrics: {
    [metricId: string]: {
      evaluationName: string;
      metricPath: string;
    };
  };
  models: string[];
  scores: {
    [modelId: string]: {
      [metricId: string]: {value: number; sourceCallId: string};
    };
  };
};

export const useLeaderboardData = (
  entity: string,
  project: string,
  config: LeaderboardConfigType
): {loading: boolean; data: LeaderboardData} => {
  // console.log('Fetching leaderboard data', config);
  // const {useRootObjectVersions, useCalls} = useWFHooks();

  // // Get the last 100 (latest) evaluation versions
  // const evaluationVersions = useRootObjectVersions(
  //   entity,
  //   project,
  //   {
  //     baseObjectClasses: ['Evaluation'],
  //     // latestOnly: true,
  //   },
  //   100,
  //   true
  // );

  // // Unfortunately, the eval framework does not build models automatically!!
  // // const modelVersions = useRootObjectVersions(entity, project, {
  // //     baseObjectClasses: ['Model'],
  // //     latestOnly: true,
  // // }, 100, true)

  // // Get the runs for these evaluation versions.
  // const evaluationVersionsResult = evaluationVersions?.result;
  // const evaluationRuns = useCalls(
  //   entity,
  //   project,
  //   {
  //     opVersionRefs: [
  //       opVersionKeyToRefUri({
  //         entity,
  //         project,
  //         opId: EVALUATE_OP_NAME_POST_PYDANTIC,
  //         versionHash: '*',
  //       }),
  //     ],
  //     traceRootsOnly: true,
  //     inputObjectVersionRefs: (evaluationVersionsResult ?? []).map(version =>
  //       objectVersionKeyToRefUri(version)
  //     ),
  //   },
  //   100,
  //   undefined,
  //   undefined,
  //   undefined,
  //   undefined,
  //   undefined,
  //   {skip: !evaluationVersionsResult}
  // );
  const evaluationRuns = useEvalCallsForConfig(entity, project, config);

  // Build the dataset

  const results: {loading: boolean; data: LeaderboardData} = useMemo(() => {
    const finalData: LeaderboardData = {
      metrics: {},
      models: [],
      scores: {},
    };
    if (evaluationRuns.loading) {
      return {
        loading: true,
        data: finalData,
      };
    } else if (!evaluationRuns.result) {
      // || !evaluationVersionsResult) {
      return {
        loading: false,
        data: finalData,
      };
    }

    const runs = evaluationRuns.result;
    // const versions = evaluationVersionsResult
    runs.forEach(r => {
      const modelName = r.traceCall?.inputs.model;
      if (!modelName) {
        return;
      }
      const evaluationVersion = r.traceCall?.inputs.self;
      if (!evaluationVersion) {
        return;
      }
      const evalName = parseRefMaybe(evaluationVersion)?.artifactName;
      if (!evalName) {
        return;
      }
      const outputSummary = r.traceCall?.output;
      if (!outputSummary) {
        return;
      }
      if (!finalData.models.includes(modelName)) {
        finalData.models.push(modelName);
      }
      const modelScores = flattenObjectPreservingWeaveTypes(
        outputSummary ?? {}
      );
      Object.entries(modelScores).forEach(([metric, score]) => {
        const metricName = `${evalName}.${metric}`;
        if (!finalData.metrics[metricName]) {
          finalData.metrics[metricName] = {
            evaluationName: evalName,
            metricPath: metric,
          };
        }
        if (!finalData.scores[modelName]) {
          finalData.scores[modelName] = {};
        }
        finalData.scores[modelName][metricName] = {
          value: score,
          sourceCallId: r.callId,
        };
      });
    });

    return {
      loading: false,
      data: finalData,
    };
  }, [evaluationRuns.loading, evaluationRuns.result]);

  return results;
};