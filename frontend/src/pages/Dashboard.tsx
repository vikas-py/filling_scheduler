
import { Container, Typography, Box, CircularProgress } from '@mui/material';
import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { DashboardKpiCards } from '@/components/dashboard/DashboardKpiCards';
import { RecentSchedulesTable } from '@/components/dashboard/RecentSchedulesTable';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { ScheduleFiltersBar } from '@/components/dashboard/ScheduleFiltersBar';
import { DashboardCharts } from '@/components/dashboard/DashboardCharts';
import type { ScheduleFilters } from '@/components/dashboard/ScheduleFiltersBar';
import { getSchedules } from '@/api/schedules';
import type { Schedule } from '@/api/schedules';

export const Dashboard = () => {
  const { user } = useAuth();
  const [filters, setFilters] = useState<ScheduleFilters>({
    search: '',
    status: 'all',
    strategy: 'all',
  });
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch schedules from API
  useEffect(() => {
    const fetchSchedules = async () => {
      try {
        setLoading(true);
        const response = await getSchedules(1, 10, {
          status: filters.status !== 'all' ? filters.status : undefined,
          strategy: filters.strategy !== 'all' ? filters.strategy : undefined,
          search: filters.search || undefined,
        });
        setSchedules(response.schedules);
      } catch (error) {
        console.error('Failed to fetch schedules:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSchedules();
  }, [filters]);

  const handleViewSchedule = (id: number) => {
    console.log('Viewing schedule:', id);
    // TODO: Navigate to schedule detail page
  };

  const handleDeleteSchedule = async (id: number) => {
    console.log('Deleting schedule:', id);
    // TODO: Show confirmation dialog and delete schedule
    // After deletion, refetch schedules
  };

  const handleFilterChange = (newFilters: ScheduleFilters) => {
    setFilters(newFilters);
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
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <RecentSchedulesTable
            schedules={schedules}
            onView={handleViewSchedule}
            onDelete={handleDeleteSchedule}
          />
        )}
      </Box>

      {/* Analytics Charts */}
      <DashboardCharts />
    </Container>
  );
};
