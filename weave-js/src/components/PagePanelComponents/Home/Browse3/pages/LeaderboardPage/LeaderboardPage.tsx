import {Alert, Box, Typography} from '@mui/material';
import {Button} from '@wandb/weave/components/Button';
import React, {useCallback, useState} from 'react';
import {useHistory} from 'react-router-dom';

import {useWeaveflowRouteContext} from '../../context';
import {EditableMarkdown} from './EditableMarkdown';
import {LeaderboardConfigEditor} from './LeaderboardConfigEditor';
import {LeaderboardGrid} from './LeaderboardGrid';
import {useLeaderboardData} from './query/hookAdapters';
import {LeaderboardValueRecord} from './query/leaderboardQuery';
import {LeaderboardConfigType} from './types/leaderboardConfigType';

const USE_COMPARE_EVALUATIONS_PAGE = false;

type LeaderboardPageProps = {
  entity: string;
  project: string;
};

export const LeaderboardPage: React.FC<LeaderboardPageProps> = props => {
  return (
    <LeaderboardPageContent entity={props.entity} project={props.project} />
  );
};

const DEFAULT_DESCRIPTION = `# Leaderboard`;

const usePersistedLeaderboardConfig = () => {
  const [configPersisted, setConfigPersisted] = useState<LeaderboardConfigType>(
    {
      version: 1,
      config: {description: '', dataSelectionSpec: {}},
    }
  );

  const [config, setConfigLocal] =
    useState<LeaderboardConfigType>(configPersisted);

  const persistConfig = useCallback(() => {
    setConfigPersisted(config);
    // persistLeaderboardConfig(config);
  }, [config]);

  const cancelChanges = useCallback(() => {
    setConfigLocal(configPersisted);
  }, [configPersisted]);

  return {config, setConfigLocal, persistConfig, cancelChanges};
};

export const LeaderboardPageContent: React.FC<LeaderboardPageProps> = props => {
  const {entity, project} = props;

  const {peekingRouter} = useWeaveflowRouteContext();
  const history = useHistory();

  const [showConfig, setShowConfig] = useState(false);

  const {
    config: currentConfig,
    setConfigLocal,
    persistConfig,
    cancelChanges,
  } = usePersistedLeaderboardConfig();
  const description = currentConfig.config.description;
  const setDescription = useCallback(
    (newDescription: string) => {
      setConfigLocal(newConfig => ({
        ...newConfig,
        config: {...newConfig.config, description: newDescription},
      }));
      persistConfig();
    },
    [setConfigLocal, persistConfig]
  );

  const {loading, data} = useLeaderboardData(
    entity,
    project,
    currentConfig.config.dataSelectionSpec
  );

  const handleCellClick = (record: LeaderboardValueRecord) => {
    const sourceCallId = record.sourceEvaluationCallId;
    if (sourceCallId) {
      let to: string;
      if (USE_COMPARE_EVALUATIONS_PAGE) {
        to = peekingRouter.compareEvaluationsUri(entity, project, [
          sourceCallId,
        ]);
      } else {
        to = peekingRouter.callUIUrl(entity, project, '', sourceCallId, null);
      }
      history.push(to);
    }
  };

  const [showingAlert, setShowingAlert] = useState(true);

  return (
    <Box display="flex" flexDirection="row" height="100%" flexGrow={1}>
      <Box
        flex={1}
        display="flex"
        flexDirection="column"
        height="100%"
        minWidth="65%">
        <div
          style={{
            position: 'absolute',
            display: showConfig ? 'none' : 'block',
            top: 20,
            right: 24,
          }}>
          <ToggleLeaderboardConfig
            isOpen={showConfig}
            onClick={() => setShowConfig(c => !c)}
          />
        </div>
        <Box flexShrink={0} maxHeight="35%" overflow="auto">
          <EditableMarkdown
            value={description}
            onChange={setDescription}
            placeholder={DEFAULT_DESCRIPTION}
          />
        </Box>
        {showingAlert && (
          <UnlistedAlert onClose={() => setShowingAlert(false)} />
        )}
        <Box flexGrow={1} display="flex" flexDirection="row" overflow="hidden">
          <LeaderboardGrid
            entity={entity}
            project={project}
            loading={loading}
            data={data}
            onCellClick={handleCellClick}
          />
        </Box>
      </Box>
      {showConfig && (
        <Box flex={1} width="35%" height="100%" overflow="hidden">
          <LeaderboardConfigEditor
            entity={entity}
            project={project}
            config={currentConfig}
            onCancel={() => {
              cancelChanges();
              setShowConfig(false);
            }}
            onPersist={() => {
              persistConfig();
              setShowConfig(false);
            }}
            setConfig={setConfigLocal}
          />
        </Box>
      )}
    </Box>
  );
};

export const ToggleLeaderboardConfig: React.FC<{
  isOpen: boolean;
  onClick: () => void;
}> = ({isOpen, onClick}) => {
  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        alignItems: 'center',
      }}>
      <Button
        variant="ghost"
        size="medium"
        onClick={onClick}
        tooltip={isOpen ? 'Discard Changes' : 'Configure Leaderboard'}
        icon={isOpen ? 'close' : 'settings'}
      />
    </Box>
  );
};

const UnlistedAlert: React.FC<{onClose: () => void}> = ({onClose}) => {
  return (
    <Alert severity="info" onClose={onClose}>
      <Typography variant="body1">
        You have found an internal, unlisted beta page! Please expect bugs and
        incomplete features. Permilinks & saving state are not yet supported
      </Typography>
    </Alert>
  );
};

// TODO:
// * [ ] Edit panel revisions
