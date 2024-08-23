import {Divider} from '@mui/material';
import Box from '@mui/material/Box';
import {Pill} from '@wandb/weave/components/Tag';
import {formatNumber} from '@wandb/weave/core/util/number';
import {
  FORMAT_NUMBER_NO_DECIMALS,
  formatTokenCost,
  formatTokenCount,
  getLLMTokenCost,
  getLLMTotalTokenCost,
} from '@wandb/weave/util/llmTokenCosts';
import React, {ReactNode} from 'react';

import {MOON_600} from '../../../../../../common/css/color.styles';
import {IconName} from '../../../../../Icon';
import {Tooltip} from '../../../../../Tooltip';
import {LLMUsageSchema} from '../wfReactInterface/traceServerClientTypes';

type UsageDataKeys = keyof LLMUsageSchema;
const isUsageDataKey = (key: any): key is UsageDataKeys => {
  if (typeof key !== 'string') {
    return false;
  }
  const usageDataKeys: UsageDataKeys[] = [
    'requests',
    'prompt_tokens',
    'completion_tokens',
    'total_tokens',
    'input_tokens',
    'output_tokens',
  ];
  return usageDataKeys.includes(key as UsageDataKeys);
};

export const TraceUsageStats = ({
  usage,
  latency_s,
}: {
  usage: {[key: string]: LLMUsageSchema};
  latency_s: number;
}) => {
  const {cost, tokens, costToolTip, tokenToolTip} =
    getTokensAndCostFromUsage(usage);

  const latency =
    (latency_s < 0.01 ? '<0.01' : formatNumber(latency_s, 'Number')) + 's';

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
      }}>
      <TraceStat icon="recent-clock" label={latency} />
      {usage && (
        <>
          {/* Tokens */}
          <TraceStat
            icon="database-artifacts"
            label={tokens}
            tooltip={tokenToolTip}
          />
          {/* Cost */}
          <TraceStat label={cost} tooltip={costToolTip} />
        </>
      )}
    </Box>
  );
};

export const getUsageFromCellParams = (params: {[key: string]: any}) => {
  const usage: {[key: string]: LLMUsageSchema} = {};
  for (const key in params) {
    if (key.startsWith('summary.usage')) {
      const usageKeys = key.replace('summary.usage.', '').split('.');
      const usageKey = usageKeys.pop() || '';
      if (isUsageDataKey(usageKey)) {
        const model = usageKeys.join('.');
        if (!usage[model]) {
          usage[model] = {
            requests: 0,
            prompt_tokens: 0,
            completion_tokens: 0,
            total_tokens: 0,
          };
        }
        usage[model][usageKey] = params[key];
      }
    }
  }
  return usage;
};

// This needs to updated eventually, to either include more possible keys or to be more dynamic
// accounts for openai and anthropic usage objects (prompt_tokens, input_tokens)
export const getUsageInputTokens = (usage: LLMUsageSchema) => {
  return usage.input_tokens ?? usage.prompt_tokens ?? 0;
};

export const getUsageOutputTokens = (usage: LLMUsageSchema) => {
  return usage.output_tokens ?? usage.completion_tokens ?? 0;
};

export type TokenCostMetrics = {
  inputs: {
    cost: Record<string, number>;
    tokens: Record<string, number>;
  };
  outputs: {
    cost: Record<string, number>;
    tokens: Record<string, number>;
  };
};

const tooltipRowStyles = {
  display: 'flex',
  justifyContent: 'space-between',
  alignContent: 'center',
  gap: '16px',
};

const tooltipDivider = (
  <Divider
    sx={{
      borderColor: MOON_600,
      marginTop: '8px',
      marginBottom: '7px',
    }}
  />
);

export const TokenToolTip = (metrics: TokenCostMetrics) => (
  <Box>
    {Object.keys(metrics.inputs.tokens).map(model => (
      <Box key={model + 'input'} sx={tooltipRowStyles}>
        <span>{model === 'total' ? 'Input tokens' : model}: </span>
        <span>
          {FORMAT_NUMBER_NO_DECIMALS.format(metrics.inputs.tokens[model])}
        </span>
      </Box>
    ))}
    {tooltipDivider}
    {Object.keys(metrics.outputs.tokens).map(model => (
      <Box key={model + 'output'} sx={tooltipRowStyles}>
        <span>{model === 'total' ? 'Output tokens' : model}: </span>
        <span>
          {FORMAT_NUMBER_NO_DECIMALS.format(metrics.outputs.tokens[model])}
        </span>
      </Box>
    ))}
  </Box>
);

export const CostToolTip = (metrics: TokenCostMetrics) => (
  <Box>
    <span style={{fontWeight: 600}}>Estimated Cost</span>
    {Object.keys(metrics.inputs.cost).map(model => (
      <Box key={model + 'input'} sx={tooltipRowStyles}>
        <span>{model === 'total' ? 'Input cost' : model}: </span>
        <span>{formatTokenCost(metrics.inputs.cost[model])}</span>
      </Box>
    ))}
    {tooltipDivider}
    {Object.keys(metrics.outputs.cost).map(model => (
      <Box key={model + 'output'} sx={tooltipRowStyles}>
        <span>{model === 'total' ? 'Output cost' : model}: </span>
        <span>{formatTokenCost(metrics.outputs.cost[model])}</span>
      </Box>
    ))}
  </Box>
);

export const getTokensAndCostFromUsage = (usage: {
  [key: string]: LLMUsageSchema;
}) => {
  const metrics: TokenCostMetrics = {
    inputs: {
      cost: {
        total: 0,
      },
      tokens: {total: 0},
    },
    outputs: {
      cost: {total: 0},
      tokens: {total: 0},
    },
  };
  if (usage) {
    for (const model of Object.keys(usage)) {
      const inputTokens = getUsageInputTokens(usage[model]);
      const outputTokens = getUsageOutputTokens(usage[model]);
      const inputCost = getLLMTokenCost(model, 'input', inputTokens);
      const outputCost = getLLMTokenCost(model, 'output', outputTokens);

      metrics.inputs.cost[model] = inputCost;
      metrics.inputs.tokens[model] = inputTokens;
      metrics.outputs.cost[model] = outputCost;
      metrics.outputs.tokens[model] = outputTokens;

      metrics.inputs.cost.total += inputCost;
      metrics.inputs.tokens.total += inputTokens;
      metrics.outputs.cost.total += outputCost;
      metrics.outputs.tokens.total += outputTokens;
    }
  }
  const costNum = metrics.inputs.cost.total + metrics.outputs.cost.total;
  const cost = formatTokenCost(costNum);
  const tokensNum = metrics.inputs.tokens.total + metrics.outputs.tokens.total;
  const tokens = formatTokenCount(tokensNum);

  const costToolTip = <CostToolTip {...metrics} />;
  const tokenToolTip = <TokenToolTip {...metrics} />;

  return {costNum, cost, tokensNum, tokens, costToolTip, tokenToolTip};
};

export const TraceStat = ({
  icon,
  label,
  tooltip,
}: {
  icon?: IconName;
  label: string;
  tooltip?: ReactNode;
}) => {
  const trigger = (
    <div>
      <Pill
        icon={icon}
        label={label}
        color="moon"
        className="bg-transparent text-moon-500 dark:bg-transparent dark:text-moon-500"
      />
    </div>
  );

  if (!tooltip) {
    return trigger;
  }

  return <Tooltip trigger={trigger} content={tooltip} />;
};

export const sumUsageData = (usage: {[key: string]: LLMUsageSchema}) => {
  const usageData = Object.entries(usage ?? {}).map(([k, v]) => {
    const promptTokens = v.input_tokens ?? v.prompt_tokens ?? 0;
    const completionTokens = v.output_tokens ?? v.completion_tokens ?? 0;
    return {
      id: k,
      ...v,
      prompt_tokens: promptTokens,
      completion_tokens: completionTokens,
      total_tokens: v.total_tokens || promptTokens + completionTokens,
      cost: getLLMTotalTokenCost(k, promptTokens, completionTokens),
    };
  });

  // if more than one model is used, add a row for the total usage
  if (usageData.length > 1) {
    const totalUsage = usageData.reduce(
      (acc, curr) => {
        const promptTokens = curr.input_tokens ?? curr.prompt_tokens;
        const completionTokens = curr.output_tokens ?? curr.completion_tokens;
        acc.requests += curr.requests ?? 0;
        acc.prompt_tokens += promptTokens;
        acc.completion_tokens += completionTokens;
        acc.total_tokens +=
          curr.total_tokens || promptTokens + completionTokens;
        acc.cost += curr.cost;
        return acc;
      },
      {
        requests: 0,
        prompt_tokens: 0,
        completion_tokens: 0,
        total_tokens: 0,
        cost: 0,
      }
    );

    usageData.push({
      id: 'Total',
      ...totalUsage,
    });
  }

  return usageData;
};
