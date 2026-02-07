import React, { useState } from 'react';
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
  CardActions,
  Chip,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  CollectionsBookmark as TemplateIcon,
  Add as AddIcon,
  Search as SearchIcon,
  Star as StarIcon,
} from '@mui/icons-material';

interface RuleTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
  popular: boolean;
  rule_type: string;
  priority: number;
  conditions: any;
  actions: any;
}

interface RuleTemplateGalleryProps {
  open: boolean;
  onClose: () => void;
  onSelectTemplate: (template: RuleTemplate) => void;
}

const TEMPLATES: RuleTemplate[] = [
  {
    id: 'nearby-drivers',
    name: 'Nearby Drivers Priority',
    description: 'Prioritize drivers within 5km of pickup location',
    category: 'Distance',
    difficulty: 'easy',
    popular: true,
    rule_type: 'assignment',
    priority: 90,
    conditions: {
      distance_km: { $lte: 5 },
    },
    actions: {
      assign_driver: true,
      notify: true,
    },
  },
  {
    id: 'high-rated-drivers',
    name: 'High-Rated Drivers First',
    description: 'Assign orders to drivers with rating >= 4.5',
    category: 'Quality',
    difficulty: 'easy',
    popular: true,
    rule_type: 'assignment',
    priority: 85,
    conditions: {
      driver_rating: { $gte: 4.5 },
      driver_status: { $eq: 'available' },
    },
    actions: {
      assign_driver: true,
    },
  },
  {
    id: 'urgent-orders',
    name: 'Urgent Order Handling',
    description: 'Fast-track high priority orders to nearest available driver',
    category: 'Priority',
    difficulty: 'medium',
    popular: true,
    rule_type: 'assignment',
    priority: 100,
    conditions: {
      and: [
        { order_priority: { $eq: 'urgent' } },
        { distance_km: { $lte: 10 } },
        { driver_available: { $eq: true } },
      ],
    },
    actions: {
      assign_driver: true,
      set_priority: { value: 100 },
      notify: { channel: 'sms', urgent: true },
    },
  },
  {
    id: 'peak-hours',
    name: 'Peak Hours Optimization',
    description: 'Optimize assignments during peak hours (8-10 AM, 6-8 PM)',
    category: 'Time',
    difficulty: 'medium',
    popular: false,
    rule_type: 'optimization',
    priority: 80,
    conditions: {
      or: [
        { current_hour: { $gte: 8, $lte: 10 } },
        { current_hour: { $gte: 18, $lte: 20 } },
      ],
    },
    actions: {
      optimize: true,
      algorithm: 'hungarian',
    },
  },
  {
    id: 'temperature-sensitive',
    name: 'Temperature-Sensitive Cargo',
    description: 'Assign refrigerated vehicles for cold chain orders',
    category: 'Special',
    difficulty: 'medium',
    popular: false,
    rule_type: 'constraint',
    priority: 95,
    conditions: {
      and: [
        { order_type: { $eq: 'cold_chain' } },
        { vehicle_type: { $eq: 'refrigerated' } },
        { temperature_control: { $eq: true } },
      ],
    },
    actions: {
      assign_vehicle: { type: 'refrigerated' },
      monitor_temperature: true,
      notify: { channel: 'app' },
    },
  },
  {
    id: 'balanced-workload',
    name: 'Balanced Driver Workload',
    description: 'Distribute orders evenly among available drivers',
    category: 'Fairness',
    difficulty: 'hard',
    popular: false,
    rule_type: 'optimization',
    priority: 70,
    conditions: {
      driver_available: { $eq: true },
    },
    actions: {
      optimize: true,
      strategy: 'balanced_workload',
      max_orders_per_driver: 5,
    },
  },
  {
    id: 'multi-stop-route',
    name: 'Multi-Stop Route Optimization',
    description: 'Optimize routes for orders with multiple stops',
    category: 'Efficiency',
    difficulty: 'hard',
    popular: true,
    rule_type: 'optimization',
    priority: 75,
    conditions: {
      order_stops: { $gt: 2 },
    },
    actions: {
      optimize: true,
      algorithm: 'tsp',
      minimize: 'total_distance',
    },
  },
  {
    id: 'new-driver-training',
    name: 'New Driver Training Assignments',
    description: 'Assign easier routes to new drivers (< 30 days)',
    category: 'Training',
    difficulty: 'easy',
    popular: false,
    rule_type: 'assignment',
    priority: 60,
    conditions: {
      and: [
        { driver_experience_days: { $lt: 30 } },
        { distance_km: { $lte: 15 } },
        { order_complexity: { $eq: 'simple' } },
      ],
    },
    actions: {
      assign_driver: true,
      mentor_support: true,
    },
  },
];

export const RuleTemplateGallery: React.FC<RuleTemplateGalleryProps> = ({
  open,
  onClose,
  onSelectTemplate,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const filteredTemplates = TEMPLATES.filter((template) => {
    const matchesSearch =
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const categories = ['all', ...Array.from(new Set(TEMPLATES.map((t) => t.category)))];

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy':
        return 'success';
      case 'medium':
        return 'warning';
      case 'hard':
        return 'error';
      default:
        return 'default';
    }
  };

  const handleSelectTemplate = (template: RuleTemplate) => {
    onSelectTemplate(template);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <TemplateIcon color="primary" />
          <Typography variant="h6">Rule Template Gallery</Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Search templates..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Box>

        <Box sx={{ mb: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {categories.map((category) => (
            <Chip
              key={category}
              label={category}
              onClick={() => setSelectedCategory(category)}
              color={selectedCategory === category ? 'primary' : 'default'}
              variant={selectedCategory === category ? 'filled' : 'outlined'}
            />
          ))}
        </Box>

        <Grid container spacing={2}>
          {filteredTemplates.map((template) => (
            <Grid item xs={12} md={6} key={template.id}>
              <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                    <Typography variant="h6" component="div">
                      {template.name}
                    </Typography>
                    {template.popular && <StarIcon color="warning" fontSize="small" />}
                  </Box>

                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {template.description}
                  </Typography>

                  <Box display="flex" gap={1} flexWrap="wrap">
                    <Chip label={template.category} size="small" variant="outlined" />
                    <Chip
                      label={template.difficulty}
                      size="small"
                      color={getDifficultyColor(template.difficulty) as any}
                    />
                    <Chip label={template.rule_type} size="small" color="info" />
                  </Box>
                </CardContent>

                <CardActions>
                  <Button
                    size="small"
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => handleSelectTemplate(template)}
                    fullWidth
                  >
                    Use Template
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>

        {filteredTemplates.length === 0 && (
          <Box textAlign="center" py={4}>
            <Typography color="text.secondary">No templates found</Typography>
          </Box>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};
