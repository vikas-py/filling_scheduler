import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Tabs,
  Tab,
  Button,
  Chip,
  IconButton,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  ArrowBack,
  Download,
  Delete,
  Refresh,
} from '@mui/icons-material';
import { getSchedule } from '../api/schedules';
import type { Schedule } from '../api/schedules';
import { GanttChart } from '../components/visualization/GanttChart';
import { ActivityList } from '../components/visualization/ActivityList';
import { ScheduleStats } from '../components/visualization/ScheduleStats';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = ({ children, value, index }: TabPanelProps) => {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
};

const getStatusColor = (status: string): 'default' | 'warning' | 'info' | 'success' | 'error' => {
  switch (status) {
    case 'pending':
      return 'default';
    case 'running':
      return 'info';
    case 'completed':
      return 'success';
    case 'failed':
      return 'error';
    default:
      return 'default';
  }
};

export const ScheduleDetail = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);

  const loadSchedule = async () => {
    if (!id) return;

    setLoading(true);
    setError(null);

    try {
      const data = await getSchedule(parseInt(id, 10));
      setSchedule(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load schedule');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSchedule();
  }, [id]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleDelete = async () => {
    if (!schedule || !window.confirm('Are you sure you want to delete this schedule?')) {
      return;
    }

    try {
      // TODO: Implement delete
      navigate('/schedules');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete schedule');
    }
  };

  const handleExport = (format: 'csv' | 'json' | 'png') => {
    // TODO: Implement export functionality
    console.log(`Exporting schedule ${id} as ${format}`);
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error || !schedule) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error || 'Schedule not found'}
        </Alert>
        <Button startIcon={<ArrowBack />} onClick={() => navigate('/schedules')}>
          Back to Schedules
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <IconButton onClick={() => navigate('/schedules')} sx={{ mr: 2 }}>
          <ArrowBack />
        </IconButton>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            {schedule.name}
          </Typography>
          {schedule.description && (
            <Typography variant="body2" color="text.secondary">
              {schedule.description}
            </Typography>
          )}
        </Box>
        <Chip
          label={schedule.status.toUpperCase()}
          color={getStatusColor(schedule.status)}
          sx={{ mr: 2 }}
        />
        <IconButton onClick={loadSchedule} title="Refresh">
          <Refresh />
        </IconButton>
        <IconButton onClick={handleDelete} color="error" title="Delete">
          <Delete />
        </IconButton>
      </Box>

      {/* Metadata */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
          <Box>
            <Typography variant="caption" color="text.secondary" display="block">
              Strategy
            </Typography>
            <Typography variant="body1" fontWeight="bold">
              {schedule.strategy}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary" display="block">
              Number of Lots
            </Typography>
            <Typography variant="body1" fontWeight="bold">
              {schedule.num_lots}
            </Typography>
          </Box>
          {schedule.total_time && (
            <Box>
              <Typography variant="caption" color="text.secondary" display="block">
                Total Time
              </Typography>
              <Typography variant="body1" fontWeight="bold">
                {schedule.total_time.toFixed(2)} hrs
              </Typography>
            </Box>
          )}
          <Box>
            <Typography variant="caption" color="text.secondary" display="block">
              Created
            </Typography>
            <Typography variant="body1" fontWeight="bold">
              {new Date(schedule.created_at).toLocaleDateString()}
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* Export buttons */}
      <Box sx={{ mb: 2, display: 'flex', gap: 1 }}>
        <Button
          startIcon={<Download />}
          size="small"
          onClick={() => handleExport('csv')}
        >
          Export CSV
        </Button>
        <Button
          startIcon={<Download />}
          size="small"
          onClick={() => handleExport('json')}
        >
          Export JSON
        </Button>
        <Button
          startIcon={<Download />}
          size="small"
          onClick={() => handleExport('png')}
        >
          Export Chart
        </Button>
      </Box>

      {/* Tabs */}
      <Paper>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Gantt Chart" />
          <Tab label="Activity List" />
          <Tab label="Statistics" />
          <Tab label="Configuration" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Box sx={{ p: 2 }}>
            {schedule.activities && schedule.activities.length > 0 ? (
              <GanttChart
                activities={schedule.activities}
                numFillers={(schedule.config.num_fillers as number) || 4}
              />
            ) : (
              <Typography variant="body1" color="text.secondary">
                No activities available. Schedule may still be processing.
              </Typography>
            )}
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ p: 2 }}>
            {schedule.activities && schedule.activities.length > 0 ? (
              <ActivityList activities={schedule.activities} />
            ) : (
              <Typography variant="body1" color="text.secondary">
                No activities available. Schedule may still be processing.
              </Typography>
            )}
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Box sx={{ p: 2 }}>
            {schedule.activities && schedule.activities.length > 0 ? (
              <ScheduleStats
                activities={schedule.activities}
                numFillers={(schedule.config.num_fillers as number) || 4}
                totalTime={schedule.total_time}
              />
            ) : (
              <Typography variant="body1" color="text.secondary">
                No statistics available. Schedule may still be processing.
              </Typography>
            )}
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Box sx={{ p: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Configuration
            </Typography>
            <pre style={{ backgroundColor: '#f5f5f5', padding: '16px', borderRadius: '4px', overflow: 'auto' }}>
              {JSON.stringify(schedule.config, null, 2)}
            </pre>
          </Box>
        </TabPanel>
      </Paper>
    </Container>
  );
};
