import { Box, Typography, Paper, Stack } from '@mui/material';
import { Schedule, AccessTime, Speed, TrendingUp } from '@mui/icons-material';

interface Activity {
  id: string;
  lot_id: string;
  filler_id: number;
  start_time: number;
  end_time: number;
  duration: number;
}

interface ScheduleStatsProps {
  activities: Activity[];
  numFillers: number;
  totalTime?: number;
  scheduleStartTime?: string; // ISO datetime string when schedule starts
}

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color: string;
}

const StatCard = ({ title, value, subtitle, icon, color }: StatCardProps) => (
  <Paper
    sx={{
      p: 2,
      flex: '1 1 250px',
      borderLeft: 4,
      borderColor: color,
    }}
  >
    <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
      <Box sx={{ color, mt: 0.5 }}>{icon}</Box>
      <Box sx={{ flex: 1 }}>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          {title}
        </Typography>
        <Typography variant="h4" fontWeight="bold" gutterBottom>
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="caption" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </Box>
    </Box>
  </Paper>
);

export const ScheduleStats = ({ activities, numFillers, totalTime, scheduleStartTime }: ScheduleStatsProps) => {
  // Format schedule time window
  const formatDateTime = (date: Date): string => {
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getScheduleTimeWindow = (): string => {
    if (!scheduleStartTime) return '';
    const startDate = new Date(scheduleStartTime);
    const endDate = new Date(startDate.getTime() + (totalTime || 0) * 60 * 60 * 1000);
    return `${formatDateTime(startDate)} - ${formatDateTime(endDate)}`;
  };

  if (!activities || activities.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No statistics available yet. Schedule may still be processing.
        </Typography>
      </Paper>
    );
  }

  // Calculate statistics
  const totalActivities = activities.length;
  const maxEndTime = Math.max(...activities.map((a) => a.end_time));
  const makespan = totalTime || maxEndTime;

  // Calculate total processing time
  const totalProcessingTime = activities.reduce((sum, a) => sum + a.duration, 0);

  // Calculate average utilization
  const maxPossibleTime = makespan * numFillers;
  const utilization = maxPossibleTime > 0 ? (totalProcessingTime / maxPossibleTime) * 100 : 0;

  // Calculate average activity duration
  const avgDuration = totalActivities > 0 ? totalProcessingTime / totalActivities : 0;

  // Per-filler statistics
  const fillerStats = Array.from({ length: numFillers }, (_, fillerId) => {
    const fillerActivities = activities.filter((a) => a.filler_id === fillerId);
    const fillerTime = fillerActivities.reduce((sum, a) => sum + a.duration, 0);
    const fillerUtilization = makespan > 0 ? (fillerTime / makespan) * 100 : 0;

    return {
      fillerId,
      activities: fillerActivities.length,
      totalTime: fillerTime,
      utilization: fillerUtilization,
    };
  });

  // Find best and worst utilization
  const bestFiller = fillerStats.reduce((best, filler) =>
    filler.utilization > best.utilization ? filler : best
  );
  const worstFiller = fillerStats.reduce((worst, filler) =>
    filler.utilization < worst.utilization ? filler : worst
  );

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Schedule Statistics
      </Typography>

      {/* Schedule Time Window */}
      {scheduleStartTime && (
        <Paper sx={{ p: 2, mb: 3, bgcolor: 'info.light' }}>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            Schedule Time Window
          </Typography>
          <Typography variant="body1" fontWeight="medium">
            {getScheduleTimeWindow()}
          </Typography>
        </Paper>
      )}

      {/* Main KPIs */}
      <Stack direction="row" spacing={2} sx={{ mb: 4, flexWrap: 'wrap' }}>
        <StatCard
          title="Total Activities"
          value={totalActivities}
          subtitle={`${(totalActivities / numFillers).toFixed(1)} per filler`}
          icon={<Schedule sx={{ fontSize: 32 }} />}
          color="#1976d2"
        />
        <StatCard
          title="Makespan"
          value={`${makespan.toFixed(2)}h`}
          subtitle="Total schedule duration"
          icon={<AccessTime sx={{ fontSize: 32 }} />}
          color="#4caf50"
        />
        <StatCard
          title="Average Duration"
          value={`${avgDuration.toFixed(2)}h`}
          subtitle="Per activity"
          icon={<Speed sx={{ fontSize: 32 }} />}
          color="#ff9800"
        />
        <StatCard
          title="Overall Utilization"
          value={`${utilization.toFixed(1)}%`}
          subtitle={`${totalProcessingTime.toFixed(2)}h / ${maxPossibleTime.toFixed(2)}h`}
          icon={<TrendingUp sx={{ fontSize: 32 }} />}
          color="#9c27b0"
        />
      </Stack>

      {/* Filler breakdown */}
      <Typography variant="h6" gutterBottom>
        Filler Performance
      </Typography>
      <Stack direction="row" spacing={2} sx={{ mb: 3, flexWrap: 'wrap' }}>
        {fillerStats.map((filler) => (
          <Paper
            key={filler.fillerId}
            sx={{
              p: 2,
              flex: '1 1 200px',
              borderLeft: 4,
              borderColor:
                filler.fillerId === bestFiller.fillerId
                  ? 'success.main'
                  : filler.fillerId === worstFiller.fillerId
                  ? 'warning.main'
                  : 'primary.main',
            }}
          >
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
              Filler {filler.fillerId + 1}
              {filler.fillerId === bestFiller.fillerId && ' 🏆'}
            </Typography>
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Activities: <strong>{filler.activities}</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Total Time: <strong>{filler.totalTime.toFixed(2)}h</strong>
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Utilization: <strong>{filler.utilization.toFixed(1)}%</strong>
              </Typography>
            </Box>
          </Paper>
        ))}
      </Stack>

      {/* Insights */}
      <Paper sx={{ p: 2, bgcolor: 'info.lighter' }}>
        <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
          Insights:
        </Typography>
        <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
          <li>
            <Typography variant="body2">
              Best performing filler: <strong>Filler {bestFiller.fillerId + 1}</strong> with{' '}
              {bestFiller.utilization.toFixed(1)}% utilization
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              Lowest utilization: <strong>Filler {worstFiller.fillerId + 1}</strong> with{' '}
              {worstFiller.utilization.toFixed(1)}% utilization
            </Typography>
          </li>
          <li>
            <Typography variant="body2">
              Utilization variance:{' '}
              {(bestFiller.utilization - worstFiller.utilization).toFixed(1)}% difference
            </Typography>
          </li>
          {utilization < 70 && (
            <li>
              <Typography variant="body2" color="warning.dark">
                Overall utilization is below 70%. Consider reducing the number of fillers or
                adjusting the schedule strategy.
              </Typography>
            </li>
          )}
          {utilization > 90 && (
            <li>
              <Typography variant="body2" color="success.dark">
                Excellent utilization! The schedule is highly efficient.
              </Typography>
            </li>
          )}
        </ul>
      </Paper>
    </Box>
  );
};
