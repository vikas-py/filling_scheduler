import {
  Box,
  Typography,
  TextField,
  Paper,
  Divider,
  Stack,
  IconButton,
  Button,
} from '@mui/material';
import { Add, Delete } from '@mui/icons-material';
import { useState } from 'react';

interface Filler {
  id: number;
  name: string;
  capacity: number;
  maxConcurrent: number;
}

interface FillerSettingsProps {
  onChange?: () => void;
}

export const FillerSettings = ({ onChange }: FillerSettingsProps) => {
  const [fillers, setFillers] = useState<Filler[]>([
    { id: 1, name: 'Filler 1', capacity: 100, maxConcurrent: 5 },
    { id: 2, name: 'Filler 2', capacity: 100, maxConcurrent: 5 },
    { id: 3, name: 'Filler 3', capacity: 100, maxConcurrent: 5 },
    { id: 4, name: 'Filler 4', capacity: 100, maxConcurrent: 5 },
  ]);

  const handleAddFiller = () => {
    const newId = Math.max(...fillers.map((f) => f.id)) + 1;
    setFillers([
      ...fillers,
      { id: newId, name: `Filler ${newId}`, capacity: 100, maxConcurrent: 5 },
    ]);
    if (onChange) onChange();
  };

  const handleRemoveFiller = (id: number) => {
    if (fillers.length <= 1) {
      alert('At least one filler must be configured');
      return;
    }
    setFillers(fillers.filter((f) => f.id !== id));
    if (onChange) onChange();
  };

  const handleFillerChange = (id: number, field: keyof Filler, value: string) => {
    setFillers(
      fillers.map((f) =>
        f.id === id
          ? { ...f, [field]: field === 'name' ? value : parseFloat(value) || 0 }
          : f
      )
    );
    if (onChange) onChange();
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h6" gutterBottom>
            Filler Configuration
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Configure individual filling machines, their capacities, and constraints.
          </Typography>
        </Box>
        <Button startIcon={<Add />} variant="contained" onClick={handleAddFiller}>
          Add Filler
        </Button>
      </Box>

      <Typography variant="body2" color="info.main" sx={{ mb: 3, p: 2, bgcolor: 'info.lighter', borderRadius: 1 }}>
        Total Fillers: <strong>{fillers.length}</strong> | Total Capacity:{' '}
        <strong>{fillers.reduce((sum, f) => sum + f.capacity, 0)} units</strong>
      </Typography>

      <Stack spacing={2}>
        {fillers.map((filler, index) => (
          <Paper key={filler.id} sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="subtitle1" fontWeight="bold">
                Filler {index + 1}
              </Typography>
              <IconButton
                color="error"
                onClick={() => handleRemoveFiller(filler.id)}
                disabled={fillers.length <= 1}
              >
                <Delete />
              </IconButton>
            </Box>
            <Divider sx={{ mb: 2 }} />

            <Stack spacing={2}>
              <TextField
                fullWidth
                label="Filler Name"
                value={filler.name}
                onChange={(e) => handleFillerChange(filler.id, 'name', e.target.value)}
                helperText="Custom name for this filler"
              />

              <TextField
                fullWidth
                label="Capacity (units)"
                type="number"
                value={filler.capacity}
                onChange={(e) => handleFillerChange(filler.id, 'capacity', e.target.value)}
                helperText="Maximum number of units this filler can handle"
                InputProps={{ inputProps: { min: 1 } }}
              />

              <TextField
                fullWidth
                label="Max Concurrent Lots"
                type="number"
                value={filler.maxConcurrent}
                onChange={(e) => handleFillerChange(filler.id, 'maxConcurrent', e.target.value)}
                helperText="Maximum number of lots that can be processed simultaneously"
                InputProps={{ inputProps: { min: 1 } }}
              />
            </Stack>
          </Paper>
        ))}
      </Stack>

      {/* Global Filler Settings */}
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
          Global Settings
        </Typography>
        <Divider sx={{ mb: 2 }} />

        <Stack spacing={2}>
          <TextField
            fullWidth
            label="Default Setup Time (hours)"
            type="number"
            defaultValue={0.5}
            helperText="Time required to set up each filler before starting"
            onChange={() => onChange && onChange()}
            InputProps={{ inputProps: { min: 0, step: 0.1 } }}
          />

          <TextField
            fullWidth
            label="Default Changeover Time (hours)"
            type="number"
            defaultValue={0.25}
            helperText="Time required between lot changes"
            onChange={() => onChange && onChange()}
            InputProps={{ inputProps: { min: 0, step: 0.1 } }}
          />

          <TextField
            fullWidth
            label="Maintenance Window (hours/day)"
            type="number"
            defaultValue={1}
            helperText="Daily downtime for maintenance"
            onChange={() => onChange && onChange()}
            InputProps={{ inputProps: { min: 0, step: 0.5 } }}
          />
        </Stack>
      </Paper>
    </Box>
  );
};
