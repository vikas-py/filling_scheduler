import { Box, LinearProgress, Typography, Paper } from '@mui/material';

export type ProgressStatus = 'idle' | 'uploading' | 'parsing' | 'scheduling' | 'completed' | 'error';

interface ProgressIndicatorProps {
  status: ProgressStatus;
  progress?: number;
  message?: string;
  error?: string;
}

const statusMessages: Record<ProgressStatus, string> = {
  idle: 'Ready to start',
  uploading: 'Uploading CSV file...',
  parsing: 'Parsing data and validating...',
  scheduling: 'Creating schedule...',
  completed: 'Schedule created successfully!',
  error: 'An error occurred',
};

const getStatusColor = (status: ProgressStatus): 'inherit' | 'primary' | 'success' | 'error' => {
  switch (status) {
    case 'completed':
      return 'success';
    case 'error':
      return 'error';
    case 'idle':
      return 'inherit';
    default:
      return 'primary';
  }
};

export const ProgressIndicator = ({ status, progress, message, error }: ProgressIndicatorProps) => {
  const displayMessage = error || message || statusMessages[status];
  const showProgress = status !== 'idle' && status !== 'completed' && status !== 'error';

  return (
    <Paper sx={{ p: 3 }}>
      <Box>
        <Typography variant="h6" gutterBottom>
          {status === 'completed' ? '✓ ' : status === 'error' ? '✗ ' : ''}
          {statusMessages[status]}
        </Typography>

        {showProgress && (
          <LinearProgress
            variant={progress !== undefined ? 'determinate' : 'indeterminate'}
            value={progress}
            color={getStatusColor(status)}
            sx={{ my: 2 }}
          />
        )}

        {displayMessage && (
          <Typography
            variant="body2"
            color={status === 'error' ? 'error' : 'text.secondary'}
            sx={{ mt: 1 }}
          >
            {displayMessage}
          </Typography>
        )}

        {status === 'completed' && !error && (
          <Typography variant="body2" color="success.main" sx={{ mt: 2 }}>
            Your schedule has been created and is ready to view.
          </Typography>
        )}
      </Box>
    </Paper>
  );
};
