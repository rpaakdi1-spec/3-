import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  TextField,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import {
  Science as SimulationIcon,
  PlayArrow as RunIcon,
  Timeline as ResultsIcon,
} from '@mui/icons-material';

interface RuleSimulationDialogProps {
  open: boolean;
  onClose: () => void;
  onSimulate: (scenarioData: any) => Promise<any>;
}

export const RuleSimulationDialog: React.FC<RuleSimulationDialogProps> = ({
  open,
  onClose,
  onSimulate,
}) => {
  const [scenarioData, setScenarioData] = useState<string>(
    '{\n  "orders": [\n    { "id": 1, "priority": "high", "distance_km": 5 },\n    { "id": 2, "priority": "normal", "distance_km": 10 }\n  ],\n  "drivers": [\n    { "id": 1, "rating": 4.8, "available": true },\n    { "id": 2, "rating": 4.5, "available": true }\n  ]\n}'
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSimulate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const parsedData = JSON.parse(scenarioData);
      const simulationResult = await onSimulate(parsedData);
      setResult(simulationResult);
    } catch (err: any) {
      setError(err.message || 'Failed to run simulation');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setResult(null);
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <SimulationIcon color="primary" />
          <Typography variant="h6">Rule Simulation</Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Alert severity="info" sx={{ mb: 2 }}>
          Test how your rules would perform against different scenarios before applying them in production.
        </Alert>

        <Box sx={{ mb: 3 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Scenario Data (JSON):
          </Typography>
          <TextField
            fullWidth
            multiline
            rows={12}
            value={scenarioData}
            onChange={(e) => setScenarioData(e.target.value)}
            placeholder="Enter scenario data"
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
            <Box display="flex" alignItems="center" gap={1} mb={2}>
              <ResultsIcon color="primary" />
              <Typography variant="subtitle1" fontWeight="bold">
                Simulation Results
              </Typography>
            </Box>

            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="body2" color="text.secondary">
                      Rules Applied
                    </Typography>
                    <Typography variant="h5" fontWeight="bold" color="primary.main">
                      {result.rules_applied || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="body2" color="text.secondary">
                      Orders Matched
                    </Typography>
                    <Typography variant="h5" fontWeight="bold" color="success.main">
                      {result.orders_matched || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={4}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="body2" color="text.secondary">
                      Total Time
                    </Typography>
                    <Typography variant="h5" fontWeight="bold" color="info.main">
                      {result.execution_time_ms || 0}ms
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1, mb: 2 }}>
              <Typography variant="body2" fontWeight="medium" gutterBottom>
                Detailed Results:
              </Typography>
              <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                {JSON.stringify(result, null, 2)}
              </Typography>
            </Box>

            {result.recommendations && result.recommendations.length > 0 && (
              <Box>
                <Typography variant="body2" fontWeight="medium" gutterBottom>
                  Recommendations:
                </Typography>
                {result.recommendations.map((rec: string, idx: number) => (
                  <Chip
                    key={idx}
                    label={rec}
                    size="small"
                    sx={{ mr: 1, mb: 1 }}
                    color="warning"
                  />
                ))}
              </Box>
            )}
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={handleClose}>Close</Button>
        <Button
          variant="contained"
          startIcon={loading ? <CircularProgress size={16} /> : <RunIcon />}
          onClick={handleSimulate}
          disabled={loading}
        >
          {loading ? 'Running...' : 'Run Simulation'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
