import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Pagination,
  CircularProgress,
} from '@mui/material';
import {
  History as HistoryIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  AccessTime as TimeIcon,
} from '@mui/icons-material';

interface RuleLogsDialogProps {
  open: boolean;
  onClose: () => void;
  ruleId: number;
  ruleName: string;
  onLoadLogs: (ruleId: number, params: any) => Promise<any[]>;
}

export const RuleLogsDialog: React.FC<RuleLogsDialogProps> = ({
  open,
  onClose,
  ruleId,
  ruleName,
  onLoadLogs,
}) => {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const pageSize = 10;

  useEffect(() => {
    if (open) {
      loadLogs();
    }
  }, [open, page, statusFilter]);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params = {
        skip: (page - 1) * pageSize,
        limit: pageSize,
        status: statusFilter !== 'all' ? statusFilter : undefined,
      };
      const data = await onLoadLogs(ruleId, params);
      setLogs(data);
    } catch (error) {
      console.error('Failed to load logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusChip = (status: string) => {
    switch (status) {
      case 'success':
        return <Chip label="Success" color="success" size="small" icon={<SuccessIcon />} />;
      case 'failure':
        return <Chip label="Failure" color="error" size="small" icon={<ErrorIcon />} />;
      default:
        return <Chip label={status} size="small" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <HistoryIcon color="primary" />
          <Typography variant="h6">Rule Execution Logs: {ruleName}</Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Status Filter</InputLabel>
            <Select
              value={statusFilter}
              label="Status Filter"
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setPage(1);
              }}
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="success">Success</MenuItem>
              <MenuItem value="failure">Failure</MenuItem>
            </Select>
          </FormControl>

          <Button variant="outlined" size="small" onClick={loadLogs}>
            Refresh
          </Button>
        </Box>

        {loading ? (
          <Box display="flex" justifyContent="center" p={4}>
            <CircularProgress />
          </Box>
        ) : logs.length === 0 ? (
          <Box p={4} textAlign="center">
            <Typography color="text.secondary">No logs found</Typography>
          </Box>
        ) : (
          <>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Order ID</TableCell>
                    <TableCell>Execution Time</TableCell>
                    <TableCell>Result</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {logs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell>
                        <Box display="flex" alignItems="center" gap={0.5}>
                          <TimeIcon fontSize="small" />
                          <Typography variant="body2">
                            {formatDate(log.executed_at || log.created_at)}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{getStatusChip(log.status)}</TableCell>
                      <TableCell>
                        <Typography variant="body2">{log.order_id || '-'}</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{log.execution_time_ms}ms</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography
                          variant="body2"
                          sx={{
                            maxWidth: 300,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                          }}
                        >
                          {JSON.stringify(log.result || log.actions_taken)}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            <Box display="flex" justifyContent="center" mt={2}>
              <Pagination
                count={Math.ceil(logs.length / pageSize) || 1}
                page={page}
                onChange={(e, value) => setPage(value)}
                color="primary"
              />
            </Box>
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};
