/**
 * Phase 15: ML Auto-Learning Dashboard
 * AI 자동 학습 시스템 모니터링 및 관리
 */
import React, { useState, useEffect } from 'react';
import {
  Brain,
  TrendingUp,
  Activity,
  Play,
  Pause,
  CheckCircle,
  XCircle,
  RefreshCw,
  Zap,
  BarChart3,
  Settings
} from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import apiClient from '../api/client';

interface MLStatistics {
  period_days: number;
  training_data: {
    total_samples: number;
    completed_episodes: number;
    average_reward: number;
  };
  experiments: {
    total: number;
    completed: number;
  };
  models: {
    total: number;
    deployed: number;
  };
  reward_trend: Array<{
    timestamp: string;
    reward: number;
  }>;
}

interface Experiment {
  id: number;
  experiment_name: string;
  status: string;
  best_reward: number;
  best_epoch: number;
  started_at: string;
  completed_at: string;
  duration_seconds: number;
}

interface ModelVersion {
  id: number;
  version: string;
  model_name: string;
  model_type: string;
  status: string;
  is_active: boolean;
  deployed_at: string;
  ab_test_traffic_percent: number;
  performance_metrics: any;
}

const MLAutoLearningDashboard: React.FC = () => {
  const [statistics, setStatistics] = useState<MLStatistics | null>(null);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [models, setModels] = useState<ModelVersion[]>([]);
  const [activeModel, setActiveModel] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState<'overview' | 'experiments' | 'models'>('overview');

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000); // 30초마다 갱신
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, expsRes, modelsRes, activeRes] = await Promise.all([
        apiClient.get('/ml/statistics?days=7'),
        apiClient.get('/ml/experiments?limit=10'),
        apiClient.get('/ml/models?limit=10'),
        apiClient.get('/ml/models/active')
      ]);

      setStatistics(statsRes.data);
      setExperiments(expsRes.data.experiments);
      setModels(modelsRes.data.models);
      setActiveModel(activeRes.data.active ? activeRes.data.model : null);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load ML data:', error);
      setLoading(false);
    }
  };

  const handleCreateExperiment = async () => {
    try {
      const experimentName = `실험_${new Date().toISOString().split('T')[0]}`;
      const hyperparameters = {
        learning_rate: 0.0003,
        gamma: 0.99,
        clip_range: 0.2,
        n_steps: 2048
      };

      await apiClient.post('/ml/experiments', null, {
        params: {
          experiment_name: experimentName,
          hyperparameters: JSON.stringify(hyperparameters)
        }
      });

      alert('실험이 생성되었습니다!');
      loadData();
    } catch (error) {
      console.error('Failed to create experiment:', error);
      alert('실험 생성 실패');
    }
  };

  const handleStartTraining = async (experimentId: number) => {
    try {
      await apiClient.post(`/ml/experiments/${experimentId}/train?epochs=100&batch_size=32`);
      alert('학습이 시작되었습니다!');
      loadData();
    } catch (error) {
      console.error('Failed to start training:', error);
      alert('학습 시작 실패');
    }
  };

  const handleDeployModel = async (modelId: number) => {
    try {
      const traffic = prompt('A/B 테스트 트래픽 비율을 입력하세요 (0.0 ~ 1.0):', '0.1');
      if (traffic === null) return;

      await apiClient.post(`/ml/models/${modelId}/deploy?ab_test_traffic=${traffic}`);
      alert('모델이 배포되었습니다!');
      loadData();
    } catch (error) {
      console.error('Failed to deploy model:', error);
      alert('모델 배포 실패');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="animate-spin" size={32} />
        <span className="ml-3 text-lg">로딩 중...</span>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Brain size={36} className="text-purple-600" />
            AI 자동 학습 시스템
          </h1>
          <p className="text-gray-600 mt-1">
            강화학습 기반 배차 최적화 및 자동 성능 개선
          </p>
        </div>
        <button
          onClick={handleCreateExperiment}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
        >
          <Play size={20} />
          새 실험 시작
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        {[
          { id: 'overview', label: '개요', icon: Activity },
          { id: 'experiments', label: '학습 실험', icon: Brain },
          { id: 'models', label: '모델 버전', icon: Zap }
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setSelectedTab(tab.id as any)}
            className={`flex items-center gap-2 px-4 py-2 border-b-2 transition-colors ${
              selectedTab === tab.id
                ? 'border-purple-600 text-purple-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            <tab.icon size={20} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {selectedTab === 'overview' && statistics && (
        <div className="space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">학습 데이터</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {statistics.training_data.total_samples.toLocaleString()}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    완료: {statistics.training_data.completed_episodes}
                  </p>
                </div>
                <BarChart3 size={32} className="text-blue-600" />
              </div>
            </div>

            <div className="bg-green-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">학습 실험</p>
                  <p className="text-2xl font-bold text-green-600">
                    {statistics.experiments.completed}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    전체: {statistics.experiments.total}
                  </p>
                </div>
                <Brain size={32} className="text-green-600" />
              </div>
            </div>

            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">모델 버전</p>
                  <p className="text-2xl font-bold text-purple-600">
                    {statistics.models.deployed}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    전체: {statistics.models.total}
                  </p>
                </div>
                <Zap size={32} className="text-purple-600" />
              </div>
            </div>

            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">평균 보상</p>
                  <p className="text-2xl font-bold text-yellow-600">
                    {statistics.training_data.average_reward.toFixed(3)}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">최근 7일</p>
                </div>
                <TrendingUp size={32} className="text-yellow-600" />
              </div>
            </div>
          </div>

          {/* Active Model */}
          {activeModel && (
            <div className="bg-gradient-to-r from-purple-500 to-blue-500 text-white p-6 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle size={24} />
                    <span className="text-lg font-semibold">활성 모델</span>
                  </div>
                  <p className="text-2xl font-bold">{activeModel.model_name} v{activeModel.version}</p>
                  <p className="text-sm opacity-90 mt-1">
                    배포: {new Date(activeModel.deployed_at).toLocaleDateString()} | 
                    A/B 테스트: {(activeModel.ab_test_traffic_percent * 100).toFixed(0)}% 트래픽
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-sm opacity-90">모델 타입</p>
                  <p className="text-xl font-bold">{activeModel.model_type}</p>
                </div>
              </div>
            </div>
          )}

          {/* Reward Trend Chart */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold mb-4">보상 추이</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={statistics.reward_trend.reverse()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="reward" 
                  stroke="#8b5cf6" 
                  strokeWidth={2}
                  name="보상"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Experiments Tab */}
      {selectedTab === 'experiments' && (
        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    실험명
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    상태
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    최고 보상
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    최고 에포크
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    소요 시간
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    액션
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {experiments.map(exp => (
                  <tr key={exp.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {exp.experiment_name}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        exp.status === 'completed' ? 'bg-green-100 text-green-800' :
                        exp.status === 'running' ? 'bg-blue-100 text-blue-800' :
                        exp.status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {exp.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {exp.best_reward ? exp.best_reward.toFixed(4) : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {exp.best_epoch || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {exp.duration_seconds ? `${Math.floor(exp.duration_seconds / 60)}분` : 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {exp.status === 'initialized' && (
                        <button
                          onClick={() => handleStartTraining(exp.id)}
                          className="text-purple-600 hover:text-purple-800 flex items-center gap-1"
                        >
                          <Play size={16} />
                          학습 시작
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Models Tab */}
      {selectedTab === 'models' && (
        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    버전
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    모델명
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    타입
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    상태
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    활성
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    액션
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {models.map(model => (
                  <tr key={model.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      v{model.version}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {model.model_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {model.model_type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        model.status === 'deployed' ? 'bg-green-100 text-green-800' :
                        model.status === 'validated' ? 'bg-blue-100 text-blue-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {model.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {model.is_active ? (
                        <CheckCircle size={20} className="text-green-600" />
                      ) : (
                        <XCircle size={20} className="text-gray-400" />
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {model.status === 'validated' && !model.is_active && (
                        <button
                          onClick={() => handleDeployModel(model.id)}
                          className="text-purple-600 hover:text-purple-800 flex items-center gap-1"
                        >
                          <Zap size={16} />
                          배포
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default MLAutoLearningDashboard;
