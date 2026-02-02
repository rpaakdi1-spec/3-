import React, { useState, useEffect } from 'react';
import { Activity, Users, TrendingUp, Settings, RefreshCw } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { mlDispatchAPI } from '../services/api';
import Layout from '../components/common/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';

interface ABTestStats {
  total_users: number;
  control_count: number;
  treatment_count: number;
  actual_treatment_percentage: number;
  target_rollout_percentage: number;
  last_updated: string;
  stats_cache?: {
    control_total?: number;
    treatment_total?: number;
    total_assignments?: number;
  };
}

const ABTestMonitorPage: React.FC = () => {
  const [stats, setStats] = useState<ABTestStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [newRollout, setNewRollout] = useState<number>(10);

  // Fetch AB Test stats
  const fetchStats = async () => {
    try {
      setLoading(true);
      const response = await mlDispatchAPI.getABTestStats();
      setStats(response.data);
      setNewRollout(response.data.target_rollout_percentage);
    } catch (error) {
      console.error('Error fetching AB test stats:', error);
      toast.error('AB Test 통계를 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  // Update rollout percentage
  const updateRollout = async () => {
    try {
      await mlDispatchAPI.updateRollout(newRollout);
      toast.success(`롤아웃 비율이 ${newRollout}%로 업데이트되었습니다`);
      fetchStats();
    } catch (error) {
      console.error('Error updating rollout:', error);
      toast.error('롤아웃 비율 업데이트에 실패했습니다');
    }
  };

  useEffect(() => {
    fetchStats();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <Loading />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AB Test 모니터링</h1>
            <p className="mt-1 text-sm text-gray-500">
              ML Dispatch 시스템의 A/B 테스트 현황을 실시간으로 모니터링합니다
            </p>
          </div>
          <Button
            variant="outline"
            onClick={fetchStats}
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            새로고침
          </Button>
        </div>

        {stats && (
          <>
            {/* Stats Cards */}
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {/* Total Users */}
              <Card>
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="p-3 bg-blue-100 rounded-lg">
                      <Users className="w-6 h-6 text-blue-600" />
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">총 사용자</p>
                    <p className="text-2xl font-semibold text-gray-900">{stats.total_users}</p>
                  </div>
                </div>
              </Card>

              {/* Control Group */}
              <Card>
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="p-3 bg-gray-100 rounded-lg">
                      <Activity className="w-6 h-6 text-gray-600" />
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Control 그룹</p>
                    <p className="text-2xl font-semibold text-gray-900">{stats.control_count}</p>
                    <p className="text-xs text-gray-400">
                      {stats.total_users > 0 
                        ? ((stats.control_count / stats.total_users) * 100).toFixed(1) 
                        : '0.0'}%
                    </p>
                  </div>
                </div>
              </Card>

              {/* Treatment Group */}
              <Card>
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="p-3 bg-green-100 rounded-lg">
                      <TrendingUp className="w-6 h-6 text-green-600" />
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">Treatment 그룹</p>
                    <p className="text-2xl font-semibold text-gray-900">{stats.treatment_count}</p>
                    <p className="text-xs text-gray-400">{stats.actual_treatment_percentage.toFixed(1)}%</p>
                  </div>
                </div>
              </Card>

              {/* Target Rollout */}
              <Card>
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="p-3 bg-purple-100 rounded-lg">
                      <Settings className="w-6 h-6 text-purple-600" />
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">목표 롤아웃</p>
                    <p className="text-2xl font-semibold text-gray-900">{stats.target_rollout_percentage}%</p>
                    <p className="text-xs text-gray-400">설정값</p>
                  </div>
                </div>
              </Card>
            </div>

            {/* Rollout Control */}
            <Card>
              <div className="p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">롤아웃 비율 조정</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Treatment 그룹 비율 (%)
                    </label>
                    <div className="flex items-center space-x-4">
                      <input
                        type="range"
                        min="0"
                        max="100"
                        step="10"
                        value={newRollout}
                        onChange={(e) => setNewRollout(Number(e.target.value))}
                        className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                      />
                      <span className="text-2xl font-semibold text-gray-900 w-16 text-right">
                        {newRollout}%
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between pt-4">
                    <p className="text-sm text-gray-500">
                      현재: {stats.target_rollout_percentage}% → 변경: {newRollout}%
                    </p>
                    <Button
                      onClick={updateRollout}
                      disabled={newRollout === stats.target_rollout_percentage}
                    >
                      롤아웃 비율 업데이트
                    </Button>
                  </div>
                </div>
              </div>
            </Card>

            {/* Stats Cache Details */}
            {stats.stats_cache && (
              <Card>
                <div className="p-6">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">통계 캐시</h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Control Total</p>
                      <p className="text-xl font-semibold text-gray-900">
                        {stats.stats_cache.control_total}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Treatment Total</p>
                      <p className="text-xl font-semibold text-gray-900">
                        {stats.stats_cache.treatment_total}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Total Assignments</p>
                      <p className="text-xl font-semibold text-gray-900">
                        {stats.stats_cache.total_assignments}
                      </p>
                    </div>
                  </div>
                </div>
              </Card>
            )}

            {/* Last Updated */}
            <div className="text-sm text-gray-500 text-center">
              마지막 업데이트: {new Date(stats.last_updated).toLocaleString('ko-KR')}
            </div>
          </>
        )}
      </div>
    </Layout>
  );
};

export default ABTestMonitorPage;
