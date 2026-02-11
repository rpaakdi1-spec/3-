/**
 * Predictive Maintenance Dashboard - Phase 14
 * AI-based failure prediction and maintenance scheduling
 */
import React, { useState, useEffect } from 'react';
import { Wrench, AlertTriangle, Calendar, TrendingUp, DollarSign, CheckCircle, Clock, Brain } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { apiClient } from '../api/client';

interface Prediction {
  id: number;
  vehicle_id: number;
  component: string;
  failure_probability: number;
  predicted_failure_date: string;
  confidence_score: number;
  recommended_action: string;
  recommended_date: string;
  estimated_cost: number;
  is_scheduled: boolean;
}

interface VehicleHealth {
  vehicle_id: number;
  overall_score: number;
  health_status: string;
  component_scores: {
    engine: number;
    transmission: number;
    brake: number;
    suspension: number;
    electrical: number;
  };
  risk_factors: any[];
  prediction_count: number;
}

const PredictiveMaintenanceDashboard: React.FC = () => {
  const [selectedVehicle, setSelectedVehicle] = useState<number>(1);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [vehicleHealth, setVehicleHealth] = useState<VehicleHealth | null>(null);
  const [statistics, setStatistics] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [predicting, setPredicting] = useState(false);

  useEffect(() => {
    loadStatistics();
    loadVehicleData();
  }, [selectedVehicle]);

  const loadStatistics = async () => {
    try {
      const response = await apiClient.get('/api/v1/iot/maintenance/statistics');
      setStatistics(response.data);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  const loadVehicleData = async () => {
    try {
      setLoading(true);
      
      // Load predictions
      const predResponse = await apiClient.get(`/api/v1/iot/maintenance/predictions/${selectedVehicle}`);
      setPredictions(predResponse.data.predictions || []);

      // Load health
      const healthResponse = await apiClient.get(`/api/v1/iot/maintenance/health/${selectedVehicle}`);
      setVehicleHealth(healthResponse.data);
    } catch (error) {
      console.error('Failed to load vehicle data:', error);
    } finally {
      setLoading(false);
    }
  };

  const runPrediction = async () => {
    try {
      setPredicting(true);
      await apiClient.post('/api/v1/iot/maintenance/predict', {
        vehicle_id: selectedVehicle,
        analyze_days: 30
      });
      
      await loadVehicleData();
      alert('예측 분석이 완료되었습니다!');
    } catch (error) {
      console.error('Failed to run prediction:', error);
      alert('예측 분석에 실패했습니다.');
    } finally {
      setPredicting(false);
    }
  };

  const scheduleMainenance = async (predictionId: number) => {
    try {
      const prediction = predictions.find(p => p.id === predictionId);
      if (!prediction) return;

      await apiClient.post('/api/v1/iot/maintenance/schedule', {
        prediction_id: predictionId,
        scheduled_date: prediction.recommended_date,
        assigned_technician: 'Auto-assigned'
      });

      await loadVehicleData();
      alert('정비가 스케줄되었습니다!');
    } catch (error) {
      console.error('Failed to schedule maintenance:', error);
      alert('스케줄 생성에 실패했습니다.');
    }
  };

  const getHealthColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 75) return 'text-blue-600 bg-blue-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    if (score >= 40) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  const getProbabilityColor = (prob: number) => {
    if (prob >= 0.7) return 'text-red-600 bg-red-100';
    if (prob >= 0.5) return 'text-orange-600 bg-orange-100';
    if (prob >= 0.3) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  // Chart data
  const componentScoreData = vehicleHealth ? [
    { name: '엔진', score: vehicleHealth.component_scores.engine },
    { name: '변속기', score: vehicleHealth.component_scores.transmission },
    { name: '브레이크', score: vehicleHealth.component_scores.brake },
    { name: '서스펜션', score: vehicleHealth.component_scores.suspension },
    { name: '전기', score: vehicleHealth.component_scores.electrical }
  ] : [];

  const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6'];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">🔧 예측 유지보수</h1>
          <p className="text-gray-600 mt-1">AI 기반 고장 예측 및 정비 스케줄링</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedVehicle}
            onChange={(e) => setSelectedVehicle(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {[1, 2, 3, 4, 5].map(id => (
              <option key={id} value={id}>차량 {id}</option>
            ))}
          </select>
          <button
            onClick={runPrediction}
            disabled={predicting}
            className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 flex items-center space-x-2"
          >
            <Brain className="w-5 h-5" />
            <span>{predicting ? '분석 중...' : 'AI 예측 실행'}</span>
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">활성 예측</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{statistics.active_predictions}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Brain className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">스케줄된 정비</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{statistics.scheduled_maintenance}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Calendar className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">고위험 차량</p>
                <p className="text-3xl font-bold text-red-600 mt-2">{statistics.high_risk_vehicles}</p>
              </div>
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-red-600" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">완료된 정비 (30일)</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{statistics.completed_maintenance_30d}</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <CheckCircle className="w-6 h-6 text-purple-600" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Vehicle Health */}
      {vehicleHealth && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">🏥 차량 건강 상태</h2>
            <div className="text-center mb-6">
              <div className={`inline-block px-8 py-4 rounded-2xl ${getHealthColor(vehicleHealth.overall_score)}`}>
                <p className="text-5xl font-bold">{vehicleHealth.overall_score.toFixed(0)}</p>
                <p className="text-sm font-medium mt-2">{vehicleHealth.health_status.toUpperCase()}</p>
              </div>
            </div>
            <div className="space-y-3">
              {Object.entries(vehicleHealth.component_scores).map(([key, value]) => {
                const names: { [key: string]: string } = {
                  engine: '엔진',
                  transmission: '변속기',
                  brake: '브레이크',
                  suspension: '서스펜션',
                  electrical: '전기'
                };
                return (
                  <div key={key} className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">{names[key]}</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${
                            value >= 75 ? 'bg-green-500' : value >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${value}%` }}
                        />
                      </div>
                      <span className="text-sm font-bold text-gray-900 w-12 text-right">{value.toFixed(0)}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">📊 부품별 점수</h2>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={componentScoreData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="score" fill="#3B82F6" radius={[8, 8, 0, 0]}>
                  {componentScoreData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Predictions */}
      {predictions.length > 0 && (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">🔮 AI 예측 결과</h2>
          <div className="space-y-4">
            {predictions.map(pred => (
              <div
                key={pred.id}
                className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <Wrench className="w-5 h-5 text-gray-600" />
                      <h3 className="font-semibold text-gray-900">{pred.component}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-bold ${getProbabilityColor(pred.failure_probability)}`}>
                        고장 확률: {(pred.failure_probability * 100).toFixed(0)}%
                      </span>
                      <span className="text-xs text-gray-500">
                        신뢰도: {(pred.confidence_score * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 mb-3">{pred.recommended_action}</p>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div className="flex items-center space-x-2">
                        <Clock className="w-4 h-4 text-gray-500" />
                        <div>
                          <p className="text-xs text-gray-500">권장일</p>
                          <p className="font-medium text-gray-900">
                            {new Date(pred.recommended_date).toLocaleDateString('ko-KR')}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <AlertTriangle className="w-4 h-4 text-gray-500" />
                        <div>
                          <p className="text-xs text-gray-500">예상 고장일</p>
                          <p className="font-medium text-red-600">
                            {new Date(pred.predicted_failure_date).toLocaleDateString('ko-KR')}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <DollarSign className="w-4 h-4 text-gray-500" />
                        <div>
                          <p className="text-xs text-gray-500">예상 비용</p>
                          <p className="font-medium text-gray-900">
                            {pred.estimated_cost.toLocaleString()}원
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                  {!pred.is_scheduled && (
                    <button
                      onClick={() => scheduleMainenance(pred.id)}
                      className="ml-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
                    >
                      <Calendar className="w-4 h-4" />
                      <span>스케줄</span>
                    </button>
                  )}
                  {pred.is_scheduled && (
                    <div className="ml-4 px-4 py-2 bg-green-100 text-green-700 rounded-lg flex items-center space-x-2">
                      <CheckCircle className="w-4 h-4" />
                      <span>예약됨</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {predictions.length === 0 && !loading && (
        <div className="bg-white p-12 rounded-xl shadow-sm border border-gray-200 text-center">
          <Brain className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 mb-4">예측 데이터가 없습니다.</p>
          <p className="text-sm text-gray-500 mb-6">
            "AI 예측 실행" 버튼을 클릭하여 차량 상태를 분석하세요.
          </p>
          <button
            onClick={runPrediction}
            disabled={predicting}
            className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 inline-flex items-center space-x-2"
          >
            <Brain className="w-5 h-5" />
            <span>{predicting ? '분석 중...' : 'AI 예측 실행'}</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default PredictiveMaintenanceDashboard;
