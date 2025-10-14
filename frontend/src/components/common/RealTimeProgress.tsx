import { Box, LinearProgress, Typography, Paper, Chip } from '@mui/material';
import {
  Schedule as ScheduleIcon,
  CheckCircle as CompletedIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

interface RealTimeProgressProps {
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress?: number;
  message?: string;
  eta?: string;
  scheduleName?: string;
}

export const RealTimeProgress = ({
  status,
  progress = 0,
  message,
  eta,
  scheduleName,
}: RealTimeProgressProps) => {
  const getChipColor = (): 'primary' | 'success' | 'error' | 'default' => {
    switch (status) {
      case 'running':
        return 'primary';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getProgressColor = (): 'primary' | 'success' | 'error' => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'primary';
    }
  };

  const getBorderColor = () => {
    switch (status) {
      case 'running':
        return 'primary.main';
      case 'completed':
        return 'success.main';
      case 'failed':
        return 'error.main';
      default:
        return 'grey.300';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'running':
        return <ScheduleIcon />;
      case 'completed':
        return <CompletedIcon />;
      case 'failed':
        return <ErrorIcon />;
      default:
        return <ScheduleIcon />;
    }
  };

  const getStatusLabel = () => {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'running':
        return 'Running';
      case 'completed':
        return 'Completed';
      case 'failed':
        return 'Failed';
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        borderLeft: 4,
        borderColor: getBorderColor(),
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {getStatusIcon()}
          <Typography variant="h6" component="div">
            {scheduleName || 'Schedule'}
          </Typography>
        </Box>
        <Chip
          label={getStatusLabel()}
          color={getChipColor()}
          size="small"
          sx={{ fontWeight: 'bold' }}
        />
      </Box>

      {status === 'running' && (
        <>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Box sx={{ width: '100%', mr: 1 }}>
              <LinearProgress
                variant="determinate"
                value={progress}
                color={getProgressColor()}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ minWidth: 50 }}>
              {`${Math.round(progress)}%`}
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {message && (
              <Typography variant="body2" color="text.secondary">
                {message}
              </Typography>
            )}
            {eta && (
              <Typography variant="caption" color="text.secondary">
                ETA: {eta}
              </Typography>
            )}
          </Box>
        </>
      )}

      {status === 'completed' && (
        <Typography variant="body2" color="success.main">
          {message || 'Schedule generation completed successfully'}
        </Typography>
      )}

      {status === 'failed' && (
        <Typography variant="body2" color="error.main">
          {message || 'Schedule generation failed'}
        </Typography>
      )}
    </Paper>
  );
};
