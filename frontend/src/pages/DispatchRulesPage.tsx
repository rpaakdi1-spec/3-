import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as TestIcon,
  TrendingUp as StatsIcon,
  ToggleOn,
  ToggleOff
} from '@mui/icons-material';
import { DispatchRulesAPI, DispatchRule, CreateRulePayload } from '../api/dispatch-rules';

const DispatchRulesPage: React.FC = () => {
  const [rules, setRules] = useState<DispatchRule[]>([]);
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedRule, setSelectedRule] = useState<DispatchRule | null>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  
  const [formData, setFormData] = useState<CreateRulePayload>({
    name: '',
    description: '',
    rule_type: 'assignment',
    priority: 50,
    conditions: {},
    actions: {}
  });

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    setLoading(true);
    try {
      const data = await DispatchRulesAPI.list();
      setRules(data);
    } catch (error) {
      showSnackbar('Failed to load rules', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    try {
      await DispatchRulesAPI.create(formData);
      showSnackbar('Rule created successfully', 'success');
      setOpenDialog(false);
      loadRules();
    } catch (error) {
      showSnackbar('Failed to create rule', 'error');
    }
  };

  const handleToggle = async (ruleId: number, isActive: boolean) => {
    try {
      if (isActive) {
        await DispatchRulesAPI.deactivate(ruleId);
      } else {
        await DispatchRulesAPI.activate(ruleId);
      }
      showSnackbar(`Rule ${isActive ? 'deactivated' : 'activated'}`, 'success');
      loadRules();
    } catch (error) {
      showSnackbar('Failed to toggle rule', 'error');
    }
  };

  const handleDelete = async (ruleId: number) => {
    if (confirm('Are you sure you want to delete this rule?')) {
      try {
        await DispatchRulesAPI.delete(ruleId);
        showSnackbar('Rule deleted', 'success');
        loadRules();
      } catch (error) {
        showSnackbar('Failed to delete rule', 'error');
      }
    }
  };

  const showSnackbar = (message: string, severity: 'success' | 'error') => {
    setSnackbar({ open: true, message, severity });
  };

  const getRuleTypeColor = (type: string) => {
    switch (type) {
      case 'assignment': return 'primary';
      case 'constraint': return 'warning';
      case 'optimization': return 'success';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Dispatch Rules</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Create Rule
        </Button>
      </Box>

      <Grid container spacing={3}>
        {rules.map((rule) => (
          <Grid item xs={12} md={6} key={rule.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6">{rule.name}</Typography>
                  <Box>
                    <IconButton
                      size="small"
                      onClick={() => handleToggle(rule.id, rule.is_active)}
                      color={rule.is_active ? 'primary' : 'default'}
                    >
                      {rule.is_active ? <ToggleOn /> : <ToggleOff />}
                    </IconButton>
                    <IconButton size="small" color="error" onClick={() => handleDelete(rule.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {rule.description || 'No description'}
                </Typography>

                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Chip label={rule.rule_type} color={getRuleTypeColor(rule.rule_type)} size="small" />
                  <Chip label={`Priority: ${rule.priority}`} size="small" variant="outlined" />
                  <Chip label={`v${rule.version}`} size="small" />
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="caption" color="text.secondary">
                    Executions: {rule.execution_count} | Success: {((rule.success_rate || 0) * 100).toFixed(1)}%
                  </Typography>
                  <Button size="small" startIcon={<TestIcon />}>
                    Test
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Create/Edit Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Rule</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Rule Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Rule Type</InputLabel>
                <Select
                  value={formData.rule_type}
                  onChange={(e) => setFormData({ ...formData, rule_type: e.target.value })}
                >
                  <MenuItem value="assignment">Assignment</MenuItem>
                  <MenuItem value="constraint">Constraint</MenuItem>
                  <MenuItem value="optimization">Optimization</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                type="number"
                label="Priority"
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
              />
            </Grid>
            <Grid item xs={12}>
              <Alert severity="info">
                Use the Visual Rule Builder (coming soon) or edit JSON directly
              </Alert>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreate} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity}>{snackbar.message}</Alert>
      </Snackbar>
    </Box>
  );
};

export default DispatchRulesPage;
