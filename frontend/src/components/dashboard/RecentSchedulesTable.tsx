import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Typography,
  Box,
  Pagination,
  Stack,
} from '@mui/material';
import { Visibility as VisibilityIcon, Delete as DeleteIcon } from '@mui/icons-material';
import { format } from 'date-fns';
import type { Schedule } from '@/api/schedules';

const getStatusColor = (status: Schedule['status']) => {
  switch (status) {
    case 'completed':
      return 'success';
    case 'running':
      return 'info';
    case 'pending':
      return 'warning';
    case 'failed':
      return 'error';
    default:
      return 'default';
  }
};

interface RecentSchedulesTableProps {
  schedules?: Schedule[];
  onView?: (id: number) => void;
  onDelete?: (id: number) => void;
  page?: number;
  pageSize?: number;
  total?: number;
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
}

export const RecentSchedulesTable = ({
  schedules = [],
  onView,
  onDelete,
  page = 1,
  pageSize = 5,
  total = 0,
  onPageChange,
}: RecentSchedulesTableProps) => {
  const handleView = (id: number) => {
    if (onView) {
      onView(id);
    } else {
      console.log('View schedule:', id);
    }
  };

  const handleDelete = (id: number) => {
    if (onDelete) {
      onDelete(id);
    } else {
      console.log('Delete schedule:', id);
    }
  };

  const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
    if (onPageChange) {
      onPageChange(value);
    }
  };

  // Pagination calculations
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const startIndex = (page - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  // Schedules are already paginated from backend, so just use as-is
  const paginatedSchedules = schedules;

  if (!schedules || schedules.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No schedules found. Create your first schedule to get started!
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h6">Recent Schedules</Typography>
      </Box>
      <TableContainer sx={{ maxHeight: 440 }}>
        <Table stickyHeader>
          <TableHead>
            <TableRow>
              <TableCell>Schedule Name</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Strategy</TableCell>
              <TableCell>Lots</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {paginatedSchedules.map((schedule) => (
              <TableRow key={schedule.id} hover>
                <TableCell>
                  <Typography variant="body2" fontWeight={500}>
                    {schedule.name}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={schedule.status.toUpperCase()}
                    color={getStatusColor(schedule.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2">{schedule.strategy}</Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2">{schedule.num_lots}</Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="body2" color="text.secondary">
                    {format(new Date(schedule.created_at), 'MMM dd, yyyy HH:mm')}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <IconButton
                    size="small"
                    color="primary"
                    onClick={() => handleView(schedule.id)}
                    title="View details"
                  >
                    <VisibilityIcon fontSize="small" />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDelete(schedule.id)}
                    title="Delete schedule"
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination Footer */}
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Stack direction="row" spacing={2} alignItems="center" justifyContent="space-between">
          <Typography variant="body2" color="text.secondary">
            Showing {startIndex + 1}-{Math.min(endIndex, total)} of {total} schedules
          </Typography>
          <Pagination
            count={totalPages}
            page={page}
            onChange={handlePageChange}
            color="primary"
            showFirstButton
            showLastButton
          />
        </Stack>
      </Box>
    </Paper>
  );
};
