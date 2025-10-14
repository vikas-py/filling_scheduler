import { Box, Typography, TextField, Paper, Divider, Stack, Chip } from '@mui/material';
import type { StrategyType } from '../schedule/StrategySelector';

interface StrategyDefaultsProps {
  onChange?: () => void;
}

const strategies: StrategyType[] = ['LPT', 'SPT', 'CFS', 'Hybrid', 'MILP'];

const strategyDescriptions: Record<StrategyType, string> = {
  LPT: 'Longest Processing Time - Schedules longer tasks first',
  SPT: 'Shortest Processing Time - Schedules shorter tasks first',
  CFS: 'Critical Fill Strategy - Prioritizes critical lots',
  Hybrid: 'Hybrid approach combining multiple strategies',
  MILP: 'Mixed Integer Linear Programming - Optimal mathematical solution',
};

const defaultConfigs: Record<StrategyType, Record<string, number>> = {
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

const fieldLabels: Record<string, string> = {
  num_fillers: 'Number of Fillers',
  max_concurrent_lots: 'Max Concurrent Lots',
  critical_threshold: 'Critical Threshold',
  pack_first_ratio: 'Pack First Ratio',
  time_limit_seconds: 'Time Limit (seconds)',
  mip_gap: 'MIP Gap',
};

const fieldHelpers: Record<string, string> = {
  num_fillers: 'Number of parallel filling machines available',
  max_concurrent_lots: 'Maximum lots that can be filled simultaneously',
  critical_threshold: 'Priority threshold for critical lots (0-1)',
  pack_first_ratio: 'Ratio of lots to pack first (0-1)',
  time_limit_seconds: 'Maximum solving time for optimizer',
  mip_gap: 'Acceptable optimality gap (0-1)',
};

export const StrategyDefaults = ({ onChange }: StrategyDefaultsProps) => {
  const handleChange = () => {
    if (onChange) onChange();
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Strategy Defaults
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Configure default parameters for each scheduling strategy. These values will be pre-filled
        when creating new schedules.
      </Typography>

      <Stack spacing={3}>
        {strategies.map((strategy) => {
          const config = defaultConfigs[strategy];

          return (
            <Paper key={strategy} sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Typography variant="h6">{strategy}</Typography>
                <Chip label={strategy} color="primary" size="small" />
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                {strategyDescriptions[strategy]}
              </Typography>
              <Divider sx={{ mb: 3 }} />

              <Stack spacing={2}>
                {Object.entries(config).map(([key, value]) => (
                  <TextField
                    key={key}
                    fullWidth
                    label={fieldLabels[key] || key}
                    type="number"
                    defaultValue={value}
                    helperText={fieldHelpers[key]}
                    onChange={handleChange}
                    InputLabelProps={{ shrink: true }}
                  />
                ))}
              </Stack>
            </Paper>
          );
        })}
      </Stack>
    </Box>
  );
};
