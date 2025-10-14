import { Box, Typography, Paper, Stack, Chip } from '@mui/material';
import {
  Schedule as ScheduleIcon,
  AccessTime,
  Speed,
  TrendingUp,
} from '@mui/icons-material';
import type { Schedule } from '../../api/schedules';

interface MetricsComparisonProps {
  schedules: Schedule[];
}

interface MetricRowProps {
  label: string;
  icon: React.ReactNode;
  values: (string | number)[];
  bestIndex?: number;
  worstIndex?: number;
}

const MetricRow = ({ label, icon, values, bestIndex, worstIndex }: MetricRowProps) => (
  <Box sx={{ mb: 2 }}>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
      <Box sx={{ color: 'text.secondary' }}>{icon}</Box>
      <Typography variant="subtitle2" color="text.secondary">
        {label}
      </Typography>
    </Box>
    <Stack direction="row" spacing={1}>
      {values.map((value, index) => (
        <Box
          key={index}
          sx={{
            flex: 1,
            p: 1.5,
            borderRadius: 1,
            border: 1,
            borderColor:
              index === bestIndex
                ? 'success.main'
                : index === worstIndex
                ? 'error.main'
                : 'divider',
            bgcolor:
              index === bestIndex
                ? 'success.lighter'
                : index === worstIndex
                ? 'error.lighter'
                : 'background.paper',
          }}
        >
          <Typography variant="h6" fontWeight="bold">
            {value}
          </Typography>
          {index === bestIndex && (
            <Chip label="Best" size="small" color="success" sx={{ mt: 0.5 }} />
          )}
          {index === worstIndex && (
            <Chip label="Worst" size="small" color="error" sx={{ mt: 0.5 }} />
          )}
        </Box>
      ))}
    </Stack>
  </Box>
);

export const MetricsComparison = ({ schedules }: MetricsComparisonProps) => {
  if (!schedules || schedules.length === 0) {
    return null;
  }

  // Calculate metrics for each schedule
  const metrics = schedules.map((schedule) => {
    const activities = schedule.activities || [];
    const numFillers = (schedule.config.num_fillers as number) || 4;

    const totalActivities = activities.length;
    const maxEndTime = activities.length > 0 ? Math.max(...activities.map((a) => a.end_time)) : 0;
    const makespan = schedule.total_time || maxEndTime;

    const totalProcessingTime = activities.reduce((sum, a) => sum + a.duration, 0);
    const maxPossibleTime = makespan * numFillers;
    const utilization = maxPossibleTime > 0 ? (totalProcessingTime / maxPossibleTime) * 100 : 0;

    const avgDuration = totalActivities > 0 ? totalProcessingTime / totalActivities : 0;

    return {
      name: schedule.name,
      totalActivities,
      makespan,
      avgDuration,
      utilization,
      numLots: schedule.num_lots,
    };
  });

  // Find best/worst for each metric
  const makespanValues = metrics.map((m) => m.makespan);
  const bestMakespanIndex = makespanValues.indexOf(Math.min(...makespanValues));
  const worstMakespanIndex = makespanValues.indexOf(Math.max(...makespanValues));

  const utilizationValues = metrics.map((m) => m.utilization);
  const bestUtilizationIndex = utilizationValues.indexOf(Math.max(...utilizationValues));
  const worstUtilizationIndex = utilizationValues.indexOf(Math.min(...utilizationValues));

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Metrics Comparison
      </Typography>

      {/* Schedule Names Header */}
      <Stack direction="row" spacing={1} sx={{ mb: 3 }}>
        <Box sx={{ width: 200 }} /> {/* Spacer for metric label */}
        {schedules.map((schedule) => (
          <Paper
            key={schedule.id}
            sx={{
              flex: 1,
              p: 1.5,
              textAlign: 'center',
              bgcolor: 'primary.lighter',
            }}
          >
            <Typography variant="subtitle1" fontWeight="bold">
              {schedule.name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {schedule.strategy}
            </Typography>
          </Paper>
        ))}
      </Stack>

      {/* Metrics Rows */}
      <MetricRow
        label="Number of Lots"
        icon={<ScheduleIcon />}
        values={metrics.map((m) => m.numLots)}
      />

      <MetricRow
        label="Total Activities"
        icon={<ScheduleIcon />}
        values={metrics.map((m) => m.totalActivities)}
      />

      <MetricRow
        label="Makespan (hours)"
        icon={<AccessTime />}
        values={metrics.map((m) => m.makespan.toFixed(2))}
        bestIndex={bestMakespanIndex}
        worstIndex={worstMakespanIndex}
      />

      <MetricRow
        label="Average Duration (hours)"
        icon={<Speed />}
        values={metrics.map((m) => m.avgDuration.toFixed(2))}
      />

      <MetricRow
        label="Overall Utilization (%)"
        icon={<TrendingUp />}
        values={metrics.map((m) => m.utilization.toFixed(1))}
        bestIndex={bestUtilizationIndex}
        worstIndex={worstUtilizationIndex}
      />
    </Box>
  );
};
