import { Box, TextField, Select, MenuItem, FormControl, InputLabel, Button, Stack } from '@mui/material';
import { Search as SearchIcon, FilterList as FilterIcon } from '@mui/icons-material';
import { useState } from 'react';

export interface ScheduleFilters {
  search: string;
  status: string;
  strategy: string;
}

interface ScheduleFiltersProps {
  onFilterChange?: (filters: ScheduleFilters) => void;
}

export const ScheduleFiltersBar = ({ onFilterChange }: ScheduleFiltersProps) => {
  const [filters, setFilters] = useState<ScheduleFilters>({
    search: '',
    status: 'all',
    strategy: 'all',
  });

  const handleSearchChange = (value: string) => {
    const newFilters = { ...filters, search: value };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  const handleStatusChange = (value: string) => {
    const newFilters = { ...filters, status: value };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  const handleStrategyChange = (value: string) => {
    const newFilters = { ...filters, strategy: value };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  const handleClearFilters = () => {
    const clearedFilters = { search: '', status: 'all', strategy: 'all' };
    setFilters(clearedFilters);
    onFilterChange?.(clearedFilters);
  };

  return (
    <Box sx={{ mb: 3, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
      <Stack direction="row" spacing={2} alignItems="center" flexWrap="wrap" useFlexGap>
        {/* Search Input */}
        <TextField
          size="small"
          placeholder="Search schedules..."
          value={filters.search}
          onChange={(e) => handleSearchChange(e.target.value)}
          sx={{ minWidth: 250, flexGrow: 1 }}
          InputProps={{
            startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
          }}
        />

        {/* Status Filter */}
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel id="status-filter-label">Status</InputLabel>
          <Select
            labelId="status-filter-label"
            value={filters.status}
            label="Status"
            onChange={(e) => handleStatusChange(e.target.value)}
          >
            <MenuItem value="all">All Statuses</MenuItem>
            <MenuItem value="pending">Pending</MenuItem>
            <MenuItem value="running">Running</MenuItem>
            <MenuItem value="completed">Completed</MenuItem>
            <MenuItem value="failed">Failed</MenuItem>
          </Select>
        </FormControl>

        {/* Strategy Filter */}
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel id="strategy-filter-label">Strategy</InputLabel>
          <Select
            labelId="strategy-filter-label"
            value={filters.strategy}
            label="Strategy"
            onChange={(e) => handleStrategyChange(e.target.value)}
          >
            <MenuItem value="all">All Strategies</MenuItem>
            <MenuItem value="LPT">LPT</MenuItem>
            <MenuItem value="SPT">SPT</MenuItem>
            <MenuItem value="CFS">CFS</MenuItem>
            <MenuItem value="Hybrid">Hybrid</MenuItem>
            <MenuItem value="MILP">MILP</MenuItem>
          </Select>
        </FormControl>

        {/* Clear Filters Button */}
        <Button
          variant="outlined"
          size="small"
          startIcon={<FilterIcon />}
          onClick={handleClearFilters}
        >
          Clear Filters
        </Button>
      </Stack>
    </Box>
  );
};
