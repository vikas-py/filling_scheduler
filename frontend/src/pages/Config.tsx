import { useState } from 'react';
import { Container, Typography, Box, Paper, Tabs, Tab, Button, Alert } from '@mui/material';
import { Settings, Save, RestartAlt } from '@mui/icons-material';
import { GeneralSettings } from '../components/config/GeneralSettings';
import { StrategyDefaults } from '../components/config/StrategyDefaults';
import { FillerSettings } from '../components/config/FillerSettings';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel = ({ children, value, index }: TabPanelProps) => {
  return (
    <div role="tabpanel" hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
};

export const Config = () => {
  const [tabValue, setTabValue] = useState(0);
  const [hasChanges, setHasChanges] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleSave = () => {
    // TODO: Implement save functionality
    console.log('Saving configuration...');
    setSaveSuccess(true);
    setHasChanges(false);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset all settings to defaults?')) {
      // TODO: Implement reset functionality
      console.log('Resetting to defaults...');
      setHasChanges(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Settings sx={{ fontSize: 32, color: 'primary.main' }} />
          <Typography variant="h4" component="h1">
            Configuration
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            startIcon={<RestartAlt />}
            onClick={handleReset}
            variant="outlined"
            color="secondary"
          >
            Reset to Defaults
          </Button>
          <Button
            startIcon={<Save />}
            onClick={handleSave}
            variant="contained"
            disabled={!hasChanges}
          >
            Save Changes
          </Button>
        </Box>
      </Box>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Manage application settings, default strategy parameters, and filler configurations.
      </Typography>

      {/* Success Alert */}
      {saveSuccess && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Configuration saved successfully!
        </Alert>
      )}

      {/* Tabs */}
      <Paper>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="General Settings" />
          <Tab label="Strategy Defaults" />
          <Tab label="Filler Configuration" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Box sx={{ p: 2 }}>
            <GeneralSettings onChange={() => setHasChanges(true)} />
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ p: 2 }}>
            <StrategyDefaults onChange={() => setHasChanges(true)} />
          </Box>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Box sx={{ p: 2 }}>
            <FillerSettings onChange={() => setHasChanges(true)} />
          </Box>
        </TabPanel>
      </Paper>
    </Container>
  );
};
