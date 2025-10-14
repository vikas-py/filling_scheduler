import { Box, Typography, Paper, Chip, Button, Stack } from '@mui/material';
import { EmojiEvents, TrendingUp, Speed, AccessTime } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import type { Schedule } from '../../api/schedules';

interface BestScheduleCardProps {
  schedules: Schedule[];
}

interface ScheduleScore {
  schedule: Schedule;
  makespan: number;
  utilization: number;
  makespanScore: number; // 0-100, higher is better
  utilizationScore: number; // 0-100, higher is better
  totalScore: number;
}

export const BestScheduleCard = ({ schedules }: BestScheduleCardProps) => {
  const navigate = useNavigate();

  if (!schedules || schedules.length === 0) {
    return null;
  }

  // Calculate scores for each schedule
  const scores: ScheduleScore[] = schedules.map((schedule) => {
    const activities = schedule.activities || [];
    const numFillers = (schedule.config?.num_fillers as number) || 1;

    const maxEndTime = activities.length > 0 ? Math.max(...activities.map((a) => a.end_time)) : 0;
    const makespan = schedule.total_time || maxEndTime;

    const totalProcessingTime = activities.reduce((sum, a) => sum + a.duration, 0);
    const maxPossibleTime = makespan * numFillers;
    const utilization = maxPossibleTime > 0 ? (totalProcessingTime / maxPossibleTime) * 100 : 0;

    return {
      schedule,
      makespan,
      utilization,
      makespanScore: 0,
      utilizationScore: utilization,
      totalScore: 0,
    };
  });

  // Normalize makespan scores (lower makespan = higher score)
  const makespans = scores.map((s) => s.makespan);
  const maxMakespan = Math.max(...makespans);
  const minMakespan = Math.min(...makespans);
  const makespanRange = maxMakespan - minMakespan;

  scores.forEach((score) => {
    score.makespanScore =
      makespanRange > 0 ? ((maxMakespan - score.makespan) / makespanRange) * 100 : 100;
    // Total score: 50% makespan + 50% utilization
    score.totalScore = (score.makespanScore + score.utilizationScore) / 2;
  });

  // Find best schedule
  const bestScore = scores.reduce((best, current) =>
    current.totalScore > best.totalScore ? current : best
  );

  const bestSchedule = bestScore.schedule;

  // Determine why it's best
  const reasons: string[] = [];
  if (bestScore.makespanScore >= 80) {
    reasons.push('Fastest completion time');
  }
  if (bestScore.utilizationScore >= 80) {
    reasons.push('High resource utilization');
  }
  if (bestScore.totalScore >= 85) {
    reasons.push('Best overall balance');
  }
  if (reasons.length === 0) {
    reasons.push('Best among compared schedules');
  }

  return (
    <Paper
      sx={{
        p: 3,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
        <EmojiEvents sx={{ fontSize: 48, color: '#ffd700' }} />
        <Box>
          <Typography variant="overline" sx={{ opacity: 0.9 }}>
            Recommended Schedule
          </Typography>
          <Typography variant="h4" fontWeight="bold">
            {bestSchedule.name}
          </Typography>
        </Box>
      </Box>

      <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
        <Chip
          label={bestSchedule.strategy}
          sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
        />
        <Chip
          label={`Score: ${bestScore.totalScore.toFixed(1)}/100`}
          sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
        />
      </Stack>

      <Typography variant="body1" sx={{ mb: 2, opacity: 0.9 }}>
        {bestSchedule.description || 'This schedule provides the best performance based on the comparison criteria.'}
      </Typography>

      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" fontWeight="bold" sx={{ mb: 1 }}>
          Why this schedule is recommended:
        </Typography>
        <ul style={{ margin: 0, paddingLeft: '20px' }}>
          {reasons.map((reason, index) => (
            <li key={index}>
              <Typography variant="body2">{reason}</Typography>
            </li>
          ))}
        </ul>
      </Box>

      <Stack direction="row" spacing={2} sx={{ mb: 3 }}>
        <Paper sx={{ p: 1.5, flex: 1, bgcolor: 'rgba(255,255,255,0.15)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            <AccessTime sx={{ fontSize: 20 }} />
            <Typography variant="caption">Makespan</Typography>
          </Box>
          <Typography variant="h6" fontWeight="bold">
            {bestScore.makespan.toFixed(2)}h
          </Typography>
          <Chip
            label={`${bestScore.makespanScore.toFixed(0)}% efficient`}
            size="small"
            sx={{ mt: 0.5, bgcolor: 'rgba(255,255,255,0.2)' }}
          />
        </Paper>

        <Paper sx={{ p: 1.5, flex: 1, bgcolor: 'rgba(255,255,255,0.15)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            <TrendingUp sx={{ fontSize: 20 }} />
            <Typography variant="caption">Utilization</Typography>
          </Box>
          <Typography variant="h6" fontWeight="bold">
            {bestScore.utilization.toFixed(1)}%
          </Typography>
          <Chip
            label={bestScore.utilization >= 80 ? 'Excellent' : 'Good'}
            size="small"
            sx={{ mt: 0.5, bgcolor: 'rgba(255,255,255,0.2)' }}
          />
        </Paper>

        <Paper sx={{ p: 1.5, flex: 1, bgcolor: 'rgba(255,255,255,0.15)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
            <Speed sx={{ fontSize: 20 }} />
            <Typography variant="caption">Overall Score</Typography>
          </Box>
          <Typography variant="h6" fontWeight="bold">
            {bestScore.totalScore.toFixed(1)}/100
          </Typography>
          <Chip
            label={bestScore.totalScore >= 80 ? '⭐ Outstanding' : '✓ Good'}
            size="small"
            sx={{ mt: 0.5, bgcolor: 'rgba(255,255,255,0.2)' }}
          />
        </Paper>
      </Stack>

      <Button
        variant="contained"
        size="large"
        onClick={() => navigate(`/schedules/${bestSchedule.id}`)}
        sx={{
          bgcolor: 'white',
          color: '#667eea',
          '&:hover': {
            bgcolor: 'rgba(255,255,255,0.9)',
          },
        }}
      >
        View Full Details
      </Button>
    </Paper>
  );
};
