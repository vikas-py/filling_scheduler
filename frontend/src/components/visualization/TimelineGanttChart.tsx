import { useState, useMemo, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
  Chip,
  Stack,
  TextField,
  InputAdornment,
  IconButton,
  Tooltip,
  Button,
} from '@mui/material';
import {
  Search,
  Clear,
  ZoomIn,
  ZoomOut,
  FitScreen,
  Download,
} from '@mui/icons-material';

interface Activity {
  id: string;
  lot_id: string;
  filler_id: number;
  start_time: number;
  end_time: number;
  duration: number;
  kind?: string; // 'FILL', 'CLEAN', 'CHANGEOVER'
  lot_type?: string;
  num_units?: number;
}

interface TimelineGanttChartProps {
  activities: Activity[];
  numFillers: number;
  makespan: number;
  scheduleStartTime?: string; // ISO datetime string when schedule starts
  onActivityClick?: (activity: Activity) => void;
}

type ZoomLevel = '1h' | '4h' | '8h' | '24h' | 'all';
type ActivityFilter = 'all' | 'FILL' | 'CLEAN' | 'CHANGEOVER';

// Color scheme for activity types
const ACTIVITY_COLORS: Record<string, string> = {
  FILL: '#1976d2',      // Blue
  CLEAN: '#ff9800',     // Orange
  CHANGEOVER: '#f44336', // Red
  default: '#757575',   // Gray
};

const ACTIVITY_LABELS: Record<string, string> = {
  FILL: 'Fill',
  CLEAN: 'Clean',
  CHANGEOVER: 'Changeover',
};

export const TimelineGanttChart = ({
  activities,
  numFillers,
  makespan,
  scheduleStartTime,
  onActivityClick,
}: TimelineGanttChartProps) => {
  const [zoomLevel, setZoomLevel] = useState<ZoomLevel>('all');
  const [filterType, setFilterType] = useState<ActivityFilter>('all');
  const [selectedLot, setSelectedLot] = useState<string | null>(null);
  const [hoveredActivity, setHoveredActivity] = useState<Activity | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [mousePosition, setMousePosition] = useState<{ x: number; y: number } | null>(null);
  const [customZoom, setCustomZoom] = useState<{ start: number; end: number } | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  // Helper functions for datetime conversion
  const getActualDateTime = (hoursOffset: number): Date | null => {
    if (!scheduleStartTime) return null;
    const startDate = new Date(scheduleStartTime);
    return new Date(startDate.getTime() + hoursOffset * 60 * 60 * 1000);
  };

  const formatDateTime = (date: Date): string => {
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };



  // Chart dimensions
  const width = 1200;
  const leftMargin = 150; // Task name column
  const rightMargin = 50;
  const topMargin = 80; // Header with dates and days
  const bottomMargin = 40;
  const activityBarHeight = 28; // Height of each activity bar
  const activitySpacing = 4; // Space between stacked activities
  const taskHeaderHeight = 35; // Height of task group header
  const taskPadding = 10; // Padding within task group

  // Group activities by filler (equipment)
  const activityGroups = useMemo(() => {
    const groups: { fillerId: number; activities: Activity[] }[] = [];
    for (let i = 1; i <= numFillers; i++) {
      const fillerActivities = activities.filter(a => a.filler_id === i);
      groups.push({ fillerId: i, activities: fillerActivities });
    }
    return groups;
  }, [activities, numFillers]);

  // Calculate heights for each task group
  const taskGroupHeights = useMemo(() => {
    return activityGroups.map(group => {
      // Each activity gets its own row (stacked vertically)
      const numActivities = group.activities.length;
      if (numActivities === 0) {
        return taskHeaderHeight + taskPadding * 2 + activityBarHeight; // Minimum height
      }
      return taskHeaderHeight + taskPadding + (numActivities * (activityBarHeight + activitySpacing)) + taskPadding;
    });
  }, [activityGroups, taskHeaderHeight, taskPadding, activityBarHeight, activitySpacing]);

  // Calculate cumulative Y positions for each task group
  const taskGroupYPositions = useMemo(() => {
    const positions: number[] = [topMargin];
    for (let i = 0; i < taskGroupHeights.length - 1; i++) {
      positions.push(positions[i] + taskGroupHeights[i]);
    }
    return positions;
  }, [taskGroupHeights, topMargin]);

  // Total chart height
  const height = topMargin + taskGroupHeights.reduce((sum, h) => sum + h, 0) + bottomMargin;

  // Calculate visible time range based on zoom level or custom zoom
  const visibleTimeRange = useMemo(() => {
    if (customZoom) {
      return customZoom;
    }
    if (zoomLevel === 'all') {
      return { start: 0, end: makespan };
    }
    const hours = parseInt(zoomLevel);
    return { start: 0, end: Math.min(hours, makespan) };
  }, [zoomLevel, makespan, customZoom]);

  // Filter activities
  const filteredActivities = useMemo(() => {
    let result = activities;

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (a) =>
          a.lot_id.toLowerCase().includes(query) ||
          a.id.toLowerCase().includes(query) ||
          (a.lot_type && a.lot_type.toLowerCase().includes(query))
      );
    }

    // Filter by activity type
    if (filterType !== 'all') {
      result = result.filter((a) => a.kind === filterType);
    }

    // Filter by visible time range
    result = result.filter(
      (a) =>
        a.end_time >= visibleTimeRange.start &&
        a.start_time <= visibleTimeRange.end
    );

    return result;
  }, [activities, filterType, visibleTimeRange, searchQuery]);

  // Time scale function
  const timeScale = (time: number) => {
    const chartWidth = width - leftMargin - rightMargin;
    const timeRange = visibleTimeRange.end - visibleTimeRange.start;
    return (
      leftMargin +
      ((time - visibleTimeRange.start) / timeRange) * chartWidth
    );
  };

  // Generate time markers
  const timeMarkers = useMemo(() => {
    const timeRange = visibleTimeRange.end - visibleTimeRange.start;
    let interval = 4; // Default 4 hours

    if (timeRange <= 8) {
      interval = 1;
    } else if (timeRange <= 24) {
      interval = 2;
    } else if (timeRange <= 48) {
      interval = 4;
    } else {
      interval = 8;
    }

    const markers: number[] = [];
    for (
      let t = Math.ceil(visibleTimeRange.start / interval) * interval;
      t <= visibleTimeRange.end;
      t += interval
    ) {
      markers.push(t);
    }
    return markers;
  }, [visibleTimeRange]);

  // Get activity color
  const getActivityColor = (activity: Activity): string => {
    if (activity.kind && activity.kind in ACTIVITY_COLORS) {
      return ACTIVITY_COLORS[activity.kind];
    }
    return ACTIVITY_COLORS.default;
  };

  // Handle activity click
  const handleActivityClick = (activity: Activity) => {
    setSelectedLot(activity.lot_id === selectedLot ? null : activity.lot_id);
    if (onActivityClick) {
      onActivityClick(activity);
    }
  };

  // Zoom controls
  const handleZoomIn = () => {
    const range = visibleTimeRange.end - visibleTimeRange.start;
    const center = (visibleTimeRange.start + visibleTimeRange.end) / 2;
    const newRange = range * 0.7; // Zoom in by 30%
    setCustomZoom({
      start: Math.max(0, center - newRange / 2),
      end: Math.min(makespan, center + newRange / 2),
    });
    setZoomLevel('all'); // Clear preset zoom
  };

  const handleZoomOut = () => {
    const range = visibleTimeRange.end - visibleTimeRange.start;
    const center = (visibleTimeRange.start + visibleTimeRange.end) / 2;
    const newRange = Math.min(range * 1.3, makespan); // Zoom out by 30%
    setCustomZoom({
      start: Math.max(0, center - newRange / 2),
      end: Math.min(makespan, center + newRange / 2),
    });
    setZoomLevel('all');
  };

  const handleResetZoom = () => {
    setCustomZoom(null);
    setZoomLevel('all');
  };

  // Export as image
  const handleExportImage = () => {
    if (!svgRef.current) return;

    const svg = svgRef.current;
    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(svg);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    canvas.width = width * 2; // Higher resolution
    canvas.height = height * 2;

    img.onload = () => {
      ctx?.scale(2, 2);
      ctx?.drawImage(img, 0, 0);
      canvas.toBlob((blob) => {
        if (blob) {
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = 'gantt-chart.png';
          a.click();
          URL.revokeObjectURL(url);
        }
      });
    };

    img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgString)));
  };

  // Handle mouse move for tooltip positioning
  const handleMouseMove = (event: React.MouseEvent<SVGSVGElement>) => {
    const svg = svgRef.current;
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    setMousePosition({
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    });
  };

  // Check if activity is highlighted
  const isActivityHighlighted = (activity: Activity): boolean => {
    return selectedLot !== null && activity.lot_id === selectedLot;
  };

  // Check if activity matches search
  const matchesSearch = (activity: Activity): boolean => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      activity.lot_id.toLowerCase().includes(query) ||
      activity.id.toLowerCase().includes(query) ||
      Boolean(activity.lot_type && activity.lot_type.toLowerCase().includes(query))
    );
  };

  // Calculate activity statistics
  const activityStats = useMemo(() => {
    const stats: Record<string, number> = {
      FILL: 0,
      CLEAN: 0,
      CHANGEOVER: 0,
      total: activities.length,
    };

    activities.forEach((activity) => {
      if (activity.kind && activity.kind in stats) {
        stats[activity.kind]++;
      }
    });

    return stats;
  }, [activities]);

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
      {/* Top Controls - Search and Actions */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2,
          gap: 2,
          flexWrap: 'wrap',
        }}
      >
        {/* Search */}
        <TextField
          size="small"
          placeholder="Search lots..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{ minWidth: 250 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search fontSize="small" />
              </InputAdornment>
            ),
            endAdornment: searchQuery && (
              <InputAdornment position="end">
                <IconButton size="small" onClick={() => setSearchQuery('')}>
                  <Clear fontSize="small" />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />

        {/* Action Buttons */}
        <Stack direction="row" spacing={1}>
          <Tooltip title="Zoom In">
            <IconButton size="small" onClick={handleZoomIn} color="primary">
              <ZoomIn />
            </IconButton>
          </Tooltip>
          <Tooltip title="Zoom Out">
            <IconButton size="small" onClick={handleZoomOut} color="primary">
              <ZoomOut />
            </IconButton>
          </Tooltip>
          <Tooltip title="Reset View">
            <IconButton size="small" onClick={handleResetZoom} color="primary">
              <FitScreen />
            </IconButton>
          </Tooltip>
          <Tooltip title="Export as PNG">
            <IconButton size="small" onClick={handleExportImage} color="primary">
              <Download />
            </IconButton>
          </Tooltip>
        </Stack>
      </Box>

      {/* Controls */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 2,
          flexWrap: 'wrap',
          gap: 2,
        }}
      >
        {/* Zoom Controls */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2" sx={{ mr: 1 }}>
            Zoom:
          </Typography>
          <ToggleButtonGroup
            value={customZoom ? null : zoomLevel}
            exclusive
            onChange={(_e, value) => {
              if (value) {
                setZoomLevel(value);
                setCustomZoom(null);
              }
            }}
            size="small"
          >
            <ToggleButton value="1h">1h</ToggleButton>
            <ToggleButton value="4h">4h</ToggleButton>
            <ToggleButton value="8h">8h</ToggleButton>
            <ToggleButton value="24h">24h</ToggleButton>
            <ToggleButton value="all">All</ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {/* Filter Controls */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2" sx={{ mr: 1 }}>
            Filter:
          </Typography>
          <ToggleButtonGroup
            value={filterType}
            exclusive
            onChange={(_e, value) => value && setFilterType(value)}
            size="small"
          >
            <ToggleButton value="all">All</ToggleButton>
            <ToggleButton value="FILL">Fill</ToggleButton>
            <ToggleButton value="CLEAN">Clean</ToggleButton>
            <ToggleButton value="CHANGEOVER">Changeover</ToggleButton>
          </ToggleButtonGroup>
        </Box>

        {/* Legend */}
        <Stack direction="row" spacing={1}>
          {Object.entries(ACTIVITY_LABELS).map(([key, label]) => (
            <Chip
              key={key}
              label={`${label} (${activityStats[key] || 0})`}
              size="small"
              sx={{
                bgcolor: ACTIVITY_COLORS[key],
                color: 'white',
                fontWeight: 'bold',
              }}
            />
          ))}
        </Stack>
      </Box>

      {/* Search Results Info */}
      {searchQuery && filteredActivities.length > 0 && (
        <Paper sx={{ p: 1.5, mb: 2, bgcolor: 'info.light', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="body2">
            Found <strong>{filteredActivities.length}</strong> activities matching "{searchQuery}"
          </Typography>
          <Button size="small" onClick={() => setSearchQuery('')} variant="outlined">
            Clear Search
          </Button>
        </Paper>
      )}

      {/* Gantt Chart */}
      <Paper sx={{ p: 2, overflow: 'auto', position: 'relative' }}>
        {searchQuery && filteredActivities.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <Typography variant="body2" color="text.secondary">
              No activities found matching "{searchQuery}"
            </Typography>
            <Button size="small" onClick={() => setSearchQuery('')} sx={{ mt: 1 }}>
              Clear Search
            </Button>
          </Box>
        )}
        {(searchQuery === '' || filteredActivities.length > 0) && (
          <svg
            ref={svgRef}
            width={width}
            height={height}
            style={{ display: 'block', margin: '0 auto' }}
            onMouseMove={handleMouseMove}
            onMouseLeave={() => setHoveredActivity(null)}
          >
          {/* Professional Timeline Header */}
          {/* Left panel header */}
          <rect
            x={0}
            y={0}
            width={leftMargin}
            height={topMargin}
            fill="#e8eaed"
            stroke="#ccc"
            strokeWidth={1}
          />

          {/* Column headers in left panel */}
          <text
            x={10}
            y={20}
            fontSize={11}
            fontWeight="bold"
            fill="#333"
          >
            Task Name
          </text>
          <text
            x={10}
            y={45}
            fontSize={10}
            fill="#666"
          >
            (Resource)
          </text>
          <text
            x={leftMargin - 60}
            y={30}
            fontSize={10}
            fontWeight="bold"
            fill="#333"
            textAnchor="middle"
          >
            Load
          </text>

          {/* Header background */}
          <rect
            x={0}
            y={0}
            width={width}
            height={topMargin}
            fill="#e8eaed"
            stroke="#ccc"
            strokeWidth={1}
          />

          {/* Task Name column header */}
          <rect
            x={0}
            y={0}
            width={leftMargin}
            height={topMargin}
            fill="#e8eaed"
            stroke="#ccc"
            strokeWidth={1}
          />
          <text
            x={leftMargin / 2}
            y={25}
            fontSize={12}
            fontWeight="600"
            textAnchor="middle"
            fill="#333"
          >
            Task Name
          </text>

          {/* Timeline header with date ranges and day-of-week */}
          {scheduleStartTime && (() => {
            const startDate = new Date(scheduleStartTime);
            const endDate = new Date(startDate.getTime() + visibleTimeRange.end * 60 * 60 * 1000);

            // Generate date range groups (week ranges)
            const dateRanges: { label: string; startX: number; endX: number }[] = [];
            const dayMarkers: { day: string; x: number; date: Date }[] = [];

            // Calculate number of days to show
            const totalHours = visibleTimeRange.end - visibleTimeRange.start;
            const totalDays = Math.ceil(totalHours / 24);

            let currentDate = new Date(startDate.getTime() + visibleTimeRange.start * 60 * 60 * 1000);
            currentDate.setHours(0, 0, 0, 0); // Start of day

            // Generate week groupings
            let weekStart = new Date(currentDate);
            let weekLabel = '';
            let weekStartX = leftMargin;

            for (let day = 0; day <= totalDays; day++) {
              const date = new Date(currentDate.getTime() + day * 24 * 60 * 60 * 1000);
              const hoursFromScheduleStart = (date.getTime() - startDate.getTime()) / (1000 * 60 * 60);

              if (hoursFromScheduleStart < visibleTimeRange.start) continue;
              if (hoursFromScheduleStart > visibleTimeRange.end) break;

              const x = timeScale(hoursFromScheduleStart);

              // Check if we need to start a new week group
              const isMonday = date.getDay() === 1 || day === 0;
              if (isMonday && day > 0) {
                // End previous week
                const endDate = new Date(date.getTime() - 24 * 60 * 60 * 1000);
                weekLabel = `${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${endDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
                dateRanges.push({ label: weekLabel, startX: weekStartX, endX: x });

                // Start new week
                weekStart = new Date(date);
                weekStartX = x;
              }

              // Add day marker
              dayMarkers.push({
                day: date.toLocaleDateString('en-US', { weekday: 'narrow' }),
                x: x,
                date: date
              });
            }

            // Add last week group
            if (weekStart) {
              weekLabel = `${weekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${endDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
              dateRanges.push({ label: weekLabel, startX: weekStartX, endX: width - rightMargin });
            }

            return (
              <>
                {/* Top row - Date range groups */}
                {dateRanges.map((range, idx) => (
                  <g key={`date-range-${idx}`}>
                    <line
                      x1={range.startX}
                      y1={0}
                      x2={range.startX}
                      y2={topMargin}
                      stroke="#999"
                      strokeWidth={1}
                    />
                    <text
                      x={(range.startX + range.endX) / 2}
                      y={20}
                      fontSize={11}
                      fontWeight="600"
                      textAnchor="middle"
                      fill="#333"
                    >
                      {range.label}
                    </text>
                  </g>
                ))}

                {/* Divider line */}
                <line
                  x1={leftMargin}
                  y1={35}
                  x2={width - rightMargin}
                  y2={35}
                  stroke="#999"
                  strokeWidth={1}
                />

                {/* Bottom row - Day of week markers */}
                {dayMarkers.map((marker, idx) => (
                  <g key={`day-marker-${idx}`}>
                    {/* Day cell background - highlight weekends */}
                    {idx < dayMarkers.length - 1 && (
                      <rect
                        x={marker.x}
                        y={35}
                        width={dayMarkers[idx + 1].x - marker.x}
                        height={topMargin - 35}
                        fill={marker.date.getDay() === 0 || marker.date.getDay() === 6 ? '#d0d0d0' : 'transparent'}
                        opacity={0.3}
                      />
                    )}
                    {/* Day letter */}
                    <text
                      x={idx < dayMarkers.length - 1 ? (marker.x + dayMarkers[idx + 1].x) / 2 : marker.x + 20}
                      y={60}
                      fontSize={10}
                      fontWeight="500"
                      textAnchor="middle"
                      fill={marker.date.getDay() === 0 || marker.date.getDay() === 6 ? '#666' : '#333'}
                    >
                      {marker.day}
                    </text>
                    {/* Vertical separator */}
                    <line
                      x1={marker.x}
                      y1={35}
                      x2={marker.x}
                      y2={topMargin}
                      stroke="#ccc"
                      strokeWidth={1}
                    />
                  </g>
                ))}
              </>
            );
          })()}

          {/* Grid lines */}
          {timeMarkers.map((time, idx) => (
            <line
              key={`grid-${idx}`}
              x1={timeScale(time)}
              y1={topMargin}
              x2={timeScale(time)}
              y2={height - bottomMargin}
              stroke="#e0e0e0"
              strokeWidth={1}
              strokeDasharray="4,4"
            />
          ))}

          {/* Task Groups (Equipment rows) */}
          {activityGroups.map((group, groupIdx) => {
            const yPos = taskGroupYPositions[groupIdx];
            const groupHeight = taskGroupHeights[groupIdx];

            return (
              <g key={`task-group-${groupIdx}`}>
                {/* Alternating background for entire task group */}
                <rect
                  x={0}
                  y={yPos}
                  width={width}
                  height={groupHeight}
                  fill={groupIdx % 2 === 0 ? '#ffffff' : '#f8f9fa'}
                  opacity={0.6}
                />

                {/* Left panel background for task name */}
                <rect
                  x={0}
                  y={yPos}
                  width={leftMargin}
                  height={groupHeight}
                  fill={groupIdx % 2 === 0 ? '#f0f0f0' : '#ffffff'}
                  stroke="#d0d0d0"
                  strokeWidth={1}
                />

                {/* Task Name */}
                <text
                  x={10}
                  y={yPos + 22}
                  fontSize={13}
                  fontWeight="600"
                  textAnchor="start"
                  fill="#1a3a52"
                >
                  Task {group.fillerId}
                </text>

                {/* Horizontal separator at bottom of task group */}
                <line
                  x1={0}
                  y1={yPos + groupHeight}
                  x2={width}
                  y2={yPos + groupHeight}
                  stroke="#d0d0d0"
                  strokeWidth={1.5}
                />
              </g>
            );
          })}

          {/* Current time indicator (Today line) */}
          {scheduleStartTime && (() => {
            const now = new Date();
            const start = new Date(scheduleStartTime);
            const hoursFromStart = (now.getTime() - start.getTime()) / (1000 * 60 * 60);

            // Only show if current time is within visible range and schedule has started
            if (hoursFromStart >= visibleTimeRange.start && hoursFromStart <= visibleTimeRange.end && hoursFromStart >= 0) {
              const x = timeScale(hoursFromStart);
              return (
                <g>
                  {/* Vertical line */}
                  <line
                    x1={x}
                    y1={topMargin}
                    x2={x}
                    y2={height - bottomMargin}
                    stroke="#ff0000"
                    strokeWidth={2}
                    strokeDasharray="5,5"
                    opacity={0.7}
                  />
                  {/* Label */}
                  <rect
                    x={x - 20}
                    y={topMargin - 8}
                    width={40}
                    height={16}
                    fill="#ff0000"
                    rx={3}
                  />
                  <text
                    x={x}
                    y={topMargin + 2}
                    fontSize={9}
                    fontWeight="bold"
                    fill="white"
                    textAnchor="middle"
                  >
                    NOW
                  </text>
                </g>
              );
            }
            return null;
          })()}

          {/* Activity bars - stacked within task groups */}
          {activityGroups.map((group, groupIdx) => {
            const groupYPos = taskGroupYPositions[groupIdx];

            // Filter activities for this group based on search and filter
            const groupActivities = group.activities.filter(a => {
              const timeVisible = a.end_time >= visibleTimeRange.start && a.start_time <= visibleTimeRange.end;
              const typeMatch = filterType === 'all' || a.kind === filterType;
              const searchMatch = !searchQuery || matchesSearch(a);
              return timeVisible && typeMatch && searchMatch;
            });

            // Sort activities by start time to display in chronological order
            const sortedActivities = [...groupActivities].sort((a, b) => a.start_time - b.start_time);

            // Render activities - each activity gets its own row (stacked vertically)
            return sortedActivities.map((activity, actIdx) => {
                const y = groupYPos + taskHeaderHeight + taskPadding + actIdx * (activityBarHeight + activitySpacing);
                const x = timeScale(activity.start_time);
                const barWidth = Math.max(
                  timeScale(activity.end_time) - x,
                  3 // Minimum width for visibility
                );
                const isHighlighted = isActivityHighlighted(activity);
                const isHovered = hoveredActivity?.id === activity.id;
                const isSearchMatch = searchQuery && matchesSearch(activity);
                const uniqueId = `${groupIdx}-${actIdx}`;

                return (
                  <g key={`activity-${uniqueId}`}>
                    {/* Glow effect for search matches */}
                    {isSearchMatch && (
                      <rect
                        x={x - 2}
                        y={y - 2}
                        width={barWidth + 4}
                        height={activityBarHeight + 4}
                        fill="none"
                        stroke="#FFD700"
                        strokeWidth={2}
                        opacity={0.7}
                        rx={2}
                      />
                    )}
                    {/* Activity bar with gradient effect */}
                    <defs>
                      <linearGradient id={`gradient-${uniqueId}`} x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" style={{ stopColor: getActivityColor(activity), stopOpacity: 1 }} />
                        <stop offset="100%" style={{ stopColor: getActivityColor(activity), stopOpacity: 0.85 }} />
                      </linearGradient>
                    </defs>
                    <rect
                      x={x}
                      y={y}
                      width={barWidth}
                      height={activityBarHeight}
                      fill={`url(#gradient-${uniqueId})`}
                      stroke={isHighlighted || isHovered ? '#000' : isSearchMatch ? '#FFD700' : '#555'}
                      strokeWidth={isHighlighted ? 2.5 : isHovered || isSearchMatch ? 2 : 0.5}
                      opacity={
                        selectedLot === null
                          ? isHovered
                            ? 1.0
                            : 0.95
                          : isHighlighted
                          ? 1.0
                          : 0.3
                      }
                      rx={2}
                      ry={2}
                      style={{ cursor: 'pointer' }}
                      onClick={() => handleActivityClick(activity)}
                      onMouseEnter={() => setHoveredActivity(activity)}
                      onMouseLeave={() => setHoveredActivity(null)}
                    >
                      <title>
                        {`Lot: ${activity.lot_id}\nType: ${
                          activity.kind || 'N/A'
                        }\nStart: ${activity.start_time.toFixed(
                          1
                        )}h\nEnd: ${activity.end_time.toFixed(
                          1
                        )}h\nDuration: ${activity.duration.toFixed(1)}h${
                          activity.lot_type
                            ? `\nLot Type: ${activity.lot_type}`
                            : ''
                        }${
                          activity.num_units
                            ? `\nUnits: ${activity.num_units}`
                            : ''
                        }`}
                      </title>
                    </rect>

                    {/* Activity label (only if wide enough) */}
                    {barWidth > 50 && (
                      <text
                        x={x + barWidth / 2}
                        y={y + activityBarHeight / 2}
                        fontSize={10}
                        fontWeight="600"
                        fill="white"
                        textAnchor="middle"
                        dominantBaseline="middle"
                        pointerEvents="none"
                        style={{
                          textShadow: '0 0 3px rgba(0,0,0,0.7)',
                        }}
                      >
                        {activity.lot_id.length > 12
                          ? activity.lot_id.substring(0, 10) + '...'
                          : activity.lot_id}
                      </text>
                    )}
                  </g>
                );
            });
          })}

          {/* X-axis */}
          <line
            x1={leftMargin}
            y1={height - bottomMargin}
            x2={width - rightMargin}
            y2={height - bottomMargin}
            stroke="#333"
            strokeWidth={2}
          />

          {/* Time markers in header (bottom row) */}
          {timeMarkers.map((time, idx) => {
            const actualDate = getActualDateTime(time);
            return (
              <g key={`marker-${idx}`}>
                {/* Tick mark at top */}
                <line
                  x1={timeScale(time)}
                  y1={30}
                  x2={timeScale(time)}
                  y2={topMargin}
                  stroke="#999"
                  strokeWidth={0.5}
                />

                {/* Time label in header */}
                <text
                  x={timeScale(time)}
                  y={48}
                  fontSize={10}
                  textAnchor="middle"
                  fill="#666"
                >
                  {actualDate
                    ? actualDate.toLocaleTimeString('en-US', { hour: 'numeric', hour12: true })
                    : `${time.toFixed(0)}h`}
                </text>
              </g>
            );
          })}

          {/* Axis labels */}
          <text
            x={width / 2}
            y={height - 10}
            fontSize={14}
            fontWeight="bold"
            textAnchor="middle"
          >
            {scheduleStartTime ? 'Schedule Timeline' : 'Time (hours)'}
          </text>

          <text
            x={10}
            y={20}
            fontSize={14}
            fontWeight="bold"
            textAnchor="start"
          >
            Resources
          </text>
        </svg>
        )}

        {/* Hover tooltip */}
        {hoveredActivity && mousePosition && (
          <Paper
            sx={{
              position: 'absolute',
              left: Math.min(mousePosition.x + 10, width - 320),
              top: Math.max(mousePosition.y - 100, 10),
              p: 1.5,
              bgcolor: 'rgba(0, 0, 0, 0.9)',
              color: 'white',
              borderRadius: 1,
              maxWidth: 320,
              pointerEvents: 'none',
              zIndex: 1000,
            }}
          >
            <Typography variant="subtitle2" fontWeight="bold">
              {hoveredActivity.lot_id}
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.5 }}>
              <strong>Type:</strong> {hoveredActivity.kind || 'N/A'}
            </Typography>
            <Typography variant="body2">
              <strong>Start:</strong>{' '}
              {scheduleStartTime && getActualDateTime(hoveredActivity.start_time)
                ? formatDateTime(getActualDateTime(hoveredActivity.start_time)!)
                : `${hoveredActivity.start_time.toFixed(2)}h`}
            </Typography>
            <Typography variant="body2">
              <strong>End:</strong>{' '}
              {scheduleStartTime && getActualDateTime(hoveredActivity.end_time)
                ? formatDateTime(getActualDateTime(hoveredActivity.end_time)!)
                : `${hoveredActivity.end_time.toFixed(2)}h`}
            </Typography>
            <Typography variant="body2">
              <strong>Duration:</strong> {hoveredActivity.duration.toFixed(2)}h
            </Typography>
            {hoveredActivity.lot_type && (
              <Typography variant="body2">
                <strong>Lot Type:</strong> {hoveredActivity.lot_type}
              </Typography>
            )}
            {hoveredActivity.num_units && (
              <Typography variant="body2">
                <strong>Units:</strong> {hoveredActivity.num_units}
              </Typography>
            )}
          </Paper>
        )}

        {/* Selected lot info */}
        {selectedLot && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
            <Typography variant="body2">
              <strong>Selected Lot:</strong> {selectedLot} (
              {
                filteredActivities.filter((a) => a.lot_id === selectedLot)
                  .length
              }{' '}
              activities highlighted)
            </Typography>
            <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
              Click any activity to select/deselect its lot
            </Typography>
          </Box>
        )}

        {/* Info */}
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ display: 'block', mt: 2, textAlign: 'center' }}
        >
          Showing {filteredActivities.length} of {activities.length} activities
          {zoomLevel !== 'all' &&
            ` (${visibleTimeRange.start.toFixed(0)}h - ${visibleTimeRange.end.toFixed(
              0
            )}h)`}
        </Typography>
      </Paper>
    </Box>
  );
};
