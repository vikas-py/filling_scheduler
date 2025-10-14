import { Box, Typography, Paper } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface Activity {
  id: string;
  lot_id: string;
  filler_id: number;
  start_time: number;
  end_time: number;
  duration: number;
}

interface GanttChartProps {
  activities: Activity[];
  numFillers?: number;
}

// Color palette for different fillers
const COLORS = [
  '#1976d2',
  '#dc004e',
  '#4caf50',
  '#ff9800',
  '#9c27b0',
  '#00bcd4',
  '#ff5722',
  '#795548',
];

const getFillerColor = (fillerId: number): string => {
  return COLORS[fillerId % COLORS.length];
};

export const GanttChart = ({ activities, numFillers = 4 }: GanttChartProps) => {
  if (!activities || activities.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No activities to display. Schedule may still be processing.
        </Typography>
      </Paper>
    );
  }

  // Group activities by filler
  const fillerGroups = Array.from({ length: numFillers }, (_, i) => {
    const fillerActivities = activities.filter((a) => a.filler_id === i);
    return {
      filler: `Filler ${i + 1}`,
      fillerId: i,
      activities: fillerActivities,
    };
  });

  // Find max time for chart scaling
  const maxTime = Math.max(...activities.map((a) => a.end_time));

  // Transform data for Recharts (one bar per activity)
  const chartData = activities.map((activity) => ({
    name: activity.lot_id,
    fillerId: activity.filler_id,
    start: activity.start_time,
    duration: activity.duration,
    end: activity.end_time,
    filler: `Filler ${activity.filler_id + 1}`,
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Paper sx={{ p: 1.5 }}>
          <Typography variant="subtitle2" fontWeight="bold">
            {data.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {data.filler}
          </Typography>
          <Typography variant="body2">
            Start: {data.start.toFixed(2)}h
          </Typography>
          <Typography variant="body2">
            End: {data.end.toFixed(2)}h
          </Typography>
          <Typography variant="body2">
            Duration: {data.duration.toFixed(2)}h
          </Typography>
        </Paper>
      );
    }
    return null;
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Schedule Gantt Chart
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Timeline view showing activities across all fillers. Each color represents a different filler.
      </Typography>

      {/* Gantt Chart - Horizontal bars by filler */}
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 20, right: 30, left: 100, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            type="number"
            domain={[0, maxTime * 1.1]}
            label={{ value: 'Time (hours)', position: 'insideBottom', offset: -10 }}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={90}
            tick={{ fontSize: 12 }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar dataKey="duration" name="Activity Duration">
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getFillerColor(entry.fillerId)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      {/* Filler utilization summary */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>
          Filler Utilization
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          {fillerGroups.map((group) => {
            const totalTime = group.activities.reduce((sum, a) => sum + a.duration, 0);
            const utilization = maxTime > 0 ? (totalTime / maxTime) * 100 : 0;

            return (
              <Paper
                key={group.fillerId}
                sx={{
                  p: 2,
                  flex: '1 1 200px',
                  borderLeft: 4,
                  borderColor: getFillerColor(group.fillerId),
                }}
              >
                <Typography variant="subtitle2" fontWeight="bold">
                  {group.filler}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {group.activities.length} activities
                </Typography>
                <Typography variant="body2">
                  Total: {totalTime.toFixed(2)}h
                </Typography>
                <Typography variant="body2">
                  Utilization: {utilization.toFixed(1)}%
                </Typography>
              </Paper>
            );
          })}
        </Box>
      </Box>
    </Box>
  );
};
