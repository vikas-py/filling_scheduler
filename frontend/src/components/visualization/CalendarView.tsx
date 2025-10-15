import { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  ChevronLeft,
  ChevronRight,
  Today,
} from '@mui/icons-material';
import type { Activity } from '../../api/schedules';

interface CalendarViewProps {
  activities: Activity[];
  scheduleStartTime?: string;
}

type ViewMode = 'day' | 'week' | 'month';

interface CalendarDay {
  date: Date;
  activities: Activity[];
  isCurrentMonth: boolean;
}

export const CalendarView = ({ activities, scheduleStartTime }: CalendarViewProps) => {
  const [currentDate, setCurrentDate] = useState<Date>(
    scheduleStartTime ? new Date(scheduleStartTime) : new Date()
  );
  const [viewMode, setViewMode] = useState<ViewMode>('week');

  // Helper to get actual datetime from activity
  const getActualDateTime = (hourOffset: number): Date => {
    if (scheduleStartTime) {
      const startDate = new Date(scheduleStartTime);
      return new Date(startDate.getTime() + hourOffset * 60 * 60 * 1000);
    }
    // If no start time, use relative hours from current date
    const now = new Date();
    return new Date(now.getTime() + hourOffset * 60 * 60 * 1000);
  };

  // Format time
  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
  };

  // Format date
  const formatDate = (date: Date): string => {
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  // Get color for activity type
  const getActivityColor = (type: string): string => {
    switch (type) {
      case 'LOT':
        return '#2196f3';
      case 'CLEAN':
        return '#ff9800';
      case 'IDLE':
        return '#9e9e9e';
      default:
        return '#757575';
    }
  };

  // Get filler color
  const getFillerColor = (filler: number): string => {
    const colors = ['#e57373', '#81c784', '#64b5f6', '#ffb74d', '#ba68c8', '#4db6ac'];
    return colors[filler % colors.length];
  };

  // Navigation handlers
  const goToPrevious = () => {
    const newDate = new Date(currentDate);
    if (viewMode === 'day') {
      newDate.setDate(newDate.getDate() - 1);
    } else if (viewMode === 'week') {
      newDate.setDate(newDate.getDate() - 7);
    } else {
      newDate.setMonth(newDate.getMonth() - 1);
    }
    setCurrentDate(newDate);
  };

  const goToNext = () => {
    const newDate = new Date(currentDate);
    if (viewMode === 'day') {
      newDate.setDate(newDate.getDate() + 1);
    } else if (viewMode === 'week') {
      newDate.setDate(newDate.getDate() + 7);
    } else {
      newDate.setMonth(newDate.getMonth() + 1);
    }
    setCurrentDate(newDate);
  };

  const goToToday = () => {
    setCurrentDate(scheduleStartTime ? new Date(scheduleStartTime) : new Date());
  };

  // Get calendar data based on view mode
  const calendarData = useMemo(() => {
    const result: CalendarDay[] = [];

    if (viewMode === 'day') {
      // Single day view
      const dayStart = new Date(currentDate);
      dayStart.setHours(0, 0, 0, 0);
      const dayEnd = new Date(currentDate);
      dayEnd.setHours(23, 59, 59, 999);

      const dayActivities = activities.filter((activity) => {
        const actStart = getActualDateTime(activity.start_time);
        const actEnd = getActualDateTime(activity.end_time);
        return (
          (actStart >= dayStart && actStart <= dayEnd) ||
          (actEnd >= dayStart && actEnd <= dayEnd) ||
          (actStart <= dayStart && actEnd >= dayEnd)
        );
      });

      result.push({
        date: dayStart,
        activities: dayActivities,
        isCurrentMonth: true,
      });
    } else if (viewMode === 'week') {
      // Week view (7 days)
      const weekStart = new Date(currentDate);
      weekStart.setDate(weekStart.getDate() - weekStart.getDay()); // Start from Sunday
      weekStart.setHours(0, 0, 0, 0);

      for (let i = 0; i < 7; i++) {
        const dayDate = new Date(weekStart);
        dayDate.setDate(weekStart.getDate() + i);
        const dayEnd = new Date(dayDate);
        dayEnd.setHours(23, 59, 59, 999);

        const dayActivities = activities.filter((activity) => {
          const actStart = getActualDateTime(activity.start_time);
          const actEnd = getActualDateTime(activity.end_time);
          return (
            (actStart >= dayDate && actStart <= dayEnd) ||
            (actEnd >= dayDate && actEnd <= dayEnd) ||
            (actStart <= dayDate && actEnd >= dayEnd)
          );
        });

        result.push({
          date: dayDate,
          activities: dayActivities,
          isCurrentMonth: true,
        });
      }
    } else {
      // Month view
      const monthStart = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
      const monthEnd = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

      // Get first day of the calendar (may be from previous month)
      const calendarStart = new Date(monthStart);
      calendarStart.setDate(calendarStart.getDate() - calendarStart.getDay());

      // Get all days in the calendar grid (usually 35 or 42 days)
      const calendarDays = 35;
      for (let i = 0; i < calendarDays; i++) {
        const dayDate = new Date(calendarStart);
        dayDate.setDate(calendarStart.getDate() + i);
        const dayEnd = new Date(dayDate);
        dayEnd.setHours(23, 59, 59, 999);

        const dayActivities = activities.filter((activity) => {
          const actStart = getActualDateTime(activity.start_time);
          const actEnd = getActualDateTime(activity.end_time);
          return (
            (actStart >= dayDate && actStart <= dayEnd) ||
            (actEnd >= dayDate && actEnd <= dayEnd) ||
            (actStart <= dayDate && actEnd >= dayEnd)
          );
        });

        result.push({
          date: dayDate,
          activities: dayActivities,
          isCurrentMonth: dayDate >= monthStart && dayDate <= monthEnd,
        });
      }
    }

    return result;
  }, [activities, currentDate, viewMode, scheduleStartTime]);

  // Render day view
  const renderDayView = () => {
    const day = calendarData[0];
    const hours = Array.from({ length: 24 }, (_, i) => i);

    return (
      <Box>
        <Typography variant="h6" sx={{ mb: 2, textAlign: 'center' }}>
          {formatDate(day.date)}
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          {hours.map((hour) => {
            const hourStart = new Date(day.date);
            hourStart.setHours(hour, 0, 0, 0);
            const hourEnd = new Date(day.date);
            hourEnd.setHours(hour, 59, 59, 999);

            const hourActivities = day.activities.filter((activity) => {
              const actStart = getActualDateTime(activity.start_time);
              const actEnd = getActualDateTime(activity.end_time);
              return (
                (actStart >= hourStart && actStart <= hourEnd) ||
                (actEnd >= hourStart && actEnd <= hourEnd) ||
                (actStart <= hourStart && actEnd >= hourEnd)
              );
            });

            return (
              <Box
                key={hour}
                sx={{
                  display: 'flex',
                  minHeight: 60,
                  borderBottom: '1px solid #e0e0e0',
                }}
              >
                <Box
                  sx={{
                    width: 80,
                    p: 1,
                    bgcolor: '#f5f5f5',
                    borderRight: '1px solid #e0e0e0',
                  }}
                >
                  <Typography variant="caption" color="text.secondary">
                    {hour.toString().padStart(2, '0')}:00
                  </Typography>
                </Box>
                <Box sx={{ flex: 1, p: 1, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                  {hourActivities.map((activity) => (
                    <Tooltip
                      key={activity.id}
                      title={
                        <Box>
                          <Typography variant="caption" fontWeight="bold">
                            {activity.type === 'LOT' ? `Lot ${activity.lot_id}` : activity.type}
                          </Typography>
                          <Typography variant="caption" display="block">
                            Filler {activity.filler_id + 1}
                          </Typography>
                          <Typography variant="caption" display="block">
                            {formatTime(getActualDateTime(activity.start_time))} -{' '}
                            {formatTime(getActualDateTime(activity.end_time))}
                          </Typography>
                          <Typography variant="caption" display="block">
                            Duration: {(activity.end_time - activity.start_time).toFixed(2)}h
                          </Typography>
                        </Box>
                      }
                    >
                      <Box
                        sx={{
                          p: 0.5,
                          bgcolor: getActivityColor(activity.type),
                          color: 'white',
                          borderRadius: 1,
                          fontSize: '0.75rem',
                          cursor: 'pointer',
                          borderLeft: `4px solid ${getFillerColor(activity.filler_id)}`,
                          '&:hover': {
                            opacity: 0.8,
                          },
                        }}
                      >
                        <Typography variant="caption" fontWeight="bold" noWrap>
                          {activity.type === 'LOT' ? `Lot ${activity.lot_id}` : activity.type} (F
                          {activity.filler_id + 1})
                        </Typography>
                      </Box>
                    </Tooltip>
                  ))}
                </Box>
              </Box>
            );
          })}
        </Box>
      </Box>
    );
  };

  // Render week view
  const renderWeekView = () => {
    const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    return (
      <Box>
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 1 }}>
          {calendarData.map((day, index) => (
            <Box key={index}>
              <Paper
                elevation={0}
                sx={{
                  p: 1,
                  minHeight: 200,
                  bgcolor: '#f5f5f5',
                  border: '1px solid #e0e0e0',
                }}
              >
                <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                  {weekDays[day.date.getDay()]}
                </Typography>
                <Typography variant="h6" gutterBottom>
                  {day.date.getDate()}
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5, maxHeight: 150, overflow: 'auto' }}>
                  {day.activities.slice(0, 10).map((activity) => (
                    <Tooltip
                      key={activity.id}
                      title={
                        <Box>
                          <Typography variant="caption" fontWeight="bold">
                            {activity.type === 'LOT' ? `Lot ${activity.lot_id}` : activity.type}
                          </Typography>
                          <Typography variant="caption" display="block">
                            Filler {activity.filler_id + 1}
                          </Typography>
                          <Typography variant="caption" display="block">
                            {formatTime(getActualDateTime(activity.start_time))} -{' '}
                            {formatTime(getActualDateTime(activity.end_time))}
                          </Typography>
                        </Box>
                      }
                    >
                      <Chip
                        label={activity.type === 'LOT' ? `L${activity.lot_id}` : activity.type}
                        size="small"
                        sx={{
                          bgcolor: getActivityColor(activity.type),
                          color: 'white',
                          fontSize: '0.7rem',
                          height: 20,
                          borderLeft: `3px solid ${getFillerColor(activity.filler_id)}`,
                          borderRadius: 1,
                        }}
                      />
                    </Tooltip>
                  ))}
                  {day.activities.length > 10 && (
                    <Typography variant="caption" color="text.secondary">
                      +{day.activities.length - 10} more
                    </Typography>
                  )}
                </Box>
              </Paper>
            </Box>
          ))}
        </Box>
      </Box>
    );
  };

  // Render month view
  const renderMonthView = () => {
    const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const weeks: CalendarDay[][] = [];
    for (let i = 0; i < calendarData.length; i += 7) {
      weeks.push(calendarData.slice(i, i + 7));
    }

    return (
      <Box>
        {/* Week day headers */}
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 1, mb: 1 }}>
          {weekDays.map((day) => (
            <Typography key={day} variant="subtitle2" fontWeight="bold" textAlign="center">
              {day}
            </Typography>
          ))}
        </Box>

        {/* Calendar grid */}
        {weeks.map((week, weekIndex) => (
          <Box key={weekIndex} sx={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 1, mb: 1 }}>
            {week.map((day, dayIndex) => (
              <Paper
                key={dayIndex}
                elevation={0}
                sx={{
                  p: 1,
                  minHeight: 120,
                  bgcolor: day.isCurrentMonth ? 'white' : '#fafafa',
                  border: '1px solid #e0e0e0',
                  opacity: day.isCurrentMonth ? 1 : 0.6,
                }}
              >
                <Typography
                  variant="body2"
                  fontWeight={day.isCurrentMonth ? 'bold' : 'normal'}
                  gutterBottom
                >
                  {day.date.getDate()}
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.25 }}>
                  {day.activities.slice(0, 3).map((activity) => (
                    <Tooltip
                      key={activity.id}
                      title={
                        <Box>
                          <Typography variant="caption" fontWeight="bold">
                            {activity.type === 'LOT' ? `Lot ${activity.lot_id}` : activity.type}
                          </Typography>
                          <Typography variant="caption" display="block">
                            Filler {activity.filler_id + 1}
                          </Typography>
                          <Typography variant="caption" display="block">
                            {formatTime(getActualDateTime(activity.start_time))}
                          </Typography>
                        </Box>
                      }
                    >
                      <Box
                        sx={{
                          bgcolor: getActivityColor(activity.type),
                          color: 'white',
                          fontSize: '0.65rem',
                          px: 0.5,
                          py: 0.25,
                          borderRadius: 0.5,
                          cursor: 'pointer',
                          borderLeft: `2px solid ${getFillerColor(activity.filler_id)}`,
                          '&:hover': {
                            opacity: 0.8,
                          },
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {activity.type === 'LOT' ? `L${activity.lot_id}` : activity.type}
                      </Box>
                    </Tooltip>
                  ))}
                  {day.activities.length > 3 && (
                    <Typography variant="caption" color="text.secondary" fontSize="0.65rem">
                      +{day.activities.length - 3}
                    </Typography>
                  )}
                </Box>
              </Paper>
            ))}
          </Box>
        ))}
      </Box>
    );
  };

  // Get header title
  const getHeaderTitle = (): string => {
    if (viewMode === 'day') {
      return formatDate(currentDate);
    } else if (viewMode === 'week') {
      const weekStart = new Date(currentDate);
      weekStart.setDate(weekStart.getDate() - weekStart.getDay());
      const weekEnd = new Date(weekStart);
      weekEnd.setDate(weekStart.getDate() + 6);
      return `${formatDate(weekStart)} - ${formatDate(weekEnd)}`;
    } else {
      return currentDate.toLocaleDateString('en-US', {
        month: 'long',
        year: 'numeric',
      });
    }
  };

  return (
    <Box>
      {/* Header with navigation */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton onClick={goToPrevious} size="small">
            <ChevronLeft />
          </IconButton>
          <Typography variant="h6" sx={{ minWidth: 250, textAlign: 'center' }}>
            {getHeaderTitle()}
          </Typography>
          <IconButton onClick={goToNext} size="small">
            <ChevronRight />
          </IconButton>
          <IconButton onClick={goToToday} size="small" title="Go to start">
            <Today />
          </IconButton>
        </Box>

        <ToggleButtonGroup
          value={viewMode}
          exclusive
          onChange={(_, newMode) => newMode && setViewMode(newMode)}
          size="small"
        >
          <ToggleButton value="day">Day</ToggleButton>
          <ToggleButton value="week">Week</ToggleButton>
          <ToggleButton value="month">Month</ToggleButton>
        </ToggleButtonGroup>
      </Box>

      {/* Legend */}
      <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 16, height: 16, bgcolor: '#2196f3', borderRadius: 0.5 }} />
          <Typography variant="caption">LOT</Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 16, height: 16, bgcolor: '#ff9800', borderRadius: 0.5 }} />
          <Typography variant="caption">CLEAN</Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ width: 16, height: 16, bgcolor: '#9e9e9e', borderRadius: 0.5 }} />
          <Typography variant="caption">IDLE</Typography>
        </Box>
      </Box>

      {/* Calendar content */}
      <Box sx={{ overflowX: 'auto' }}>
        {viewMode === 'day' && renderDayView()}
        {viewMode === 'week' && renderWeekView()}
        {viewMode === 'month' && renderMonthView()}
      </Box>

      {/* Summary */}
      <Box sx={{ mt: 3, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
        <Typography variant="body2" color="text.secondary">
          Showing {activities.length} activities across schedule
          {scheduleStartTime && ` (Starting ${formatDate(new Date(scheduleStartTime))})`}
        </Typography>
      </Box>
    </Box>
  );
};
