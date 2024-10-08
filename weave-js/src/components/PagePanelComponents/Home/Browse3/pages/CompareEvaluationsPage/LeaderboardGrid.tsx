import React, { useMemo } from 'react';
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid';
import { Box } from '@mui/material';

interface LeaderboardGridProps {
  data: {
    models: string[];
    metrics: string[];
    scores: {[key: string]: {[key: string]: number}};
  };
  onCellClick: (modelName: string, metricName: string, score: number) => void;
}

interface RowData {
  id: number;
  model: string;
  [key: string]: number | string;
}

export const LeaderboardGrid: React.FC<LeaderboardGridProps> = ({
  data,
  onCellClick,
}) => {
  const metricRanges = useMemo(() => {
    const ranges: {[key: string]: {min: number; max: number}} = {};
    data.metrics.forEach(metric => {
      const scores = data.models.map(model => data.scores[model][metric]);
      ranges[metric] = {
        min: Math.min(...scores),
        max: Math.max(...scores)
      };
    });
    return ranges;
  }, [data]);

  const getColorForScore = (metric: string, score: number) => {
    const { min, max } = metricRanges[metric];
    const normalizedScore = (score - min) / (max - min);
    return `hsl(${120 * normalizedScore}, 70%, 85%)`;
  };

  const columns: GridColDef[] = [
    { field: 'model', headerName: 'Model', width: 200, flex: 1 },
    ...data.metrics.map(metric => ({
      field: metric,
      headerName: metric,
      width: 130,
      flex: 1,
      renderCell: (params: GridRenderCellParams) => (
        <div
          style={{
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: getColorForScore(metric, params.value as number),
          }}
          onClick={() =>
            onCellClick(
              params.row.model,
              params.field as string,
              params.value as number
            )
          }
        >
          {`${(params.value as number).toFixed(2)}%`}
        </div>
      ),
    })),
  ];

  const rows: RowData[] = data.models.map((model, index) => ({
    id: index,
    model,
    ...data.scores[model],
  }));

  return (
    <Box sx={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column' }}>
      <DataGrid
        rows={rows}
        columns={columns}
        autoPageSize
        disableRowSelectionOnClick
        hideFooterSelectedRowCount
        sx={{
          flexGrow: 1,
          '& .MuiDataGrid-main': { overflow: 'unset' },
          '& .MuiDataGrid-virtualScroller': { overflow: 'unset' },
          '& .MuiDataGrid-footerContainer': { position: 'sticky', bottom: 0, bgcolor: 'background.paper', zIndex: 1 },
        }}
      />
    </Box>
  );
};
