import { TextField, Box, Typography, Paper, Alert } from '@mui/material';
import type { StrategyType } from './StrategySelector';

interface ConfigEditorProps {
  strategy: StrategyType | null;
  config: Record<string, unknown>;
  onConfigChange: (config: Record<string, unknown>) => void;
}

const defaultConfigs: Record<StrategyType, Record<string, unknown>> = {
  LPT: {
    num_fillers: 4,
    max_concurrent_lots: 10,
  },
  SPT: {
    num_fillers: 4,
    max_concurrent_lots: 10,
  },
  CFS: {
    num_fillers: 4,
    max_concurrent_lots: 10,
    critical_threshold: 0.8,
  },
  Hybrid: {
    num_fillers: 4,
    max_concurrent_lots: 10,
    pack_first_ratio: 0.5,
  },
  MILP: {
    num_fillers: 4,
    max_concurrent_lots: 10,
    time_limit_seconds: 300,
    mip_gap: 0.05,
  },
};

const configDescriptions: Record<string, string> = {
  num_fillers: 'Number of parallel filling machines available',
  max_concurrent_lots: 'Maximum number of lots that can be filled simultaneously',
  critical_threshold: 'Priority threshold for critical lots (0-1)',
  pack_first_ratio: 'Ratio of lots to pack first in hybrid strategy (0-1)',
  time_limit_seconds: 'Maximum time for MILP solver in seconds',
  mip_gap: 'Acceptable optimality gap for MILP (0-1)',
};

export const ConfigEditor = ({ strategy, config, onConfigChange }: ConfigEditorProps) => {
  if (!strategy) {
    return (
      <Alert severity="info">
        Please select a strategy first to configure parameters.
      </Alert>
    );
  }

  const defaultConfig = defaultConfigs[strategy];
  const currentConfig = { ...defaultConfig, ...config };

  const handleFieldChange = (field: string, value: string) => {
    const numValue = parseFloat(value);
    const newConfig = {
      ...currentConfig,
      [field]: isNaN(numValue) ? value : numValue,
    };
    onConfigChange(newConfig);
  };

  return (
    <Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Configure parameters for the {strategy} strategy. Default values are provided but can be adjusted based on your requirements.
      </Typography>

      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
          {Object.entries(defaultConfig).map(([key, defaultValue]) => {
            const currentValue = currentConfig[key];
            const description = configDescriptions[key] || '';

            return (
              <Box key={key}>
                <TextField
                  fullWidth
                  label={key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                  value={currentValue ?? defaultValue}
                  onChange={(e) => handleFieldChange(key, e.target.value)}
                  type="number"
                  helperText={description}
                  InputLabelProps={{ shrink: true }}
                />
              </Box>
            );
          })}
        </Box>
      </Paper>

      <Alert severity="info" sx={{ mt: 2 }}>
        <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
          Configuration Tips:
        </Typography>
        <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
          <li>
            <strong>num_fillers:</strong> Should match your actual number of filling machines
          </li>
          <li>
            <strong>max_concurrent_lots:</strong> Consider machine capacity and lot sizes
          </li>
          {strategy === 'MILP' && (
            <>
              <li>
                <strong>time_limit_seconds:</strong> Higher values may give better solutions but take longer
              </li>
              <li>
                <strong>mip_gap:</strong> Smaller gaps give more optimal solutions but take longer to compute
              </li>
            </>
          )}
        </ul>
      </Alert>
    </Box>
  );
};
