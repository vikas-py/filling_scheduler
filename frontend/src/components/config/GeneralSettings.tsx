import {
  Box,
  Typography,
  FormControl,
  FormControlLabel,
  Switch,
  Select,
  MenuItem,
  InputLabel,
  Paper,
  Divider,
} from '@mui/material';

interface GeneralSettingsProps {
  onChange?: () => void;
}

export const GeneralSettings = ({ onChange }: GeneralSettingsProps) => {
  const handleChange = () => {
    if (onChange) onChange();
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        General Settings
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Configure application-wide preferences and behavior.
      </Typography>

      {/* Appearance */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
          Appearance
        </Typography>
        <Divider sx={{ mb: 2 }} />

        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Theme</InputLabel>
          <Select defaultValue="light" label="Theme" onChange={handleChange}>
            <MenuItem value="light">Light</MenuItem>
            <MenuItem value="dark">Dark</MenuItem>
            <MenuItem value="auto">Auto (System)</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Language</InputLabel>
          <Select defaultValue="en" label="Language" onChange={handleChange}>
            <MenuItem value="en">English</MenuItem>
            <MenuItem value="es">Spanish</MenuItem>
            <MenuItem value="fr">French</MenuItem>
            <MenuItem value="de">German</MenuItem>
          </Select>
        </FormControl>

        <FormControlLabel
          control={<Switch defaultChecked onChange={handleChange} />}
          label="Show tooltips and help text"
        />
      </Paper>

      {/* Notifications */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
          Notifications
        </Typography>
        <Divider sx={{ mb: 2 }} />

        <FormControlLabel
          control={<Switch defaultChecked onChange={handleChange} />}
          label="Enable desktop notifications"
        />
        <FormControlLabel
          control={<Switch defaultChecked onChange={handleChange} />}
          label="Notify when schedule completes"
        />
        <FormControlLabel
          control={<Switch onChange={handleChange} />}
          label="Notify on schedule failures"
        />
        <FormControlLabel
          control={<Switch onChange={handleChange} />}
          label="Email notifications"
        />
      </Paper>

      {/* Data & Privacy */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
          Data & Privacy
        </Typography>
        <Divider sx={{ mb: 2 }} />

        <FormControlLabel
          control={<Switch defaultChecked onChange={handleChange} />}
          label="Auto-save drafts"
        />
        <FormControlLabel
          control={<Switch defaultChecked onChange={handleChange} />}
          label="Enable analytics"
        />
        <FormControl fullWidth sx={{ mt: 2 }}>
          <InputLabel>Data retention period</InputLabel>
          <Select defaultValue="90" label="Data retention period" onChange={handleChange}>
            <MenuItem value="30">30 days</MenuItem>
            <MenuItem value="90">90 days</MenuItem>
            <MenuItem value="180">180 days</MenuItem>
            <MenuItem value="365">1 year</MenuItem>
            <MenuItem value="-1">Forever</MenuItem>
          </Select>
        </FormControl>
      </Paper>

      {/* Performance */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
          Performance
        </Typography>
        <Divider sx={{ mb: 2 }} />

        <FormControl fullWidth sx={{ mb: 2 }}>
          <InputLabel>Chart animation</InputLabel>
          <Select defaultValue="normal" label="Chart animation" onChange={handleChange}>
            <MenuItem value="none">Disabled</MenuItem>
            <MenuItem value="fast">Fast</MenuItem>
            <MenuItem value="normal">Normal</MenuItem>
            <MenuItem value="smooth">Smooth</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel>Items per page</InputLabel>
          <Select defaultValue="10" label="Items per page" onChange={handleChange}>
            <MenuItem value="5">5</MenuItem>
            <MenuItem value="10">10</MenuItem>
            <MenuItem value="25">25</MenuItem>
            <MenuItem value="50">50</MenuItem>
            <MenuItem value="100">100</MenuItem>
          </Select>
        </FormControl>
      </Paper>
    </Box>
  );
};
