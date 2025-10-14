
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
import { getSchedules, deleteSchedule } from '@/api/schedules';
import type { Schedule } from '@/api/schedules';

export const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [filters, setFilters] = useState<ScheduleFilters>({
    search: '',
    status: 'all',
    strategy: 'all',
  });
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
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
      // Refetch schedules
      const response = await getSchedules(1, 10, {
        status: filters.status !== 'all' ? filters.status : undefined,
        strategy: filters.strategy !== 'all' ? filters.strategy : undefined,
        search: filters.search || undefined,
      });
      setSchedules(response.schedules);
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
