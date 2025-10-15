import { useState, useMemo, useRef, useEffect } from 'react';
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

  const formatDateTimeShort = (date: Date): string => {
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
    });
  };

  // Chart dimensions
  const width = 1200;
  const leftMargin = 100;
  const rightMargin = 50;
  const topMargin = 40;
  const bottomMargin = 60;
  const rowHeight = 50;
  const barHeight = 35;
  const height = numFillers * rowHeight + topMargin + bottomMargin;

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
      (activity.lot_type && activity.lot_type.toLowerCase().includes(query))
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

          {/* Y-axis labels (Filler names) */}
          {Array.from({ length: numFillers }, (_, i) => (
            <g key={`filler-${i}`}>
              {/* Filler label */}
              <text
                x={10}
                y={topMargin + i * rowHeight + rowHeight / 2}
                fontSize={14}
                fontWeight="bold"
                textAnchor="start"
                dominantBaseline="middle"
              >
                Filler {i + 1}
              </text>

              {/* Horizontal row separator */}
              {i < numFillers - 1 && (
                <line
                  x1={leftMargin}
                  y1={topMargin + (i + 1) * rowHeight}
                  x2={width - rightMargin}
                  y2={topMargin + (i + 1) * rowHeight}
                  stroke="#e0e0e0"
                  strokeWidth={1}
                />
              )}
            </g>
          ))}

          {/* Activity bars */}
          {filteredActivities.map((activity, idx) => {
            const y =
              topMargin +
              (activity.filler_id - 1) * rowHeight +
              (rowHeight - barHeight) / 2;
            const x = timeScale(activity.start_time);
            const barWidth = Math.max(
              timeScale(activity.end_time) - x,
              2 // Minimum width for visibility
            );
            const isHighlighted = isActivityHighlighted(activity);
            const isHovered = hoveredActivity?.id === activity.id;
            const isSearchMatch = searchQuery && matchesSearch(activity);

            return (
              <g key={`activity-${idx}`}>
                {/* Glow effect for search matches */}
                {isSearchMatch && (
                  <rect
                    x={x - 2}
                    y={y - 2}
                    width={barWidth + 4}
                    height={barHeight + 4}
                    fill="none"
                    stroke="#FFD700"
                    strokeWidth={2}
                    opacity={0.7}
                    rx={2}
                  />
                )}
                <rect
                  x={x}
                  y={y}
                  width={barWidth}
                  height={barHeight}
                  fill={getActivityColor(activity)}
                  stroke={isHighlighted || isHovered ? '#000' : isSearchMatch ? '#FFD700' : '#333'}
                  strokeWidth={isHighlighted ? 3 : isHovered || isSearchMatch ? 2 : 1}
                  opacity={
                    selectedLot === null
                      ? isHovered
                        ? 0.9
                        : 0.8
                      : isHighlighted
                      ? 1.0
                      : 0.3
                  }
                  rx={4}
                  ry={4}
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
                {barWidth > 60 && (
                  <text
                    x={x + barWidth / 2}
                    y={y + barHeight / 2}
                    fontSize={11}
                    fontWeight="bold"
                    fill="white"
                    textAnchor="middle"
                    dominantBaseline="middle"
                    pointerEvents="none"
                    style={{
                      textShadow: '0 0 3px rgba(0,0,0,0.5)',
                    }}
                  >
                    {activity.lot_id.length > 10
                      ? activity.lot_id.substring(0, 10) + '...'
                      : activity.lot_id}
                  </text>
                )}
              </g>
            );
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

          {/* Time markers */}
          {timeMarkers.map((time, idx) => {
            const actualDate = getActualDateTime(time);
            return (
              <g key={`marker-${idx}`}>
                {/* Tick mark */}
                <line
                  x1={timeScale(time)}
                  y1={height - bottomMargin}
                  x2={timeScale(time)}
                  y2={height - bottomMargin + 8}
                  stroke="#333"
                  strokeWidth={2}
                />

                {/* Time label */}
                <text
                  x={timeScale(time)}
                  y={height - bottomMargin + 25}
                  fontSize={11}
                  textAnchor="middle"
                >
                  {actualDate ? formatDateTimeShort(actualDate) : `${time.toFixed(0)}h`}
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
