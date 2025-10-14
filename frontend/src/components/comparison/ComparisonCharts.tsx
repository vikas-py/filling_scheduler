import { Box, Typography, Stack, Paper } from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import type { Schedule } from '../../api/schedules';

interface ComparisonChartsProps {
  schedules: Schedule[];
}

const COLORS = ['#1976d2', '#dc004e', '#4caf50', '#ff9800'];

export const ComparisonCharts = ({ schedules }: ComparisonChartsProps) => {
  if (!schedules || schedules.length === 0) {
    return null;
  }

  // Prepare data for bar charts
  const barChartData = schedules.map((schedule, index) => {
    const activities = schedule.activities || [];
    const numFillers = (schedule.config.num_fillers as number) || 4;

    const totalActivities = activities.length;
    const maxEndTime = activities.length > 0 ? Math.max(...activities.map((a) => a.end_time)) : 0;
    const makespan = schedule.total_time || maxEndTime;

    const totalProcessingTime = activities.reduce((sum, a) => sum + a.duration, 0);
    const maxPossibleTime = makespan * numFillers;
    const utilization = maxPossibleTime > 0 ? (totalProcessingTime / maxPossibleTime) * 100 : 0;

    return {
      name: schedule.name.length > 15 ? schedule.name.substring(0, 15) + '...' : schedule.name,
      fullName: schedule.name,
      makespan: parseFloat(makespan.toFixed(2)),
      utilization: parseFloat(utilization.toFixed(1)),
      activities: totalActivities,
      color: COLORS[index % COLORS.length],
    };
  });

  // Prepare data for radar chart (normalized 0-100)
  const maxMakespan = Math.max(...barChartData.map((d) => d.makespan));
  const maxActivities = Math.max(...barChartData.map((d) => d.activities));

  const radarData = [
    {
      metric: 'Utilization',
      ...Object.fromEntries(
        schedules.map((schedule, i) => [
          schedule.name,
          barChartData[i].utilization,
        ])
      ),
    },
    {
      metric: 'Efficiency',
      ...Object.fromEntries(
        schedules.map((schedule, i) => [
          schedule.name,
          maxMakespan > 0 ? ((maxMakespan - barChartData[i].makespan) / maxMakespan) * 100 : 0,
        ])
      ),
    },
    {
      metric: 'Throughput',
      ...Object.fromEntries(
        schedules.map((schedule, i) => [
          schedule.name,
          maxActivities > 0 ? (barChartData[i].activities / maxActivities) * 100 : 0,
        ])
      ),
    },
  ];

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Performance Charts
      </Typography>

      <Stack spacing={3}>
        {/* Makespan Comparison */}
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Makespan Comparison (Lower is Better)
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Total time to complete all activities
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis label={{ value: 'Hours', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="makespan" name="Makespan (hours)" fill="#1976d2" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>

        {/* Utilization Comparison */}
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Utilization Comparison (Higher is Better)
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Percentage of time fillers are actively working
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis
                label={{ value: 'Utilization (%)', angle: -90, position: 'insideLeft' }}
                domain={[0, 100]}
              />
              <Tooltip />
              <Legend />
              <Bar dataKey="utilization" name="Utilization (%)" fill="#4caf50" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>

        {/* Radar Chart - Overall Performance */}
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Overall Performance Radar
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Multi-dimensional comparison of key metrics (normalized 0-100)
          </Typography>
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} />
              <Tooltip />
              <Legend />
              {schedules.map((schedule, index) => (
                <Radar
                  key={schedule.id}
                  name={schedule.name}
                  dataKey={schedule.name}
                  stroke={COLORS[index % COLORS.length]}
                  fill={COLORS[index % COLORS.length]}
                  fillOpacity={0.3}
                />
              ))}
            </RadarChart>
          </ResponsiveContainer>
        </Paper>
      </Stack>
    </Box>
  );
};
