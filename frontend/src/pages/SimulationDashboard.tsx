import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  TextField,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  CompareArrows as CompareIcon,
} from '@mui/icons-material';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface SimulationResult {
  total_dispatches: number;
  simulation_period: {
    start: string;
    end: string;
  };
  original_metrics: {
    total_distance_km: number;
    avg_distance_km: number;
    total_cost: number;
    avg_cost: number;
    completion_rate: number;
  };
  simulated_metrics: {
    total_distance_km: number;
    avg_distance_km: number;
    total_cost: number;
    avg_cost: number;
    completion_rate: number;
  };
  improvements: {
    distance_saved_km: number;
    distance_saved_pct: number;
    cost_saved: number;
    cost_saved_pct: number;
    time_saved_minutes: number;
  };
}

export const SimulationDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  
  // Historical Simulation
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  
  // What-If Simulation
  const [scenarioName, setScenarioName] = useState('');
  const [scenarioDescription, setScenarioDescription] = useState('');
  
  // A/B Testing
  const [ruleAId, setRuleAId] = useState('');
  const [ruleBId, setRuleBId] = useState('');
  const [testDuration, setTestDuration] = useState(7);

  const handleRunHistoricalSimulation = async () => {
    setLoading(true);
    try {
      // Call API to run historical simulation
      const response = await fetch('/api/v1/dispatch-rules/simulation/historical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          start_date: startDate,
          end_date: endDate,
        }),
      });
      const result = await response.json();
      setSimulationResult(result);
    } catch (error) {
      console.error('Simulation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRunWhatIfSimulation = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/dispatch-rules/simulation/whatif', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scenario_name: scenarioName,
          scenario_description: scenarioDescription,
          sample_size: 100,
        }),
      });
      const result = await response.json();
      setSimulationResult(result);
    } catch (error) {
      console.error('Simulation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRunABTest = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/dispatch-rules/simulation/ab-test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rule_a_id: parseInt(ruleAId),
          rule_b_id: parseInt(ruleBId),
          test_duration_days: testDuration,
          traffic_split: 0.5,
        }),
      });
      const result = await response.json();
      setSimulationResult(result);
    } catch (error) {
      console.error('A/B test error:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderMetricsComparison = () => {
    if (!simulationResult) return null;

    return (
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Original Metrics
              </Typography>
              <MetricsTable metrics={simulationResult.original_metrics} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Simulated Metrics
              </Typography>
              <MetricsTable metrics={simulationResult.simulated_metrics} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Improvements
              </Typography>
              <ImprovementsDisplay improvements={simulationResult.improvements} />
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Comparison
              </Typography>
              <ComparisonChart
                original={simulationResult.original_metrics}
                simulated={simulationResult.simulated_metrics}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Rule Simulation & Testing
      </Typography>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
          <Tab label="Historical Simulation" />
          <Tab label="What-If Analysis" />
          <Tab label="A/B Testing" />
        </Tabs>
      </Paper>

      {/* Historical Simulation Tab */}
      {activeTab === 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Historical Data Replay
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Replay historical dispatches with current rules to see potential improvements
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Start Date"
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="End Date"
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                fullWidth
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <PlayIcon />}
                onClick={handleRunHistoricalSimulation}
                disabled={loading || !startDate || !endDate}
                sx={{ height: '56px' }}
              >
                Run Simulation
              </Button>
            </Grid>
          </Grid>
          {renderMetricsComparison()}
        </Paper>
      )}

      {/* What-If Analysis Tab */}
      {activeTab === 1 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            What-If Scenario Analysis
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Test different scenarios with modified parameters
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Scenario Name"
                value={scenarioName}
                onChange={(e) => setScenarioName(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Scenario Description"
                multiline
                rows={3}
                value={scenarioDescription}
                onChange={(e) => setScenarioDescription(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <PlayIcon />}
                onClick={handleRunWhatIfSimulation}
                disabled={loading || !scenarioName}
              >
                Run What-If Analysis
              </Button>
            </Grid>
          </Grid>
          {renderMetricsComparison()}
        </Paper>
      )}

      {/* A/B Testing Tab */}
      {activeTab === 2 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            A/B Testing
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Compare two rules to determine which performs better
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Rule A ID (Control)"
                type="number"
                value={ruleAId}
                onChange={(e) => setRuleAId(e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Rule B ID (Treatment)"
                type="number"
                value={ruleBId}
                onChange={(e) => setRuleBId(e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Test Duration (days)"
                type="number"
                value={testDuration}
                onChange={(e) => setTestDuration(parseInt(e.target.value))}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <CompareIcon />}
                onClick={handleRunABTest}
                disabled={loading || !ruleAId || !ruleBId}
              >
                Run A/B Test
              </Button>
            </Grid>
          </Grid>
          {renderMetricsComparison()}
        </Paper>
      )}
    </Box>
  );
};

const MetricsTable: React.FC<{ metrics: any }> = ({ metrics }) => (
  <TableContainer>
    <Table size="small">
      <TableBody>
        {Object.entries(metrics).map(([key, value]) => (
          <TableRow key={key}>
            <TableCell>{formatMetricName(key)}</TableCell>
            <TableCell align="right">
              {typeof value === 'number' ? value.toFixed(2) : String(value)}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  </TableContainer>
);

const ImprovementsDisplay: React.FC<{ improvements: any }> = ({ improvements }) => (
  <Grid container spacing={2}>
    {Object.entries(improvements).map(([key, value]) => {
      const isPositive = typeof value === 'number' && value > 0;
      return (
        <Grid item xs={12} sm={6} md={4} key={key}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {isPositive ? (
              <TrendingUpIcon color="success" />
            ) : (
              <TrendingDownIcon color="error" />
            )}
            <Box>
              <Typography variant="caption" color="text.secondary">
                {formatMetricName(key)}
              </Typography>
              <Typography
                variant="h6"
                color={isPositive ? 'success.main' : 'error.main'}
              >
                {typeof value === 'number' ? value.toFixed(2) : String(value)}
              </Typography>
            </Box>
          </Box>
        </Grid>
      );
    })}
  </Grid>
);

const ComparisonChart: React.FC<{ original: any; simulated: any }> = ({
  original,
  simulated,
}) => {
  const data = {
    labels: Object.keys(original),
    datasets: [
      {
        label: 'Original',
        data: Object.values(original),
        backgroundColor: 'rgba(59, 130, 246, 0.5)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1,
      },
      {
        label: 'Simulated',
        data: Object.values(simulated),
        backgroundColor: 'rgba(16, 185, 129, 0.5)',
        borderColor: 'rgb(16, 185, 129)',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: false,
      },
    },
  };

  return <Bar data={data} options={options} />;
};

function formatMetricName(key: string): string {
  return key
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (l) => l.toUpperCase());
}
