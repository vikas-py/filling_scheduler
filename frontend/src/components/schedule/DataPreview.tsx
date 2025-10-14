import { useEffect, useState } from 'react';
import Papa from 'papaparse';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import { CheckCircle, Error as ErrorIcon } from '@mui/icons-material';

interface DataPreviewProps {
  file: File | null;
  onDataParsed?: (data: unknown[], headers: string[]) => void;
}

interface ParsedData {
  headers: string[];
  rows: Record<string, unknown>[];
  totalRows: number;
  errors: string[];
}

export const DataPreview = ({ file, onDataParsed }: DataPreviewProps) => {
  const [parsedData, setParsedData] = useState<ParsedData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!file) {
      setParsedData(null);
      return;
    }

    setLoading(true);

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      preview: 20, // Only parse first 20 rows for preview
      complete: (results) => {
        const headers = results.meta.fields || [];
        const rows = results.data as Record<string, unknown>[];
        const errors: string[] = [];

        // Validate required columns
        const requiredColumns = ['lot_id', 'num_units', 'fill_time'];
        const missingColumns = requiredColumns.filter((col) => !headers.includes(col));

        if (missingColumns.length > 0) {
          errors.push(`Missing required columns: ${missingColumns.join(', ')}`);
        }

        // Count total rows (estimate from file size)
        const estimatedTotalRows = rows.length;

        setParsedData({
          headers,
          rows,
          totalRows: estimatedTotalRows,
          errors,
        });

        if (onDataParsed && errors.length === 0) {
          onDataParsed(rows, headers);
        }

        setLoading(false);
      },
      error: (error) => {
        setParsedData({
          headers: [],
          rows: [],
          totalRows: 0,
          errors: [`Failed to parse CSV: ${error.message}`],
        });
        setLoading(false);
      },
    });
  }, [file, onDataParsed]);

  if (!file) {
    return (
      <Alert severity="info">
        Upload a CSV file to preview the data.
      </Alert>
    );
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', p: 4 }}>
        <CircularProgress />
        <Typography sx={{ ml: 2 }}>Parsing CSV file...</Typography>
      </Box>
    );
  }

  if (!parsedData) {
    return null;
  }

  return (
    <Box>
      {parsedData.errors.length > 0 ? (
        <Alert severity="error" icon={<ErrorIcon />} sx={{ mb: 2 }}>
          <Typography variant="subtitle2" fontWeight="bold">
            Validation Errors:
          </Typography>
          <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
            {parsedData.errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </Alert>
      ) : (
        <Alert severity="success" icon={<CheckCircle />} sx={{ mb: 2 }}>
          CSV file is valid! Showing preview of first {parsedData.rows.length} rows.
          {parsedData.totalRows > parsedData.rows.length && (
            <> (Total rows: ~{parsedData.totalRows})</>
          )}
        </Alert>
      )}

      <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
        <Chip label={`${parsedData.totalRows} rows`} color="primary" size="small" />
        <Chip label={`${parsedData.headers.length} columns`} color="primary" size="small" />
      </Box>

      <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              {parsedData.headers.map((header) => (
                <TableCell key={header} sx={{ fontWeight: 'bold', backgroundColor: 'grey.100' }}>
                  {header}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {parsedData.rows.map((row, index) => (
              <TableRow key={index} hover>
                {parsedData.headers.map((header) => (
                  <TableCell key={header}>
                    {String(row[header] ?? '')}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};
