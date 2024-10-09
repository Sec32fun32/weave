import AddIcon from '@mui/icons-material/Add';
import {Box, Button, Typography} from '@mui/material';
import React, {useState} from 'react';

import {ColumnConfig} from './ColumnConfig';
import {LeaderboardConfigType} from './LeaderboardConfigType';
import {ModelConfig} from './ModelConfig';

export const LeaderboardConfig: React.FC<{
  currentConfig: LeaderboardConfigType;
  onConfigUpdate: (newConfig: LeaderboardConfigType) => void;
}> = ({currentConfig, onConfigUpdate}) => {
  const [config, setConfig] = useState<LeaderboardConfigType>(currentConfig);

  const handleSave = () => {
    onConfigUpdate(config);
  };

  const handleCancel = () => {
    setConfig(currentConfig);
  };

  const handleAddColumn = () => {
    setConfig(prev => ({
      ...prev,
      config: {
        ...prev.config,
        columns: [
          ...prev.config.columns,
          {dataset: {name: '', version: 'latest'}, scores: []},
        ],
      },
    }));
  };

  const handleRemoveColumn = (index: number) => {
    setConfig(prev => ({
      ...prev,
      config: {
        ...prev.config,
        columns: prev.config.columns.filter((_, i) => i !== index),
      },
    }));
  };

  const handleUpdateColumn = (
    index: number,
    updatedColumn: LeaderboardConfigType['config']['columns'][0]
  ) => {
    setConfig(prev => ({
      ...prev,
      config: {
        ...prev.config,
        columns: prev.config.columns.map((column, i) =>
          i === index ? updatedColumn : column
        ),
      },
    }));
  };

  const handleAddModel = () => {
    setConfig(prev => ({
      ...prev,
      config: {
        ...prev.config,
        models: [...prev.config.models, {name: '', version: 'latest'}],
      },
    }));
  };

  const handleRemoveModel = (index: number) => {
    setConfig(prev => ({
      ...prev,
      config: {
        ...prev.config,
        models: prev.config.models.filter((_, i) => i !== index),
      },
    }));
  };

  const handleUpdateModel = (
    index: number,
    updatedModel: LeaderboardConfigType['config']['models'][0]
  ) => {
    setConfig(prev => ({
      ...prev,
      config: {
        ...prev.config,
        models: prev.config.models.map((model, i) =>
          i === index ? updatedModel : model
        ),
      },
    }));
  };

  return (
    <Box sx={{width: '100%', p: 2}}>
      <Typography variant="h5" gutterBottom>
        Leaderboard Configuration
      </Typography>

      <Box sx={{mb: 4}}>
        <Typography variant="h6" gutterBottom>
          Columns
        </Typography>
        {config.config.columns.map((column, index) => (
          <ColumnConfig
            key={index}
            column={column}
            onUpdate={updatedColumn => handleUpdateColumn(index, updatedColumn)}
            onRemove={() => handleRemoveColumn(index)}
          />
        ))}
        <Button startIcon={<AddIcon />} onClick={handleAddColumn} sx={{mt: 2}}>
          Add Column
        </Button>
      </Box>

      <Box sx={{mb: 4}}>
        <Typography variant="h6" gutterBottom>
          Models
        </Typography>
        {config.config.models.map((model, index) => (
          <ModelConfig
            key={index}
            model={model}
            onUpdate={updatedModel => handleUpdateModel(index, updatedModel)}
            onRemove={() => handleRemoveModel(index)}
          />
        ))}
        <Button startIcon={<AddIcon />} onClick={handleAddModel} sx={{mt: 2}}>
          Add Model
        </Button>
      </Box>

      <Box sx={{display: 'flex', justifyContent: 'flex-end', mt: 4}}>
        <Button variant="outlined" onClick={handleCancel} sx={{mr: 2}}>
          Cancel
        </Button>
        <Button variant="contained" onClick={handleSave}>
          Save
        </Button>
      </Box>
    </Box>
  );
};
