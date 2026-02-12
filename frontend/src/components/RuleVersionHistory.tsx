import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Chip,
  IconButton,
  Alert,
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineOppositeContent,
} from '@mui/lab';
import {
  History as HistoryIcon,
  Restore as RestoreIcon,
  CheckCircle as ActiveIcon,
  RadioButtonUnchecked as InactiveIcon,
} from '@mui/icons-material';

interface RuleVersion {
  version: number;
  created_at: string;
  created_by?: string;
  is_current: boolean;
  changes_summary?: string;
  conditions: any;
  actions: any;
  priority: number;
}

interface RuleVersionHistoryProps {
  open: boolean;
  onClose: () => void;
  ruleId: number;
  ruleName: string;
  onLoadVersions: (ruleId: number) => Promise<RuleVersion[]>;
  onRestoreVersion: (ruleId: number, version: number) => Promise<void>;
}

export const RuleVersionHistory: React.FC<RuleVersionHistoryProps> = ({
  open,
  onClose,
  ruleId,
  ruleName,
  onLoadVersions,
  onRestoreVersion,
}) => {
  const [versions, setVersions] = useState<RuleVersion[]>([]);
  const [loading, setLoading] = useState(false);
  const [restoring, setRestoring] = useState<number | null>(null);

  useEffect(() => {
    if (open) {
      loadVersions();
    }
  }, [open]);

  const loadVersions = async () => {
    setLoading(true);
    try {
      // Mock data for now - replace with actual API call
      const mockVersions: RuleVersion[] = [
        {
          version: 3,
          created_at: new Date().toISOString(),
          created_by: 'admin',
          is_current: true,
          changes_summary: 'Updated priority to 100',
          conditions: { driver_rating: { $gte: 4.5 } },
          actions: { assign_driver: true },
          priority: 100,
        },
        {
          version: 2,
          created_at: new Date(Date.now() - 86400000).toISOString(),
          created_by: 'admin',
          is_current: false,
          changes_summary: 'Added distance constraint',
          conditions: { driver_rating: { $gte: 4.5 }, distance_km: { $lte: 10 } },
          actions: { assign_driver: true },
          priority: 90,
        },
        {
          version: 1,
          created_at: new Date(Date.now() - 172800000).toISOString(),
          created_by: 'admin',
          is_current: false,
          changes_summary: 'Initial version',
          conditions: { driver_rating: { $gte: 4.0 } },
          actions: { assign_driver: true },
          priority: 80,
        },
      ];
      setVersions(mockVersions);
    } catch (error) {
      console.error('Failed to load versions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async (version: number) => {
    if (!confirm(`Are you sure you want to restore to version ${version}?`)) {
      return;
    }

    setRestoring(version);
    try {
      await onRestoreVersion(ruleId, version);
      await loadVersions();
      alert('Version restored successfully');
    } catch (error) {
      alert('Failed to restore version');
    } finally {
      setRestoring(null);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box display="flex" alignItems="center" gap={1}>
          <HistoryIcon color="primary" />
          <Typography variant="h6">Version History: {ruleName}</Typography>
        </Box>
      </DialogTitle>

      <DialogContent>
        <Alert severity="info" sx={{ mb: 2 }}>
          View and restore previous versions of this rule. Restoring a version will create a new version with the old settings.
        </Alert>

        {versions.length === 0 ? (
          <Box textAlign="center" py={4}>
            <Typography color="text.secondary">No version history available</Typography>
          </Box>
        ) : (
          <Timeline position="right">
            {versions.map((version, index) => (
              <TimelineItem key={version.version}>
                <TimelineOppositeContent color="text.secondary" sx={{ flex: 0.3 }}>
                  <Typography variant="body2">{formatDate(version.created_at)}</Typography>
                  {version.created_by && (
                    <Typography variant="caption" color="text.secondary">
                      by {version.created_by}
                    </Typography>
                  )}
                </TimelineOppositeContent>

                <TimelineSeparator>
                  <TimelineDot color={version.is_current ? 'primary' : 'grey'}>
                    {version.is_current ? <ActiveIcon /> : <InactiveIcon />}
                  </TimelineDot>
                  {index < versions.length - 1 && <TimelineConnector />}
                </TimelineSeparator>

                <TimelineContent>
                  <Box sx={{ mb: 2 }}>
                    <Box display="flex" alignItems="center" gap={1} mb={1}>
                      <Typography variant="h6">Version {version.version}</Typography>
                      {version.is_current && <Chip label="Current" color="primary" size="small" />}
                    </Box>

                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      {version.changes_summary || 'No description'}
                    </Typography>

                    <Box sx={{ bgcolor: 'grey.50', p: 1.5, borderRadius: 1, mb: 1 }}>
                      <Typography variant="caption" display="block" gutterBottom>
                        Priority: {version.priority}
                      </Typography>
                      <Typography variant="caption" display="block" gutterBottom>
                        Conditions: {JSON.stringify(version.conditions)}
                      </Typography>
                      <Typography variant="caption" display="block">
                        Actions: {JSON.stringify(version.actions)}
                      </Typography>
                    </Box>

                    {!version.is_current && (
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<RestoreIcon />}
                        onClick={() => handleRestore(version.version)}
                        disabled={restoring === version.version}
                      >
                        {restoring === version.version ? 'Restoring...' : 'Restore'}
                      </Button>
                    )}
                  </Box>
                </TimelineContent>
              </TimelineItem>
            ))}
          </Timeline>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};
