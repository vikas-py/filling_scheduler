import { useState, useEffect } from 'react';
import { Container, Typography, Box, Button, Paper, Alert, CircularProgress } from '@mui/material';
import { CompareArrows, Refresh } from '@mui/icons-material';
import { getSchedules, getSchedule } from '../api/schedules';
import type { Schedule } from '../api/schedules';
import { ScheduleSelector } from '../components/comparison/ScheduleSelector';
import { MetricsComparison } from '../components/comparison/MetricsComparison';
import { ComparisonCharts } from '../components/comparison/ComparisonCharts';
import { BestScheduleCard } from '../components/comparison/BestScheduleCard';

export const Compare = () => {
  const [availableSchedules, setAvailableSchedules] = useState<Schedule[]>([]);
  const [selectedScheduleIds, setSelectedScheduleIds] = useState<number[]>([]);
  const [selectedSchedules, setSelectedSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSchedules = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getSchedules(1, 100); // Get up to 100 schedules
      const completed = response.schedules.filter((s) => s.status === 'completed');
      setAvailableSchedules(completed);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load schedules');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSchedules();
  }, []);

  useEffect(() => {
    // Fetch detailed schedule data when IDs change
    const loadDetailedSchedules = async () => {
      if (selectedScheduleIds.length === 0) {
        setSelectedSchedules([]);
        return;
      }

      setLoadingDetails(true);
      setError(null);

      try {
        // Fetch detailed data for each selected schedule
        const detailedSchedules = await Promise.all(
          selectedScheduleIds.map((id) => getSchedule(id))
        );
        setSelectedSchedules(detailedSchedules);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load schedule details');
        setSelectedSchedules([]);
      } finally {
        setLoadingDetails(false);
      }
    };

    loadDetailedSchedules();
  }, [selectedScheduleIds]);

  const handleScheduleSelect = (scheduleIds: number[]) => {
    // Limit to maximum 4 schedules for comparison
    if (scheduleIds.length <= 4) {
      setSelectedScheduleIds(scheduleIds);
    }
  };

  const handleClearSelection = () => {
    setSelectedScheduleIds([]);
    setSelectedSchedules([]);
  };

  const canCompare = selectedSchedules.length >= 2;

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <CompareArrows sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" component="h1">
            Compare Schedules
          </Typography>
        </Box>
        <Button startIcon={<Refresh />} onClick={loadSchedules}>
          Refresh
        </Button>
      </Box>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Select 2-4 completed schedules to compare their performance metrics, utilization, and efficiency.
      </Typography>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Info Alert */}
      {!loading && availableSchedules.length === 0 && (
        <Alert severity="info" sx={{ mb: 3 }}>
          No completed schedules available for comparison. Create and complete some schedules first.
        </Alert>
      )}

      {/* Schedule Selector */}
      {availableSchedules.length > 0 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">Select Schedules</Typography>
            {selectedScheduleIds.length > 0 && (
              <Button size="small" onClick={handleClearSelection}>
                Clear Selection
              </Button>
            )}
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {selectedScheduleIds.length} of 4 schedules selected
          </Typography>

          <ScheduleSelector
            schedules={availableSchedules}
            selectedIds={selectedScheduleIds}
            onSelectionChange={handleScheduleSelect}
            maxSelection={4}
          />
        </Paper>
      )}

      {/* Comparison Results */}
      {loadingDetails ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <CircularProgress />
          <Typography variant="body1" color="text.secondary" sx={{ mt: 2 }}>
            Loading schedule details...
          </Typography>
        </Paper>
      ) : canCompare ? (
        <Box>
          <Paper sx={{ p: 3, mb: 3 }}>
            <MetricsComparison schedules={selectedSchedules} />
          </Paper>

          <Paper sx={{ p: 3, mb: 3 }}>
            <ComparisonCharts schedules={selectedSchedules} />
          </Paper>

          <BestScheduleCard schedules={selectedSchedules} />
        </Box>
      ) : (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            Select at least 2 schedules to start comparing.
          </Typography>
        </Paper>
      )}
    </Container>
  );
};
