import { Card, CardContent, Typography, Box, Stack } from '@mui/material';

export interface DashboardKpi {
  label: string;
  value: number;
  color?: string;
}

const kpis: DashboardKpi[] = [
  { label: 'Total Schedules', value: 0, color: '#1976d2' },
  { label: 'Active', value: 0, color: '#388e3c' },
  { label: 'Completed', value: 0, color: '#0288d1' },
  { label: 'Failed', value: 0, color: '#d32f2f' },
];

export const DashboardKpiCards = ({ data = kpis }: { data?: DashboardKpi[] }) => (
  <Box sx={{ mb: 4 }}>
    <Stack direction="row" spacing={3} flexWrap="wrap" useFlexGap>
      {data.map((kpi) => (
        <Box key={kpi.label} sx={{ flex: { xs: '1 1 100%', sm: '1 1 calc(50% - 12px)', md: '1 1 calc(25% - 18px)' }, minWidth: 0 }}>
          <Card sx={{ borderLeft: `6px solid ${kpi.color}` }}>
            <CardContent>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                {kpi.label}
              </Typography>
              <Typography variant="h4" color={kpi.color}>
                {kpi.value}
              </Typography>
            </CardContent>
          </Card>
        </Box>
      ))}
    </Stack>
  </Box>
);
