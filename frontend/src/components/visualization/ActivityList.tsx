import { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TableSortLabel,
  TextField,
  InputAdornment,
  Chip,
} from '@mui/material';
import { Search } from '@mui/icons-material';

interface Activity {
  id: string;
  lot_id: string;
  filler_id: number;
  start_time: number;
  end_time: number;
  duration: number;
  num_units?: number;
}

interface ActivityListProps {
  activities: Activity[];
}

type SortField = 'lot_id' | 'filler_id' | 'start_time' | 'end_time' | 'duration';
type SortOrder = 'asc' | 'desc';

export const ActivityList = ({ activities }: ActivityListProps) => {
  const [search, setSearch] = useState('');
  const [sortField, setSortField] = useState<SortField>('start_time');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  // Filter and sort activities
  const filteredAndSortedActivities = useMemo(() => {
    let result = [...activities];

    // Filter by search
    if (search) {
      const searchLower = search.toLowerCase();
      result = result.filter((activity) =>
        activity.lot_id.toLowerCase().includes(searchLower) ||
        activity.id.toLowerCase().includes(searchLower)
      );
    }

    // Sort
    result.sort((a, b) => {
      let aValue = a[sortField];
      let bValue = b[sortField];

      if (typeof aValue === 'string' && typeof bValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [activities, search, sortField, sortOrder]);

  if (!activities || activities.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          No activities to display. Schedule may still be processing.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Activity List ({filteredAndSortedActivities.length} of {activities.length})
        </Typography>
        <TextField
          size="small"
          placeholder="Search by lot ID..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search />
              </InputAdornment>
            ),
          }}
          sx={{ width: 300 }}
        />
      </Box>

      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>
                <TableSortLabel
                  active={sortField === 'lot_id'}
                  direction={sortField === 'lot_id' ? sortOrder : 'asc'}
                  onClick={() => handleSort('lot_id')}
                >
                  Lot ID
                </TableSortLabel>
              </TableCell>
              <TableCell>
                <TableSortLabel
                  active={sortField === 'filler_id'}
                  direction={sortField === 'filler_id' ? sortOrder : 'asc'}
                  onClick={() => handleSort('filler_id')}
                >
                  Filler
                </TableSortLabel>
              </TableCell>
              <TableCell align="right">
                <TableSortLabel
                  active={sortField === 'start_time'}
                  direction={sortField === 'start_time' ? sortOrder : 'asc'}
                  onClick={() => handleSort('start_time')}
                >
                  Start Time
                </TableSortLabel>
              </TableCell>
              <TableCell align="right">
                <TableSortLabel
                  active={sortField === 'end_time'}
                  direction={sortField === 'end_time' ? sortOrder : 'asc'}
                  onClick={() => handleSort('end_time')}
                >
                  End Time
                </TableSortLabel>
              </TableCell>
              <TableCell align="right">
                <TableSortLabel
                  active={sortField === 'duration'}
                  direction={sortField === 'duration' ? sortOrder : 'asc'}
                  onClick={() => handleSort('duration')}
                >
                  Duration
                </TableSortLabel>
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredAndSortedActivities.map((activity) => (
              <TableRow key={activity.id} hover>
                <TableCell>
                  <Typography variant="body2" fontWeight="medium">
                    {activity.lot_id}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={`Filler ${activity.filler_id + 1}`}
                    size="small"
                    color="primary"
                  />
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2">
                    {activity.start_time.toFixed(2)}h
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2">
                    {activity.end_time.toFixed(2)}h
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2" fontWeight="medium">
                    {activity.duration.toFixed(2)}h
                  </Typography>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {filteredAndSortedActivities.length === 0 && search && (
        <Paper sx={{ p: 2, mt: 2, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            No activities found matching "{search}"
          </Typography>
        </Paper>
      )}
    </Box>
  );
};
