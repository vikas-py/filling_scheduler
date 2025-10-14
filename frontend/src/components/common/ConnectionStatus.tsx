import { Box, Chip, Tooltip, CircularProgress } from '@mui/material';
import {
  CheckCircle as ConnectedIcon,
  Error as ErrorIcon,
  CloudOff as DisconnectedIcon,
} from '@mui/icons-material';
import type { WebSocketStatus } from '@/hooks/useWebSocket';

interface ConnectionStatusProps {
  status: WebSocketStatus;
  onReconnect?: () => void;
}

export const ConnectionStatus = ({ status, onReconnect }: ConnectionStatusProps) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'connected':
        return {
          label: 'Connected',
          color: 'success' as const,
          icon: <ConnectedIcon sx={{ fontSize: 16 }} />,
          tooltip: 'Real-time updates active',
        };
      case 'connecting':
        return {
          label: 'Connecting',
          color: 'warning' as const,
          icon: <CircularProgress size={14} />,
          tooltip: 'Establishing connection...',
        };
      case 'disconnected':
        return {
          label: 'Offline',
          color: 'default' as const,
          icon: <DisconnectedIcon sx={{ fontSize: 16 }} />,
          tooltip: 'Real-time updates unavailable',
        };
      case 'error':
        return {
          label: 'Error',
          color: 'error' as const,
          icon: <ErrorIcon sx={{ fontSize: 16 }} />,
          tooltip: 'Connection error. Click to retry',
        };
    }
  };

  const config = getStatusConfig();

  return (
    <Tooltip title={config.tooltip}>
      <Box sx={{ display: 'inline-flex' }}>
        <Chip
          label={config.label}
          color={config.color}
          size="small"
          icon={config.icon}
          onClick={status === 'error' ? onReconnect : undefined}
          sx={{
            cursor: status === 'error' ? 'pointer' : 'default',
            '& .MuiChip-icon': {
              marginLeft: '8px',
            },
          }}
        />
      </Box>
    </Tooltip>
  );
};
