
import { Container, Typography, Box } from '@mui/material';
import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { DashboardKpiCards } from '@/components/dashboard/DashboardKpiCards';
import { RecentSchedulesTable } from '@/components/dashboard/RecentSchedulesTable';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { ScheduleFiltersBar } from '@/components/dashboard/ScheduleFiltersBar';
import { DashboardCharts } from '@/components/dashboard/DashboardCharts';
import type { ScheduleFilters } from '@/components/dashboard/ScheduleFiltersBar';

export const Dashboard = () => {
  const { user } = useAuth();
  const [, setFilters] = useState<ScheduleFilters>({
    search: '',
    status: 'all',
    strategy: 'all',
  });

  const handleViewSchedule = (id: number) => {
    console.log('Viewing schedule:', id);
    // TODO: Navigate to schedule detail page
  };

  const handleDeleteSchedule = (id: number) => {
    console.log('Deleting schedule:', id);
    // TODO: Show confirmation dialog and delete schedule
  };

  const handleFilterChange = (newFilters: ScheduleFilters) => {
    setFilters(newFilters);
    console.log('Filters changed:', newFilters);
    // TODO: Apply filters to schedules list (will be implemented with backend API)
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Welcome back, {user?.email}!
      </Typography>

      {/* Quick Actions */}
      <QuickActions />

      {/* KPI Cards */}
      <DashboardKpiCards />

      {/* Filters */}
      <Box sx={{ mt: 4 }}>
        <ScheduleFiltersBar onFilterChange={handleFilterChange} />
      </Box>

      {/* Recent Schedules Table */}
      <Box>
        <RecentSchedulesTable
          onView={handleViewSchedule}
          onDelete={handleDeleteSchedule}
        />
      </Box>

      {/* Analytics Charts */}
      <DashboardCharts />
    </Container>
  );
};
