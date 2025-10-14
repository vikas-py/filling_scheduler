import { useState } from 'react';
import { Container, Typography, Box, Paper, Stepper, Step, StepLabel, Button, TextField } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { CsvUpload } from '../components/schedule/CsvUpload';
import { DataPreview } from '../components/schedule/DataPreview';
import { StrategySelector, type StrategyType } from '../components/schedule/StrategySelector';
import { ConfigEditor } from '../components/schedule/ConfigEditor';
import { ProgressIndicator, type ProgressStatus } from '../components/schedule/ProgressIndicator';
import { createSchedule } from '../api/schedules';

const steps = ['Upload Data', 'Select Strategy', 'Configure', 'Review & Create'];

export const ScheduleCreate = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);

  // Form state
  const [scheduleName, setScheduleName] = useState('');
  const [scheduleDescription, setScheduleDescription] = useState('');
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [selectedStrategy, setSelectedStrategy] = useState<StrategyType | null>(null);
  const [config, setConfig] = useState<Record<string, unknown>>({});

  // Progress state
  const [progressStatus, setProgressStatus] = useState<ProgressStatus>('idle');
  const [error, setError] = useState<string>('');
  const [createdScheduleId, setCreatedScheduleId] = useState<number | null>(null);

  const handleNext = () => {
    setActiveStep((prevActiveStep) => prevActiveStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevActiveStep) => prevActiveStep - 1);
  };

  const handleReset = () => {
    setActiveStep(0);
    setScheduleName('');
    setScheduleDescription('');
    setCsvFile(null);
    setSelectedStrategy(null);
    setConfig({});
    setProgressStatus('idle');
    setError('');
    setCreatedScheduleId(null);
  };

  const handleFileUpload = (file: File) => {
    setCsvFile(file);
    setError('');
  };

  const handleFileRemove = () => {
    setCsvFile(null);
  };

  const handleStrategySelect = (strategy: StrategyType) => {
    setSelectedStrategy(strategy);
  };

  const handleConfigChange = (newConfig: Record<string, unknown>) => {
    setConfig(newConfig);
  };

  const handleSubmit = async () => {
    if (!csvFile || !selectedStrategy) {
      setError('Please complete all required fields');
      return;
    }

    const name = scheduleName.trim() || `Schedule ${new Date().toISOString().split('T')[0]}`;

    try {
      setProgressStatus('uploading');
      setActiveStep(4); // Move to completion step

      const schedule = await createSchedule({
        name,
        description: scheduleDescription,
        strategy: selectedStrategy,
        config,
        csv_file: csvFile,
      });

      setProgressStatus('completed');
      setCreatedScheduleId(schedule.id);
    } catch (err: any) {
      setProgressStatus('error');
      console.error('Schedule creation failed:', err);
      console.error('Error response:', err.response?.data);

      // Extract detailed error message
      let errorMessage = 'Failed to create schedule';
      if (err.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMessage = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          errorMessage = err.response.data.detail.map((e: any) => e.msg).join(', ');
        } else {
          errorMessage = JSON.stringify(err.response.data.detail);
        }
      } else if (err.message) {
        errorMessage = err.message;
      }

      setError(errorMessage);
    }
  };

  const canProceed = () => {
    switch (activeStep) {
      case 0:
        return csvFile !== null;
      case 1:
        return selectedStrategy !== null;
      case 2:
        return true; // Config has defaults
      case 3:
        return true;
      default:
        return false;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Create New Schedule
        </Typography>
        <Button variant="outlined" onClick={() => navigate('/schedules')}>
          Cancel
        </Button>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {activeStep >= steps.length && progressStatus === 'completed' ? (
          <Box>
            <Typography sx={{ mt: 2, mb: 1 }}>
              All steps completed - schedule created successfully!
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
              <Box sx={{ flex: '1 1 auto' }} />
              <Button onClick={handleReset}>Create Another</Button>
              {createdScheduleId && (
                <Button
                  variant="contained"
                  onClick={() => navigate(`/schedules/${createdScheduleId}`)}
                  sx={{ ml: 1 }}
                >
                  View Schedule
                </Button>
              )}
              <Button onClick={() => navigate('/schedules')} sx={{ ml: 1 }}>
                All Schedules
              </Button>
            </Box>
          </Box>
        ) : (
          <Box>
            <Box sx={{ minHeight: 400, mb: 3 }}>
              {activeStep === 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Step 1: Upload CSV Data
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Upload a CSV file containing your lot data. The file should have columns: lot_id, num_units, fill_time, etc.
                  </Typography>
                  <CsvUpload
                    onFileUpload={handleFileUpload}
                    onFileRemove={handleFileRemove}
                    uploadedFile={csvFile}
                    error={error}
                  />
                  {csvFile && (
                    <Box sx={{ mt: 3 }}>
                      <DataPreview file={csvFile} />
                    </Box>
                  )}
                </Box>
              )}

              {activeStep === 1 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Step 2: Select Scheduling Strategy
                  </Typography>
                  <StrategySelector
                    selectedStrategy={selectedStrategy}
                    onStrategySelect={handleStrategySelect}
                  />
                </Box>
              )}

              {activeStep === 2 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Step 3: Configure Parameters
                  </Typography>
                  <ConfigEditor
                    strategy={selectedStrategy}
                    config={config}
                    onConfigChange={handleConfigChange}
                  />
                </Box>
              )}

              {activeStep === 3 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Step 4: Review and Create
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                    Review your settings and create the schedule.
                  </Typography>

                  <Box sx={{ mb: 3 }}>
                    <TextField
                      fullWidth
                      label="Schedule Name"
                      value={scheduleName}
                      onChange={(e) => setScheduleName(e.target.value)}
                      placeholder="Optional - auto-generated if empty"
                      sx={{ mb: 2 }}
                    />
                    <TextField
                      fullWidth
                      label="Description"
                      value={scheduleDescription}
                      onChange={(e) => setScheduleDescription(e.target.value)}
                      multiline
                      rows={2}
                      placeholder="Optional description"
                    />
                  </Box>

                  <Paper sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="subtitle2" fontWeight="bold" gutterBottom>
                      Summary:
                    </Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <Typography variant="body2">
                        <strong>File:</strong> {csvFile?.name}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Strategy:</strong> {selectedStrategy}
                      </Typography>
                      <Typography variant="body2">
                        <strong>Configuration:</strong> {JSON.stringify(config, null, 2)}
                      </Typography>
                    </Box>
                  </Paper>
                </Box>
              )}

              {activeStep === 4 && (
                <ProgressIndicator
                  status={progressStatus}
                  error={error}
                />
              )}
            </Box>

            <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
              <Button
                color="inherit"
                disabled={activeStep === 0}
                onClick={handleBack}
                sx={{ mr: 1 }}
              >
                Back
              </Button>
              <Box sx={{ flex: '1 1 auto' }} />
              {activeStep < 3 ? (
                <Button onClick={handleNext} disabled={!canProceed()}>
                  Next
                </Button>
              ) : (
                <Button
                  variant="contained"
                  onClick={handleSubmit}
                  disabled={progressStatus === 'uploading' || progressStatus === 'scheduling'}
                >
                  Create Schedule
                </Button>
              )}
            </Box>
          </Box>
        )}
      </Paper>
    </Container>
  );
};
