import React, { useState } from 'react';
import {
  Paper,
  Box,
  Typography,
  TextField,
  Button,
  Grid,
  FormControlLabel,
  Switch,
  Alert,
  CircularProgress,
  Divider,
} from '@mui/material';
import { PlayArrow as PlayIcon } from '@mui/icons-material';
import { SimulationsAPI, RuleSimulation } from '../../api/simulations';

interface SimulationFormProps {
  onSimulationCreated?: (simulation: RuleSimulation) => void;
}

const SimulationForm: React.FC<SimulationFormProps> = ({ onSimulationCreated }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    iterations: 1,
    randomize_data: false,
    rule_config: JSON.stringify({
      conditions: {
        "AND": [
          { "distance_km": { "<=": 5 } },
          { "driver_rating": { ">=": 4.5 } }
        ]
      },
      actions: {
        "notify": true,
        "assign_driver": true
      }
    }, null, 2),
    scenario_data: JSON.stringify({
      orders: [
        { id: 1, distance_km: 3, priority: "normal", cargo_temp: "냉동" },
        { id: 2, distance_km: 7, priority: "high", cargo_temp: "냉장" }
      ],
      drivers: [
        { id: 1, rating: 4.8, available: true, vehicle_type: "냉동차" },
        { id: 2, rating: 4.2, available: true, vehicle_type: "냉장차" }
      ]
    }, null, 2),
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // JSON 파싱 검증
      const ruleConfig = JSON.parse(formData.rule_config);
      const scenarioData = JSON.parse(formData.scenario_data);

      const simulation = await SimulationsAPI.create({
        name: formData.name,
        description: formData.description,
        rule_config: ruleConfig,
        scenario_data: scenarioData,
        iterations: formData.iterations,
        randomize_data: formData.randomize_data,
        scenario_type: 'custom',
      });

      setSuccess(true);
      if (onSimulationCreated) {
        onSimulationCreated(simulation);
      }

      // 폼 초기화
      setTimeout(() => {
        setSuccess(false);
      }, 3000);

    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || '시뮬레이션 실행 실패');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        새 시뮬레이션 만들기
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        규칙 조건과 시나리오 데이터를 입력하여 시뮬레이션을 실행하세요
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          시뮬레이션이 성공적으로 실행되었습니다!
        </Alert>
      )}

      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          {/* 기본 정보 */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="시뮬레이션 이름"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="예: 거리 우선 배차 테스트"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              fullWidth
              label="설명"
              multiline
              rows={2}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="시뮬레이션 목적 및 테스트 내용 설명"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              type="number"
              label="반복 횟수"
              required
              value={formData.iterations}
              onChange={(e) => setFormData({ ...formData, iterations: parseInt(e.target.value) })}
              inputProps={{ min: 1, max: 100 }}
              helperText="1-100 사이의 값"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={formData.randomize_data}
                  onChange={(e) => setFormData({ ...formData, randomize_data: e.target.checked })}
                />
              }
              label="데이터 랜덤화"
            />
            <Typography variant="caption" display="block" color="text.secondary">
              각 반복마다 데이터에 변동을 줍니다
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
          </Grid>

          {/* 규칙 설정 */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              규칙 설정 (JSON)
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={10}
              value={formData.rule_config}
              onChange={(e) => setFormData({ ...formData, rule_config: e.target.value })}
              placeholder="규칙 조건과 액션을 JSON 형식으로 입력"
              helperText="AND, OR, NOT 등의 논리 연산자를 사용할 수 있습니다"
              sx={{ fontFamily: 'monospace' }}
            />
          </Grid>

          {/* 시나리오 데이터 */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              시나리오 데이터 (JSON)
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={12}
              value={formData.scenario_data}
              onChange={(e) => setFormData({ ...formData, scenario_data: e.target.value })}
              placeholder="테스트할 주문과 기사 데이터를 JSON 형식으로 입력"
              helperText="orders와 drivers 배열을 포함해야 합니다"
              sx={{ fontFamily: 'monospace' }}
            />
          </Grid>

          {/* 제출 버튼 */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                startIcon={loading ? <CircularProgress size={20} /> : <PlayIcon />}
                disabled={loading}
              >
                {loading ? '실행 중...' : '시뮬레이션 실행'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </form>
    </Paper>
  );
};

export default SimulationForm;
