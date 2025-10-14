
import {
  Container,
  Typography,
  Box,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  Alert,
  Snackbar,
} from '@mui/material';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { DashboardKpiCards } from '@/components/dashboard/DashboardKpiCards';
import { RecentSchedulesTable } from '@/components/dashboard/RecentSchedulesTable';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { ScheduleFiltersBar } from '@/components/dashboard/ScheduleFiltersBar';
import { DashboardCharts } from '@/components/dashboard/DashboardCharts';
import type { ScheduleFilters } from '@/components/dashboard/ScheduleFiltersBar';
import { deleteSchedule, getScheduleStats } from '@/api/schedules';
import type { Schedule } from '@/api/schedules';

export const Dashboard = () => {
  const [chartData, setChartData] = useState<{
    strategies: { name: string; schedules: number }[];
    status: { name: string; value: number; color: string }[];
  }>({
    strategies: [],
    status: [],
  });
  const { user } = useAuth();
  const navigate = useNavigate();
  const [filters, setFilters] = useState<ScheduleFilters>({
    search: '',
    status: 'all',
    strategy: 'all',
  });
    const [schedules, setSchedules] = useState<Schedule[]>([]);
    const [loading, setLoading] = useState(true);
    const [kpiStats, setKpiStats] = useState({
      total_schedules: 0,
      active_schedules: 0,
      completed_schedules: 0,
      failed_schedules: 0,
      page: 1,
      page_size: 10,
      total_filtered: 0,
    });
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [scheduleToDelete, setScheduleToDelete] = useState<number | null>(null);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error';
  }>({
    open: false,
    message: '',
    severity: 'success',
  });

  // Fetch schedules from API
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        const stats = await getScheduleStats({
          page,
          page_size: pageSize,
          status: filters.status !== 'all' ? filters.status : undefined,
          strategy: filters.strategy !== 'all' ? filters.strategy : undefined,
          search: filters.search || undefined,
        });
        setSchedules(stats.schedules);
        setKpiStats(stats);
        setChartData({
          strategies: Object.entries(stats.strategies_distribution || {}).map(([name, schedules]) => ({ name, schedules })),
          status: Object.entries(stats.status_distribution || {}).map(([name, value], i) => ({ name, value, color: ['#4caf50','#2196f3','#ff9800','#f44336'][i % 4] })),
        });
      } catch (error) {
        setSnackbar({ open: true, message: 'Failed to fetch dashboard data', severity: 'error' });
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, [filters, page, pageSize]);

  const handleViewSchedule = (id: number) => {
    navigate(`/schedules/${id}`);
  };

  const handleDeleteSchedule = (id: number) => {
    setScheduleToDelete(id);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (scheduleToDelete === null) return;
    try {
      await deleteSchedule(scheduleToDelete);
      setSnackbar({
        open: true,
        message: 'Schedule deleted successfully',
        severity: 'success',
      });
      // Refetch dashboard data
      const stats = await getScheduleStats({
        page,
        page_size: pageSize,
        status: filters.status !== 'all' ? filters.status : undefined,
        strategy: filters.strategy !== 'all' ? filters.strategy : undefined,
        search: filters.search || undefined,
      });
      setSchedules(stats.schedules);
      setKpiStats(stats);
    } catch (error) {
      console.error('Failed to delete schedule:', error);
      setSnackbar({
        open: true,
        message: 'Failed to delete schedule',
        severity: 'error',
      });
    } finally {
      setDeleteDialogOpen(false);
      setScheduleToDelete(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setScheduleToDelete(null);
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
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
      <DashboardKpiCards
        data={[
          { label: 'Total Schedules', value: kpiStats.total_schedules, color: '#1976d2' },
          { label: 'Active', value: kpiStats.active_schedules, color: '#388e3c' },
          { label: 'Completed', value: kpiStats.completed_schedules, color: '#0288d1' },
          { label: 'Failed', value: kpiStats.failed_schedules, color: '#d32f2f' },
        ]}
      />

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
            page={page}
            pageSize={pageSize}
            total={kpiStats.total_filtered}
            onPageChange={setPage}
            onPageSizeChange={setPageSize}
          />
        )}
      </Box>

      {/* Analytics Charts */}
      <DashboardCharts
        strategiesData={chartData.strategies}
        statusData={chartData.status}
      />

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={handleDeleteCancel}
        aria-labelledby="delete-dialog-title"
        aria-describedby="delete-dialog-description"
      >
        <DialogTitle id="delete-dialog-title">Delete Schedule?</DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-dialog-description">
            Are you sure you want to delete this schedule? This action cannot be undone.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDeleteCancel} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained" autoFocus>
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success/Error Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};
