import React, { useState, useEffect } from 'react';
import {
  Brain,
  AlertTriangle,
  TrendingUp,
  Zap,
  DollarSign,
  Calendar,
  CheckCircle,
  XCircle,
  RefreshCw,
  PlayCircle,
  BarChart3,
  Activity,
  Truck,
  Shield,
  Info
} from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface VehiclePrediction {
  vehicle_id: number;
  vehicle_plate: string;
  failure_probability: number;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  estimated_cost: number;
  recommendation: string;
  days_until_recommended_maintenance: number;
  confidence_score: number;
  key_factors: { factor: string; importance: number }[];
  current_stats: {
    total_distance: number;
    days_since_last_maintenance: number;
    total_maintenances: number;
  };
}

interface MLStatistics {
  total_vehicles: number;
  risk_distribution: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  average_failure_probability: number;
  total_estimated_cost: number;
  urgent_action_needed: number;
  top_risk_vehicles: VehiclePrediction[];
}

interface ModelStatus {
  is_trained: boolean;
  is_available: boolean;
  feature_count: number;
  features: string[];
  status: string;
}

const MLPredictionsPage: React.FC = () => {
  const [predictions, setPredictions] = useState<VehiclePrediction[]>([]);
  const [statistics, setStatistics] = useState<MLStatistics | null>(null);
  const [modelStatus, setModelStatus] = useState<ModelStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [training, setTraining] = useState(false);
  const [selectedRisk, setSelectedRisk] = useState<string>('all');
  const [selectedVehicle, setSelectedVehicle] = useState<VehiclePrediction | null>(null);

  useEffect(() => {
    loadData();
    loadModelStatus();
  }, [selectedRisk]);

  const loadData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      // Load predictions
      const params = selectedRisk !== 'all' ? { risk_level: selectedRisk } : {};
      const predRes = await axios.get(`${API_URL}/api/v1/ml/predictions`, {
        headers,
        params
      });
      setPredictions(predRes.data);

      // Load statistics
      const statsRes = await axios.get(`${API_URL}/api/v1/ml/statistics`, {
        headers
      });
      setStatistics(statsRes.data);
    } catch (error) {
      console.error('Failed to load ML predictions:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadModelStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await axios.get(`${API_URL}/api/v1/ml/model-status`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setModelStatus(res.data);
    } catch (error) {
      console.error('Failed to load model status:', error);
    }
  };

  const handleTrainModel = async () => {
    if (!confirm('모델 학습을 시작하시겠습니까? 이 작업은 수 분이 소요될 수 있습니다.')) {
      return;
    }

    setTraining(true);
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_URL}/api/v1/ml/train`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('모델 학습이 백그라운드에서 시작되었습니다. 잠시 후 다시 확인해주세요.');
      
      // Reload after 30 seconds
      setTimeout(() => {
        loadModelStatus();
        loadData();
        setTraining(false);
      }, 30000);
    } catch (error: any) {
      alert(`모델 학습 실패: ${error.response?.data?.detail || error.message}`);
      setTraining(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'CRITICAL': return 'bg-red-100 text-red-800 border-red-300';
      case 'HIGH': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'LOW': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'CRITICAL': return <AlertTriangle className="w-4 h-4" />;
      case 'HIGH': return <AlertTriangle className="w-4 h-4" />;
      case 'MEDIUM': return <Info className="w-4 h-4" />;
      case 'LOW': return <CheckCircle className="w-4 h-4" />;
      default: return null;
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
      minimumFractionDigits: 0
    }).format(amount);
  };

  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <Brain className="w-8 h-8 text-purple-600" />
                AI/ML 예측 정비 시스템
              </h1>
              <p className="text-gray-600 mt-1">차량 고장 예측 및 최적 정비 시점 추천</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={loadData}
                disabled={loading}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                새로고침
              </button>
              <button
                onClick={handleTrainModel}
                disabled={training || loading}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2 disabled:bg-gray-400"
              >
                <PlayCircle className="w-4 h-4" />
                {training ? '학습 중...' : '모델 학습'}
              </button>
            </div>
          </div>
        </div>

        {/* Model Status Banner */}
        {modelStatus && (
          <div className={`mb-6 p-4 rounded-lg border ${
            modelStatus.is_available 
              ? 'bg-green-50 border-green-200' 
              : 'bg-yellow-50 border-yellow-200'
          }`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {modelStatus.is_available ? (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                ) : (
                  <XCircle className="w-5 h-5 text-yellow-600" />
                )}
                <div>
                  <h3 className="font-semibold text-gray-900">
                    모델 상태: {modelStatus.is_available ? '준비됨' : '학습 필요'}
                  </h3>
                  <p className="text-sm text-gray-600">
                    특징 수: {modelStatus.feature_count} | 상태: {modelStatus.status}
                  </p>
                </div>
              </div>
              {!modelStatus.is_available && (
                <button
                  onClick={handleTrainModel}
                  className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                >
                  지금 학습하기
                </button>
              )}
            </div>
          </div>
        )}

        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">총 차량</span>
                <Truck className="w-5 h-5 text-blue-500" />
              </div>
              <p className="text-2xl font-bold text-gray-900">{statistics.total_vehicles}</p>
              <p className="text-xs text-gray-500 mt-1">분석 완료</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">긴급 조치</span>
                <AlertTriangle className="w-5 h-5 text-red-500" />
              </div>
              <p className="text-2xl font-bold text-red-600">{statistics.urgent_action_needed}</p>
              <p className="text-xs text-gray-500 mt-1">CRITICAL + HIGH</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">평균 고장 확률</span>
                <Activity className="w-5 h-5 text-orange-500" />
              </div>
              <p className="text-2xl font-bold text-orange-600">
                {formatPercent(statistics.average_failure_probability)}
              </p>
              <p className="text-xs text-gray-500 mt-1">전체 평균</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">예상 총 비용</span>
                <DollarSign className="w-5 h-5 text-green-500" />
              </div>
              <p className="text-2xl font-bold text-green-600">
                {formatCurrency(statistics.total_estimated_cost)}
              </p>
              <p className="text-xs text-gray-500 mt-1">정비 예산</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-600">위험 분포</span>
                <BarChart3 className="w-5 h-5 text-purple-500" />
              </div>
              <div className="flex gap-1 mt-2">
                <div className="flex-1 bg-red-200 h-2 rounded" style={{width: `${(statistics.risk_distribution.critical / statistics.total_vehicles) * 100}%`}}></div>
                <div className="flex-1 bg-orange-200 h-2 rounded" style={{width: `${(statistics.risk_distribution.high / statistics.total_vehicles) * 100}%`}}></div>
                <div className="flex-1 bg-yellow-200 h-2 rounded" style={{width: `${(statistics.risk_distribution.medium / statistics.total_vehicles) * 100}%`}}></div>
                <div className="flex-1 bg-green-200 h-2 rounded" style={{width: `${(statistics.risk_distribution.low / statistics.total_vehicles) * 100}%`}}></div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                C:{statistics.risk_distribution.critical} H:{statistics.risk_distribution.high} M:{statistics.risk_distribution.medium} L:{statistics.risk_distribution.low}
              </p>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow mb-6 p-4">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-gray-700">위험도 필터:</span>
            <div className="flex gap-2">
              {['all', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((risk) => (
                <button
                  key={risk}
                  onClick={() => setSelectedRisk(risk)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    selectedRisk === risk
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {risk === 'all' ? '전체' : risk}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Predictions List */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">차량 예측 목록</h2>
            <p className="text-sm text-gray-600 mt-1">
              {predictions.length}대 차량 분석 결과
            </p>
          </div>

          <div className="p-6">
            {loading ? (
              <div className="text-center py-12">
                <RefreshCw className="w-8 h-8 text-gray-400 animate-spin mx-auto mb-4" />
                <p className="text-gray-500">예측 데이터 로딩 중...</p>
              </div>
            ) : predictions.length === 0 ? (
              <div className="text-center py-12">
                <Brain className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">예측 데이터 없음</h3>
                <p className="text-gray-500 mb-4">
                  {modelStatus?.is_available 
                    ? '필터 조건을 변경해보세요' 
                    : '먼저 모델을 학습해주세요'}
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {predictions.map((pred) => (
                  <div
                    key={pred.vehicle_id}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => setSelectedVehicle(pred)}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start gap-3">
                        <div className="mt-1">
                          <Truck className="w-6 h-6 text-gray-400" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {pred.vehicle_plate}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">
                            차량 ID: {pred.vehicle_id}
                          </p>
                          <p className="text-sm text-gray-700 mt-2 font-medium">
                            {pred.recommendation}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium border ${getRiskColor(pred.risk_level)}`}>
                          {getRiskIcon(pred.risk_level)}
                          {pred.risk_level}
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-4 gap-4 mb-3">
                      <div className="bg-gray-50 p-3 rounded">
                        <span className="text-xs text-gray-600">고장 확률</span>
                        <p className="text-lg font-bold text-gray-900 mt-1">
                          {formatPercent(pred.failure_probability)}
                        </p>
                      </div>
                      <div className="bg-gray-50 p-3 rounded">
                        <span className="text-xs text-gray-600">예상 비용</span>
                        <p className="text-lg font-bold text-gray-900 mt-1">
                          {formatCurrency(pred.estimated_cost)}
                        </p>
                      </div>
                      <div className="bg-gray-50 p-3 rounded">
                        <span className="text-xs text-gray-600">권장 정비</span>
                        <p className="text-lg font-bold text-gray-900 mt-1">
                          {pred.days_until_recommended_maintenance}일 후
                        </p>
                      </div>
                      <div className="bg-gray-50 p-3 rounded">
                        <span className="text-xs text-gray-600">신뢰도</span>
                        <p className="text-lg font-bold text-gray-900 mt-1">
                          {formatPercent(pred.confidence_score)}
                        </p>
                      </div>
                    </div>

                    {/* Key Factors */}
                    <div>
                      <span className="text-xs font-medium text-gray-600">주요 영향 요인:</span>
                      <div className="flex gap-2 mt-2">
                        {pred.key_factors.slice(0, 3).map((factor, idx) => (
                          <span
                            key={idx}
                            className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded"
                          >
                            {factor.factor.replace(/_/g, ' ')} ({formatPercent(factor.importance)})
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Current Stats */}
                    <div className="mt-3 pt-3 border-t border-gray-200 flex gap-6 text-sm text-gray-600">
                      <span>총 주행: {pred.current_stats.total_distance.toLocaleString()}km</span>
                      <span>마지막 정비: {pred.current_stats.days_since_last_maintenance}일 전</span>
                      <span>정비 횟수: {pred.current_stats.total_maintenances}회</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Detail Modal */}
        {selectedVehicle && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {selectedVehicle.vehicle_plate} - 상세 예측
                  </h2>
                  <button
                    onClick={() => setSelectedVehicle(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <XCircle className="w-6 h-6" />
                  </button>
                </div>
              </div>

              <div className="p-6 space-y-6">
                {/* Risk Badge */}
                <div className="text-center">
                  <span className={`inline-flex items-center gap-2 px-6 py-3 rounded-full text-lg font-bold border-2 ${getRiskColor(selectedVehicle.risk_level)}`}>
                    {getRiskIcon(selectedVehicle.risk_level)}
                    {selectedVehicle.risk_level} 위험도
                  </span>
                </div>

                {/* Main Metrics */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg">
                    <span className="text-sm text-red-700">고장 확률</span>
                    <p className="text-3xl font-bold text-red-900 mt-2">
                      {formatPercent(selectedVehicle.failure_probability)}
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg">
                    <span className="text-sm text-green-700">예상 정비 비용</span>
                    <p className="text-3xl font-bold text-green-900 mt-2">
                      {formatCurrency(selectedVehicle.estimated_cost)}
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg">
                    <span className="text-sm text-blue-700">권장 정비 시점</span>
                    <p className="text-3xl font-bold text-blue-900 mt-2">
                      {selectedVehicle.days_until_recommended_maintenance}일 후
                    </p>
                  </div>
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg">
                    <span className="text-sm text-purple-700">예측 신뢰도</span>
                    <p className="text-3xl font-bold text-purple-900 mt-2">
                      {formatPercent(selectedVehicle.confidence_score)}
                    </p>
                  </div>
                </div>

                {/* Recommendation */}
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <Shield className="w-5 h-5 text-yellow-600 mt-0.5" />
                    <div>
                      <h3 className="font-semibold text-yellow-900">권장 조치</h3>
                      <p className="text-yellow-800 mt-1">{selectedVehicle.recommendation}</p>
                    </div>
                  </div>
                </div>

                {/* Key Factors */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">주요 영향 요인</h3>
                  <div className="space-y-2">
                    {selectedVehicle.key_factors.map((factor, idx) => (
                      <div key={idx} className="bg-gray-50 p-3 rounded">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-gray-700">
                            {factor.factor.replace(/_/g, ' ')}
                          </span>
                          <span className="text-sm font-semibold text-gray-900">
                            {formatPercent(factor.importance)}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-purple-600 h-2 rounded-full"
                            style={{ width: `${factor.importance * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Current Stats */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">현재 차량 상태</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-gray-50 p-3 rounded">
                      <span className="text-xs text-gray-600">총 주행거리</span>
                      <p className="text-lg font-bold text-gray-900 mt-1">
                        {selectedVehicle.current_stats.total_distance.toLocaleString()}km
                      </p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <span className="text-xs text-gray-600">마지막 정비</span>
                      <p className="text-lg font-bold text-gray-900 mt-1">
                        {selectedVehicle.current_stats.days_since_last_maintenance}일 전
                      </p>
                    </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <span className="text-xs text-gray-600">총 정비 횟수</span>
                      <p className="text-lg font-bold text-gray-900 mt-1">
                        {selectedVehicle.current_stats.total_maintenances}회
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MLPredictionsPage;
