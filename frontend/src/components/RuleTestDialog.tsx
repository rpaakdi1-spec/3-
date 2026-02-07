import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  Alert,
  CircularProgress,
  Chip,
  Divider,
} from '@mui/material';
import {
  PlayArrow as TestIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

interface RuleTestDialogProps {
  open: boolean;
  onClose: () => void;
  ruleId: number;
  ruleName: string;
  onTest: (ruleId: number, testData: any) => Promise<any>;
}

export const RuleTestDialog: React.FC<RuleTestDialogProps> = ({
  open,
  onClose,
  ruleId,
  ruleName,
  onTest,
}) => {
  const [testData, setTestData] = useState<string>('{\n  "order_id": 123,\n  "driver_rating": 4.8,\n  "distance_km": 3.5\n}');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTest = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const parsedData = JSON.parse(testData);
      const testResult = await onTest(ruleId, parsedData);
      setResult(testResult);
    } catch (err: any) {
      setError(err.message || 'Failed to test rule');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setTestData('{\n  "order_id": 123,\n  "driver_rating": 4.8,\n  "distance_km": 3.5\n}');
    setResult(null);
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <TestIcon color="primary" />
          <Typography variant="h6">Test Rule: {ruleName}</Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Enter test data (JSON format):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={8}
            value={testData}
            onChange={(e) => setTestData(e.target.value)}
            placeholder="Enter test data as JSON"
            variant="outlined"
            sx={{ fontFamily: 'monospace' }}
          />
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {result && (
          <Box sx={{ mt: 2 }}>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="subtitle1" fontWeight="bold" sx={{ mb: 1 }}>
              Test Result:
            </Typography>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              {result.matched ? (
                <>
                  <SuccessIcon color="success" />
                  <Chip label="Rule Matched" color="success" size="small" />
                </>
              ) : (
                <>
                  <ErrorIcon color="error" />
                  <Chip label="Rule Not Matched" color="error" size="small" />
                </>
              )}
            </Box>

            <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1, mb: 2 }}>
              <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                {JSON.stringify(result, null, 2)}
              </Typography>
            </Box>

            {result.execution_time_ms && (
              <Typography variant="caption" color="text.secondary">
                Execution Time: {result.execution_time_ms}ms
              </Typography>
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>Close</Button>
        <Button
          variant="contained"
          startIcon={loading ? <CircularProgress size={16} /> : <TestIcon />}
          onClick={handleTest}
          disabled={loading}
        >
          {loading ? 'Testing...' : 'Run Test'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
