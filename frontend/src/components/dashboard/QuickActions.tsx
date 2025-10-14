import { Box, Button, Stack } from '@mui/material';
import {
  Add as AddIcon,
  CompareArrows as CompareIcon,
  Upload as UploadIcon,
  ListAlt as ListIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '@/utils/constants';

export const QuickActions = () => {
  const navigate = useNavigate();

  return (
    <Box sx={{ mb: 3 }}>
      <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => navigate(ROUTES.SCHEDULE_NEW)}
          size="large"
        >
          New Schedule
        </Button>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<CompareIcon />}
          onClick={() => navigate(ROUTES.COMPARE)}
        >
          Compare Strategies
        </Button>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<ListIcon />}
          onClick={() => navigate(ROUTES.SCHEDULES)}
        >
          View All Schedules
        </Button>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<UploadIcon />}
          onClick={() => navigate(ROUTES.SCHEDULE_NEW)}
        >
          Upload File
        </Button>
      </Stack>
    </Box>
  );
};
