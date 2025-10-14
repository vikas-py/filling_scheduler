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
import { useState } from 'react';
import type { Schedule } from '@/api/schedules';

// Mock data for development (matches API format)
const mockSchedules: Schedule[] = [
  {
    id: 1,
    name: 'Production Run Q4 2025',
    status: 'completed',
    strategy: 'LPT',
    config: {},
    created_at: '2025-10-13T10:30:00',
    updated_at: '2025-10-13T14:30:00',
    num_lots: 45,
  },
  {
    id: 2,
    name: 'Emergency Order Batch',
    status: 'running',
    strategy: 'SPT',
    config: {},
    created_at: '2025-10-14T08:15:00',
    updated_at: '2025-10-14T08:15:00',
    num_lots: 23,
  },
  {
    id: 3,
    name: 'Standard Production',
    status: 'pending',
    strategy: 'CFS',
    config: {},
    created_at: '2025-10-14T09:00:00',
    updated_at: '2025-10-14T09:00:00',
    num_lots: 67,
  },
  {
    id: 4,
    name: 'Optimization Test',
    status: 'failed',
    strategy: 'MILP',
    config: {},
    created_at: '2025-10-12T14:20:00',
    updated_at: '2025-10-12T14:25:00',
    num_lots: 12,
  },
  {
    id: 5,
    name: 'Weekly Production Schedule',
    status: 'completed',
    strategy: 'Hybrid',
    config: {},
    created_at: '2025-10-11T11:45:00',
    updated_at: '2025-10-11T15:30:00',
    num_lots: 89,
  },
];

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
  rowsPerPage?: number;
}

export const RecentSchedulesTable = ({
  schedules = mockSchedules,
  onView,
  onDelete,
  rowsPerPage = 5,
}: RecentSchedulesTableProps) => {
  const [page, setPage] = useState(1);

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
    setPage(value);
  };

  if (!schedules || schedules.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No schedules found. Create your first schedule to get started!
        </Typography>
      </Paper>
    );
  }

  // Pagination calculations
  const totalPages = Math.ceil(schedules.length / rowsPerPage);
  const startIndex = (page - 1) * rowsPerPage;
  const endIndex = startIndex + rowsPerPage;
  const paginatedSchedules = schedules.slice(startIndex, endIndex);

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
            Showing {startIndex + 1}-{Math.min(endIndex, schedules.length)} of {schedules.length} schedules
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
