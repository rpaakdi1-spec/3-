import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Tabs,
  Tab,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  CompareArrows as CompareIcon,
  ViewList as ListIcon,
  Dashboard as DashboardIcon,
  Science as ScienceIcon,
} from '@mui/icons-material';
import { SimulationsAPI, RuleSimulation } from '../api/simulations';
import SimulationForm from '../components/simulation/SimulationForm';
import SimulationList from '../components/simulation/SimulationList';
import SimulationDetail from '../components/simulation/SimulationDetail';
import ComparisonView from '../components/simulation/ComparisonView';
import TemplateGallery from '../components/simulation/TemplateGallery';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simulation-tabpanel-${index}`}
      aria-labelledby={`simulation-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const SimulationPage: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [statistics, setStatistics] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [selectedSimulation, setSelectedSimulation] = useState<RuleSimulation | null>(null);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      const stats = await SimulationsAPI.getStatistics(7);
      setStatistics(stats);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleSimulationCreated = (simulation: RuleSimulation) => {
    setSelectedSimulation(simulation);
    setTabValue(1); // Switch to list tab
    loadStatistics();
  };

  const handleSimulationSelected = (simulation: RuleSimulation) => {
    setSelectedSimulation(simulation);
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ScienceIcon fontSize="large" />
          규칙 시뮬레이션
        </Typography>
        <Typography variant="body1" color="text.secondary">
          배차 규칙을 다양한 시나리오에서 테스트하고 성능을 비교하세요
        </Typography>
      </Box>

      {/* Statistics Cards */}
      {statistics && (
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  총 시뮬레이션
                </Typography>
                <Typography variant="h4">
                  {statistics.total_simulations}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  최근 7일
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  완료
                </Typography>
                <Typography variant="h4" color="success.main">
                  {statistics.completed_simulations}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  성공적으로 완료
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  평균 매칭률
                </Typography>
                <Typography variant="h4" color="primary.main">
                  {statistics.avg_match_rate.toFixed(1)}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  매칭 성공률
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  평균 응답 시간
                </Typography>
                <Typography variant="h4" color="info.main">
                  {statistics.avg_response_time_ms.toFixed(1)}ms
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  처리 시간
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          indicatorColor="primary"
          textColor="primary"
          variant="fullWidth"
        >
          <Tab icon={<PlayIcon />} label="새 시뮬레이션" />
          <Tab icon={<ListIcon />} label="시뮬레이션 목록" />
          <Tab icon={<CompareIcon />} label="A/B 비교" />
          <Tab icon={<DashboardIcon />} label="템플릿 갤러리" />
        </Tabs>
      </Paper>

      {/* Tab Panels */}
      <TabPanel value={tabValue} index={0}>
        <SimulationForm onSimulationCreated={handleSimulationCreated} />
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={selectedSimulation ? 6 : 12}>
            <SimulationList onSimulationSelected={handleSimulationSelected} />
          </Grid>
          {selectedSimulation && (
            <Grid item xs={12} md={6}>
              <SimulationDetail
                simulation={selectedSimulation}
                onClose={() => setSelectedSimulation(null)}
              />
            </Grid>
          )}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <ComparisonView />
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <TemplateGallery onTemplateSelected={(template) => {
          // 템플릿 선택 시 새 시뮬레이션 탭으로 이동하고 데이터 채우기
          setTabValue(0);
        }} />
      </TabPanel>
    </Container>
  );
};

export default SimulationPage;
