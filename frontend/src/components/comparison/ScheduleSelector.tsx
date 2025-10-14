import { Box, Checkbox, FormControlLabel, Stack, Chip, Typography, Paper } from '@mui/material';
import { format } from 'date-fns';
import type { Schedule } from '../../api/schedules';

interface ScheduleSelectorProps {
  schedules: Schedule[];
  selectedIds: number[];
  onSelectionChange: (ids: number[]) => void;
  maxSelection?: number;
}

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

export const ScheduleSelector = ({
  schedules,
  selectedIds,
  onSelectionChange,
  maxSelection = 4,
}: ScheduleSelectorProps) => {
  const handleToggle = (scheduleId: number) => {
    const currentIndex = selectedIds.indexOf(scheduleId);
    const newSelectedIds = [...selectedIds];

    if (currentIndex === -1) {
      // Add if not already selected and under max limit
      if (newSelectedIds.length < maxSelection) {
        newSelectedIds.push(scheduleId);
      }
    } else {
      // Remove if already selected
      newSelectedIds.splice(currentIndex, 1);
    }

    onSelectionChange(newSelectedIds);
  };

  const isDisabled = (scheduleId: number) => {
    return selectedIds.length >= maxSelection && !selectedIds.includes(scheduleId);
  };

  return (
    <Box>
      <Stack spacing={1}>
        {schedules.map((schedule) => {
          const isSelected = selectedIds.includes(schedule.id);
          const disabled = isDisabled(schedule.id);

          return (
            <Paper
              key={schedule.id}
              sx={{
                p: 2,
                borderLeft: isSelected ? 4 : 0,
                borderColor: 'primary.main',
                bgcolor: disabled ? 'action.disabledBackground' : 'background.paper',
                opacity: disabled ? 0.6 : 1,
                transition: 'all 0.2s',
                '&:hover': {
                  bgcolor: disabled ? 'action.disabledBackground' : 'action.hover',
                },
              }}
            >
              <FormControlLabel
                control={
                  <Checkbox
                    checked={isSelected}
                    onChange={() => handleToggle(schedule.id)}
                    disabled={disabled}
                  />
                }
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flex: 1 }}>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle1" fontWeight="medium">
                        {schedule.name}
                      </Typography>
                      {schedule.description && (
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                          {schedule.description}
                        </Typography>
                      )}
                      <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
                        <Chip
                          label={schedule.status.toUpperCase()}
                          size="small"
                          color={getStatusColor(schedule.status)}
                        />
                        <Chip label={schedule.strategy} size="small" variant="outlined" />
                        <Chip label={`${schedule.num_lots} lots`} size="small" variant="outlined" />
                        {schedule.total_time && (
                          <Chip
                            label={`${schedule.total_time.toFixed(2)}h`}
                            size="small"
                            variant="outlined"
                          />
                        )}
                      </Box>
                    </Box>
                    <Box sx={{ textAlign: 'right' }}>
                      <Typography variant="caption" color="text.secondary">
                        Created
                      </Typography>
                      <Typography variant="body2">
                        {format(new Date(schedule.created_at), 'MMM d, yyyy')}
                      </Typography>
                    </Box>
                  </Box>
                }
                sx={{ width: '100%', m: 0 }}
              />
            </Paper>
          );
        })}
      </Stack>

      {selectedIds.length >= maxSelection && (
        <Typography variant="caption" color="warning.main" sx={{ mt: 2, display: 'block' }}>
          Maximum {maxSelection} schedules can be selected for comparison.
        </Typography>
      )}
    </Box>
  );
};
