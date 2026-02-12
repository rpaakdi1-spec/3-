import React, { useState, useCallback, useMemo } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  NodeTypes,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Chip,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  PlayArrow as TestIcon,
} from '@mui/icons-material';

// Custom Node Components
const ConditionNode = ({ data }: { data: any }) => {
  return (
    <Box
      sx={{
        padding: 2,
        borderRadius: 2,
        border: '2px solid #3b82f6',
        backgroundColor: '#eff6ff',
        minWidth: 200,
      }}
    >
      <Typography variant="subtitle2" fontWeight="bold" color="primary">
        Condition
      </Typography>
      <Typography variant="body2" sx={{ mt: 1 }}>
        {data.label}
      </Typography>
      {data.field && (
        <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
          Field: {data.field}
        </Typography>
      )}
      {data.operator && (
        <Typography variant="caption" display="block">
          Operator: {data.operator}
        </Typography>
      )}
      {data.value !== undefined && (
        <Typography variant="caption" display="block">
          Value: {String(data.value)}
        </Typography>
      )}
    </Box>
  );
};

const ActionNode = ({ data }: { data: any }) => {
  return (
    <Box
      sx={{
        padding: 2,
        borderRadius: 2,
        border: '2px solid #10b981',
        backgroundColor: '#ecfdf5',
        minWidth: 200,
      }}
    >
      <Typography variant="subtitle2" fontWeight="bold" color="success.main">
        Action
      </Typography>
      <Typography variant="body2" sx={{ mt: 1 }}>
        {data.label}
      </Typography>
      {data.actionType && (
        <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
          Type: {data.actionType}
        </Typography>
      )}
      {data.params && (
        <Typography variant="caption" display="block">
          Params: {JSON.stringify(data.params)}
        </Typography>
      )}
    </Box>
  );
};

const LogicalNode = ({ data }: { data: any }) => {
  return (
    <Box
      sx={{
        padding: 2,
        borderRadius: 2,
        border: '2px solid #f59e0b',
        backgroundColor: '#fffbeb',
        minWidth: 100,
        textAlign: 'center',
      }}
    >
      <Typography variant="h6" fontWeight="bold" color="warning.main">
        {data.label}
      </Typography>
    </Box>
  );
};

const nodeTypes: NodeTypes = {
  condition: ConditionNode,
  action: ActionNode,
  logical: LogicalNode,
};

interface RuleBuilderCanvasProps {
  onSave: (ruleData: any) => void;
  initialRule?: any;
}

export const RuleBuilderCanvas: React.FC<RuleBuilderCanvasProps> = ({
  onSave,
  initialRule,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [nodeType, setNodeType] = useState<'condition' | 'action' | 'logical'>('condition');

  // Node creation dialog state
  const [newNodeData, setNewNodeData] = useState<any>({
    label: '',
    field: '',
    operator: '',
    value: '',
    actionType: '',
    params: {},
  });

  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            animated: true,
            markerEnd: { type: MarkerType.ArrowClosed },
          },
          eds
        )
      );
    },
    [setEdges]
  );

  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    setSelectedNode(node);
  }, []);

  const handleAddNode = () => {
    setDialogOpen(true);
  };

  const handleSaveNode = () => {
    const id = `${nodeType}-${nodes.length + 1}`;
    const newNode: Node = {
      id,
      type: nodeType,
      position: { x: Math.random() * 400, y: Math.random() * 400 },
      data: { ...newNodeData },
    };

    setNodes((nds) => [...nds, newNode]);
    setDialogOpen(false);
    setNewNodeData({
      label: '',
      field: '',
      operator: '',
      value: '',
      actionType: '',
      params: {},
    });
  };

  const handleDeleteNode = () => {
    if (selectedNode) {
      setNodes((nds) => nds.filter((node) => node.id !== selectedNode.id));
      setEdges((eds) =>
        eds.filter((edge) => edge.source !== selectedNode.id && edge.target !== selectedNode.id)
      );
      setSelectedNode(null);
    }
  };

  const handleSaveRule = () => {
    const ruleData = {
      nodes: nodes,
      edges: edges,
      // Convert visual representation to rule JSON
      conditions: convertNodesToConditions(nodes, edges),
      actions: convertNodesToActions(nodes, edges),
    };
    onSave(ruleData);
  };

  const handleTestRule = () => {
    console.log('Testing rule with current configuration');
    // Implement test logic
  };

  return (
    <Box sx={{ height: '600px', width: '100%' }}>
      <Paper sx={{ mb: 2, p: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddNode}
          >
            Add Node
          </Button>
          <Button
            variant="outlined"
            startIcon={<DeleteIcon />}
            onClick={handleDeleteNode}
            disabled={!selectedNode}
          >
            Delete Node
          </Button>
          <Button
            variant="contained"
            color="success"
            startIcon={<SaveIcon />}
            onClick={handleSaveRule}
          >
            Save Rule
          </Button>
          <Button
            variant="outlined"
            color="primary"
            startIcon={<TestIcon />}
            onClick={handleTestRule}
          >
            Test Rule
          </Button>
          {selectedNode && (
            <Chip
              label={`Selected: ${selectedNode.data.label}`}
              onDelete={() => setSelectedNode(null)}
            />
          )}
        </Box>
      </Paper>

      <Paper sx={{ height: 'calc(100% - 80px)' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
        >
          <Controls />
          <Background />
        </ReactFlow>
      </Paper>

      {/* Add Node Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Node</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Node Type</InputLabel>
            <Select
              value={nodeType}
              label="Node Type"
              onChange={(e) => setNodeType(e.target.value as any)}
            >
              <MenuItem value="condition">Condition</MenuItem>
              <MenuItem value="action">Action</MenuItem>
              <MenuItem value="logical">Logical (AND/OR)</MenuItem>
            </Select>
          </FormControl>

          <TextField
            fullWidth
            label="Label"
            value={newNodeData.label}
            onChange={(e) => setNewNodeData({ ...newNodeData, label: e.target.value })}
            sx={{ mt: 2 }}
          />

          {nodeType === 'condition' && (
            <>
              <TextField
                fullWidth
                label="Field"
                value={newNodeData.field}
                onChange={(e) => setNewNodeData({ ...newNodeData, field: e.target.value })}
                sx={{ mt: 2 }}
                placeholder="e.g., order.priority"
              />
              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Operator</InputLabel>
                <Select
                  value={newNodeData.operator}
                  label="Operator"
                  onChange={(e) => setNewNodeData({ ...newNodeData, operator: e.target.value })}
                >
                  <MenuItem value="eq">Equals (==)</MenuItem>
                  <MenuItem value="ne">Not Equals (!=)</MenuItem>
                  <MenuItem value="gt">Greater Than (&gt;)</MenuItem>
                  <MenuItem value="lt">Less Than (&lt;)</MenuItem>
                  <MenuItem value="gte">Greater Than or Equal (&gt;=)</MenuItem>
                  <MenuItem value="lte">Less Than or Equal (&lt;=)</MenuItem>
                  <MenuItem value="in">In</MenuItem>
                  <MenuItem value="nin">Not In</MenuItem>
                  <MenuItem value="contains">Contains</MenuItem>
                  <MenuItem value="regex">Regex</MenuItem>
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="Value"
                value={newNodeData.value}
                onChange={(e) => setNewNodeData({ ...newNodeData, value: e.target.value })}
                sx={{ mt: 2 }}
              />
            </>
          )}

          {nodeType === 'action' && (
            <>
              <FormControl fullWidth sx={{ mt: 2 }}>
                <InputLabel>Action Type</InputLabel>
                <Select
                  value={newNodeData.actionType}
                  label="Action Type"
                  onChange={(e) => setNewNodeData({ ...newNodeData, actionType: e.target.value })}
                >
                  <MenuItem value="assign_driver">Assign Driver</MenuItem>
                  <MenuItem value="assign_vehicle">Assign Vehicle</MenuItem>
                  <MenuItem value="set_priority">Set Priority</MenuItem>
                  <MenuItem value="notify">Send Notification</MenuItem>
                  <MenuItem value="optimize">Run Optimization</MenuItem>
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="Parameters (JSON)"
                value={JSON.stringify(newNodeData.params)}
                onChange={(e) => {
                  try {
                    const params = JSON.parse(e.target.value);
                    setNewNodeData({ ...newNodeData, params });
                  } catch {}
                }}
                sx={{ mt: 2 }}
                multiline
                rows={3}
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSaveNode} variant="contained">
            Add
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Helper functions to convert visual representation to rule JSON
function convertNodesToConditions(nodes: Node[], edges: Edge[]): any {
  const conditionNodes = nodes.filter((n) => n.type === 'condition');
  const logicalNodes = nodes.filter((n) => n.type === 'logical');
  
  if (conditionNodes.length === 0) return {};
  
  // Single condition
  if (conditionNodes.length === 1 && logicalNodes.length === 0) {
    const node = conditionNodes[0];
    return buildConditionObject(node);
  }
  
  // Multiple conditions with logical operators
  if (logicalNodes.length > 0) {
    return buildComplexConditions(conditionNodes, logicalNodes, edges);
  }
  
  // Multiple conditions without explicit logical operator - assume AND
  return {
    and: conditionNodes.map(buildConditionObject),
  };
}

function buildConditionObject(node: Node): any {
  const { field, operator, value } = node.data;
  
  // Convert operator to MongoDB-style notation
  const operatorMap: Record<string, string> = {
    'eq': '$eq',
    'ne': '$ne',
    'gt': '$gt',
    'lt': '$lt',
    'gte': '$gte',
    'lte': '$lte',
    'in': '$in',
    'nin': '$nin',
    'contains': '$regex',
    'regex': '$regex',
  };
  
  const mappedOp = operatorMap[operator] || operator;
  
  // Handle special cases
  if (operator === 'contains') {
    return {
      [field]: {
        [mappedOp]: value,
        '$options': 'i' // case-insensitive
      }
    };
  }
  
  // Try to parse value as number if possible
  let parsedValue = value;
  if (typeof value === 'string' && !isNaN(Number(value))) {
    parsedValue = Number(value);
  }
  
  return {
    [field]: {
      [mappedOp]: parsedValue
    }
  };
}

function buildComplexConditions(conditionNodes: Node[], logicalNodes: Node[], edges: Edge[]): any {
  // Build a tree structure based on edges
  // For now, implement a simple approach
  const primaryLogical = logicalNodes[0];
  const operator = primaryLogical?.data.label?.toLowerCase() === 'or' ? 'or' : 'and';
  
  return {
    [operator]: conditionNodes.map(buildConditionObject),
  };
}

function convertNodesToActions(nodes: Node[], edges: Edge[]): any {
  const actionNodes = nodes.filter((n) => n.type === 'action');
  
  if (actionNodes.length === 0) return {};
  
  // Convert to action object format expected by backend
  const actions: Record<string, any> = {};
  
  actionNodes.forEach((node) => {
    const { actionType, params } = node.data;
    
    switch (actionType) {
      case 'assign_driver':
        actions.assign_driver = true;
        if (params.criteria) actions.driver_criteria = params.criteria;
        break;
      case 'assign_vehicle':
        actions.assign_vehicle = true;
        if (params.criteria) actions.vehicle_criteria = params.criteria;
        break;
      case 'set_priority':
        actions.set_priority = params.priority || 50;
        break;
      case 'notify':
        actions.notify = true;
        if (params.message) actions.notification_message = params.message;
        break;
      case 'optimize':
        actions.optimize = true;
        break;
      default:
        actions[actionType] = params;
    }
  });
  
  return actions;
}
