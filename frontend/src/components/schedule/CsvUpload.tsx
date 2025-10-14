import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Box, Typography, Paper, Alert, Chip, IconButton } from '@mui/material';
import { CloudUpload, Delete, CheckCircle } from '@mui/icons-material';

interface CsvUploadProps {
  onFileUpload: (file: File) => void;
  onFileRemove: () => void;
  uploadedFile: File | null;
  error?: string;
}

export const CsvUpload = ({ onFileUpload, onFileRemove, uploadedFile, error }: CsvUploadProps) => {
  const [dragError, setDragError] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      setDragError(null);

      if (acceptedFiles.length === 0) {
        setDragError('Please upload a CSV file');
        return;
      }

      const file = acceptedFiles[0];

      // Check file size (max 10MB)
      const maxSize = 10 * 1024 * 1024;
      if (file.size > maxSize) {
        setDragError('File size must be less than 10MB');
        return;
      }

      // Check file extension
      if (!file.name.toLowerCase().endsWith('.csv')) {
        setDragError('Only CSV files are allowed');
        return;
      }

      onFileUpload(file);
    },
    [onFileUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.ms-excel': ['.csv'],
    },
    multiple: false,
    maxSize: 10 * 1024 * 1024,
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <Box>
      {!uploadedFile ? (
        <Paper
          {...getRootProps()}
          sx={{
            p: 4,
            border: '2px dashed',
            borderColor: isDragActive ? 'primary.main' : dragError || error ? 'error.main' : 'grey.300',
            backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
            cursor: 'pointer',
            textAlign: 'center',
            transition: 'all 0.2s ease',
            '&:hover': {
              borderColor: 'primary.main',
              backgroundColor: 'action.hover',
            },
          }}
        >
          <input {...getInputProps()} />
          <CloudUpload sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive ? 'Drop the file here...' : 'Drag & drop CSV file here'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            or click to browse files
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Maximum file size: 10MB
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Required columns: <strong>Lot ID</strong>, <strong>Type</strong>, <strong>Vials</strong>
          </Typography>
        </Paper>
      ) : (
        <Paper sx={{ p: 3, border: '1px solid', borderColor: 'success.main' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CheckCircle color="success" sx={{ fontSize: 32 }} />
              <Box>
                <Typography variant="subtitle1" fontWeight="bold">
                  {uploadedFile.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {formatFileSize(uploadedFile.size)}
                </Typography>
              </Box>
              <Chip label="CSV" color="primary" size="small" />
            </Box>
            <IconButton color="error" onClick={onFileRemove}>
              <Delete />
            </IconButton>
          </Box>
        </Paper>
      )}

      {(dragError || error) && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {dragError || error}
        </Alert>
      )}

      {uploadedFile && !error && (
        <Alert severity="info" sx={{ mt: 2 }}>
          File uploaded successfully. Continue to preview the data.
        </Alert>
      )}
    </Box>
  );
};
