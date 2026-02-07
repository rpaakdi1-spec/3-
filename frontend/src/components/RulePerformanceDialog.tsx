import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  Speed as SpeedIcon,
  CheckCircle as SuccessIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';

interface RulePerformanceDialogProps {
  open: boolean;
  onClose: () => void;
  ruleId: number;
  ruleName: string;
  onLoadPerformance: (ruleId: number) => Promise<any>;
}

export const RulePerformanceDialog: React.FC<RulePerformanceDialogProps> = ({
  open,
  onClose,
  ruleId,
  ruleName,
  onLoadPerformance,
}) => {
  const [performance, setPerformance] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) {
      loadPerformance();
    }
  }, [open]);

  const loadPerformance = async () => {
    setLoading(true);
    try {
      const data = await onLoadPerformance(ruleId);
      setPerformance(data);
    } catch (error) {
      console.error('Failed to load performance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const MetricCard = ({ title, value, icon, color }: any) => (
    <Card variant="outlined">
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" fontWeight="bold" color={color}>
              {value}
            </Typography>
          </Box>
          <Box sx={{ color, fontSize: 40 }}>{icon}</Box>
        </Box>
      </CardContent>
    </Card>
  );

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <TimelineIcon color="primary" />
          <Typography variant="h6">Performance Metrics: {ruleName}</Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        {loading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : performance ? (
          <Box>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={6}>
                <MetricCard
                  title="Total Executions"
                  value={performance.total_executions || 0}
                  icon={<TimelineIcon />}
                  color="primary.main"
                />
              </Grid>
              <Grid item xs={6}>
                <MetricCard
                  title="Success Rate"
                  value={`${((performance.success_rate || 0) * 100).toFixed(1)}%`}
                  icon={<SuccessIcon />}
                  color="success.main"
                />
              </Grid>
              <Grid item xs={6}>
                <MetricCard
                  title="Avg Execution Time"
                  value={`${performance.avg_execution_time_ms || 0}ms`}
                  icon={<SpeedIcon />}
                  color="info.main"
                />
              </Grid>
              <Grid item xs={6}>
                <MetricCard
                  title="Performance Score"
                  value={performance.performance_score?.toFixed(1) || 'N/A'}
                  icon={<TrendingUpIcon />}
                  color="warning.main"
                />
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Detailed Statistics
            </Typography>

            <Box sx={{ bgcolor: 'grey.50', p: 2, borderRadius: 1 }}>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Successes:
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {performance.successful_executions || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Failures:
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {performance.failed_executions || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Min Execution Time:
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {performance.min_execution_time_ms || 0}ms
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Max Execution Time:
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {performance.max_execution_time_ms || 0}ms
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary">
                    Last Executed:
                  </Typography>
                  <Typography variant="body1" fontWeight="medium">
                    {performance.last_executed_at
                      ? new Date(performance.last_executed_at).toLocaleString('ko-KR')
                      : 'Never'}
                  </Typography>
                </Grid>
              </Grid>
            </Box>

            {performance.recent_trend && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Recent Trend:
                </Typography>
                <Typography variant="body1">
                  {performance.recent_trend === 'improving' && '📈 Improving'}
                  {performance.recent_trend === 'stable' && '➡️ Stable'}
                  {performance.recent_trend === 'declining' && '📉 Declining'}
                </Typography>
              </Box>
            )}
          </Box>
        ) : (
          <Box p={4} textAlign="center">
            <Typography color="text.secondary">No performance data available</Typography>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        <Button variant="outlined" onClick={loadPerformance}>
          Refresh
        </Button>
      </DialogActions>
    </Dialog>
  );
};
