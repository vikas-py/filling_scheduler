import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TablePagination,
  TextField,
  Button,
  CircularProgress,
} from '@mui/material';
import { getSchedules } from '../api/schedules';
import type { Schedule } from '../api/schedules';

export const SchedulesList = () => {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await getSchedules(page + 1, rowsPerPage, { search });
        setSchedules(response.schedules);
        setTotal(response.total);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [page, rowsPerPage, search]);

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Schedules
      </Typography>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            label="Search"
            value={search}
            onChange={e => setSearch(e.target.value)}
            size="small"
          />
          <Button variant="contained" onClick={() => setPage(0)}>
            Search
          </Button>
        </Box>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
            <CircularProgress />
          </Box>
        ) : (
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Strategy</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Lots</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {schedules.map(sch => (
                <TableRow key={sch.id}>
                  <TableCell>{sch.name}</TableCell>
                  <TableCell>{sch.status}</TableCell>
                  <TableCell>{sch.strategy}</TableCell>
                  <TableCell>{new Date(sch.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>{sch.num_lots}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
        <TablePagination
          component="div"
          count={total}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={e => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </Paper>
    </Container>
  );
};
