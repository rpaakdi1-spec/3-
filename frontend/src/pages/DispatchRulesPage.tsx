import React, { useState, useEffect } from 'react';
import Layout from '../components/common/Layout';
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
  Snackbar,
  Tabs,
  Tab,
  Menu,
  ListItemIcon,
  ListItemText
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as TestIcon,
  TrendingUp as StatsIcon,
  ToggleOn,
  ToggleOff,
  AccountTree as VisualIcon,
  MoreVert as MoreIcon,
  History as HistoryIcon,
  Science as SimulationIcon,
  CollectionsBookmark as TemplateIcon,
  Timeline as TimelineIcon
} from '@mui/icons-material';
import { DispatchRulesAPI, DispatchRule, CreateRulePayload } from '../api/dispatch-rules';
import { RuleBuilderCanvas } from '../components/RuleBuilderCanvas';
import { RuleTestDialog } from '../components/RuleTestDialog';
import { RuleLogsDialog } from '../components/RuleLogsDialog';
import { RulePerformanceDialog } from '../components/RulePerformanceDialog';
import { RuleSimulationDialog } from '../components/RuleSimulationDialog';
import { RuleTemplateGallery } from '../components/RuleTemplateGallery';
import { RuleVersionHistory } from '../components/RuleVersionHistory';

const DispatchRulesPage: React.FC = () => {
  const [rules, setRules] = useState<DispatchRule[]>([]);
  const [loading, setLoading] = useState(false);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedRule, setSelectedRule] = useState<DispatchRule | null>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });
  const [tabValue, setTabValue] = useState(0); // 0: Form, 1: Visual Builder
  
  // Dialog states
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  const [logsDialogOpen, setLogsDialogOpen] = useState(false);
  const [performanceDialogOpen, setPerformanceDialogOpen] = useState(false);
  const [simulationDialogOpen, setSimulationDialogOpen] = useState(false);
  const [templateGalleryOpen, setTemplateGalleryOpen] = useState(false);
  const [versionHistoryOpen, setVersionHistoryOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  
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

  const handleVisualBuilderSave = (ruleData: any) => {
    // Update formData with visual builder data
    setFormData({
      ...formData,
      conditions: ruleData.conditions,
      actions: ruleData.actions
    });
    showSnackbar('Rule configuration updated from visual builder', 'success');
  };

  // New handlers for advanced features
  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, rule: DispatchRule) => {
    setAnchorEl(event.currentTarget);
    setSelectedRule(rule);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleTestRule = () => {
    handleMenuClose();
    setTestDialogOpen(true);
  };

  const handleViewLogs = () => {
    handleMenuClose();
    setLogsDialogOpen(true);
  };

  const handleViewPerformance = () => {
    handleMenuClose();
    setPerformanceDialogOpen(true);
  };

  const handleViewVersionHistory = () => {
    handleMenuClose();
    setVersionHistoryOpen(true);
  };

  const handleSelectTemplate = (template: any) => {
    setFormData({
      name: template.name,
      description: template.description,
      rule_type: template.rule_type,
      priority: template.priority,
      conditions: template.conditions,
      actions: template.actions,
    });
    showSnackbar('Template loaded successfully', 'success');
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
    <Layout>
      <Box sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4">Dispatch Rules</Typography>
          <Box display="flex" gap={2}>
            <Button
              variant="outlined"
              startIcon={<SimulationIcon />}
              onClick={() => setSimulationDialogOpen(true)}
            >
              Simulation
            </Button>
            <Button
              variant="outlined"
              startIcon={<TemplateIcon />}
              onClick={() => setTemplateGalleryOpen(true)}
            >
              Templates
            </Button>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenDialog(true)}
            >
              Create Rule
            </Button>
          </Box>
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
                    <IconButton 
                      size="small" 
                      onClick={(e) => handleMenuOpen(e, rule)}
                    >
                      <MoreIcon />
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
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="lg" fullWidth>
        <DialogTitle>Create New Rule</DialogTitle>
        <DialogContent>
          <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mb: 2 }}>
            <Tab label="Basic Info" />
            <Tab label="Visual Builder" icon={<VisualIcon />} iconPosition="start" />
          </Tabs>

          {tabValue === 0 && (
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
                    label="Rule Type"
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
                  Switch to the Visual Builder tab to design your rule logic visually
                </Alert>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Conditions (JSON)"
                  value={JSON.stringify(formData.conditions, null, 2)}
                  onChange={(e) => {
                    try {
                      setFormData({ ...formData, conditions: JSON.parse(e.target.value) });
                    } catch {}
                  }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Actions (JSON)"
                  value={JSON.stringify(formData.actions, null, 2)}
                  onChange={(e) => {
                    try {
                      setFormData({ ...formData, actions: JSON.parse(e.target.value) });
                    } catch {}
                  }}
                />
              </Grid>
            </Grid>
          )}

          {tabValue === 1 && (
            <Box sx={{ mt: 2 }}>
              <RuleBuilderCanvas onSave={handleVisualBuilderSave} />
            </Box>
          )}
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

      {/* Rule Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleTestRule}>
          <ListItemIcon><TestIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Test Rule</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleViewLogs}>
          <ListItemIcon><HistoryIcon fontSize="small" /></ListItemIcon>
          <ListItemText>View Logs</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleViewPerformance}>
          <ListItemIcon><TimelineIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Performance</ListItemText>
        </MenuItem>
        <MenuItem onClick={handleViewVersionHistory}>
          <ListItemIcon><HistoryIcon fontSize="small" /></ListItemIcon>
          <ListItemText>Version History</ListItemText>
        </MenuItem>
      </Menu>

      {/* Test Dialog */}
      {selectedRule && (
        <RuleTestDialog
          open={testDialogOpen}
          onClose={() => setTestDialogOpen(false)}
          ruleId={selectedRule.id}
          ruleName={selectedRule.name}
          onTest={DispatchRulesAPI.test}
        />
      )}

      {/* Logs Dialog */}
      {selectedRule && (
        <RuleLogsDialog
          open={logsDialogOpen}
          onClose={() => setLogsDialogOpen(false)}
          ruleId={selectedRule.id}
          ruleName={selectedRule.name}
          onLoadLogs={DispatchRulesAPI.getLogs}
        />
      )}

      {/* Performance Dialog */}
      {selectedRule && (
        <RulePerformanceDialog
          open={performanceDialogOpen}
          onClose={() => setPerformanceDialogOpen(false)}
          ruleId={selectedRule.id}
          ruleName={selectedRule.name}
          onLoadPerformance={DispatchRulesAPI.getPerformance}
        />
      )}

      {/* Version History Dialog */}
      {selectedRule && (
        <RuleVersionHistory
          open={versionHistoryOpen}
          onClose={() => setVersionHistoryOpen(false)}
          ruleId={selectedRule.id}
          ruleName={selectedRule.name}
          onLoadVersions={async (ruleId) => []} // Mock for now
          onRestoreVersion={async (ruleId, version) => {}}
        />
      )}

      {/* Simulation Dialog */}
      <RuleSimulationDialog
        open={simulationDialogOpen}
        onClose={() => setSimulationDialogOpen(false)}
        onSimulate={DispatchRulesAPI.simulate}
      />

      {/* Template Gallery */}
      <RuleTemplateGallery
        open={templateGalleryOpen}
        onClose={() => setTemplateGalleryOpen(false)}
        onSelectTemplate={handleSelectTemplate}
      />
    </Box>
    </Layout>
  );
};

export default DispatchRulesPage;
