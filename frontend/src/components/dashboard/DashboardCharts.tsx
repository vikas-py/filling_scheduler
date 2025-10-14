import { Paper, Typography, Box, Stack } from '@mui/material';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

// Mock data for charts
const strategiesData = [
  { name: 'LPT', schedules: 24 },
  { name: 'SPT', schedules: 18 },
  { name: 'CFS', schedules: 32 },
  { name: 'Hybrid', schedules: 15 },
  { name: 'MILP', schedules: 8 },
];

const statusData = [
  { name: 'Completed', value: 65, color: '#4caf50' },
  { name: 'Running', value: 12, color: '#2196f3' },
  { name: 'Pending', value: 8, color: '#ff9800' },
  { name: 'Failed', value: 5, color: '#f44336' },
];

const COLORS = ['#4caf50', '#2196f3', '#ff9800', '#f44336'];

interface DashboardChartsProps {
  strategiesData?: typeof strategiesData;
  statusData?: typeof statusData;
}

export const DashboardCharts = ({
  strategiesData: customStrategiesData = strategiesData,
  statusData: customStatusData = statusData,
}: DashboardChartsProps) => {
  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h6" gutterBottom sx={{ mb: 2 }}>
        Schedule Analytics
      </Typography>
      <Stack direction={{ xs: 'column', md: 'row' }} spacing={3}>
        {/* Strategies Bar Chart */}
        <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 60%' } }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle1" gutterBottom fontWeight={500}>
              Schedules by Strategy
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={customStrategiesData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="schedules" fill="#1976d2" name="Number of Schedules" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Box>

        {/* Status Pie Chart */}
        <Box sx={{ flex: { xs: '1 1 100%', md: '1 1 40%' } }}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="subtitle1" gutterBottom fontWeight={500}>
              Status Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={customStatusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {customStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color || COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Box>
      </Stack>
    </Box>
  );
};
