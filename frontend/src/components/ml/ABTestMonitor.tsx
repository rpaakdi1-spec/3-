/**
 * A/B Test Monitor
 * 
 * Phase 3: 실시간 A/B 테스트 모니터링 대시보드
 * - Treatment vs Control 그룹 성과 비교
 * - 실시간 메트릭 표시
 * - 롤아웃 비율 조정
 * - 자동 롤백 트리거
 */

import { useState, useEffect } from 'react'
import { mlDispatchAPI } from '../../services/api'

interface ABTestStats {
  total_users: number
  control_count: number
  treatment_count: number
  actual_treatment_percentage: number
  target_rollout_percentage: number
}

interface GroupMetrics {
  total_dispatches: number
  success_rate: number
  avg_score?: number
  avg_response_time: number
}

interface ABTestMetrics {
  control: GroupMetrics
  treatment: GroupMetrics
  improvements: {
    success_rate: number
    success_rate_percentage: number
  }
  winner: 'control' | 'treatment' | 'tie'
}

interface RolloutHistoryItem {
  timestamp: string
  old_percentage: number
  new_percentage: number
}

export default function ABTestMonitor() {
  const [stats, setStats] = useState<ABTestStats | null>(null)
  const [metrics, setMetrics] = useState<ABTestMetrics | null>(null)
  const [history, setHistory] = useState<RolloutHistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  
  const [rolloutPercentage, setRolloutPercentage] = useState(10)
  const [updating, setUpdating] = useState(false)

  useEffect(() => {
    fetchAllData()
    const interval = setInterval(fetchAllData, 10000) // 10초마다 새로고침
    return () => clearInterval(interval)
  }, [])

  const fetchAllData = async () => {
    try {
      const [statsRes, metricsRes, historyRes] = await Promise.all([
        mlDispatchAPI.getABTestStats(),
        mlDispatchAPI.getABTestMetrics(),
        mlDispatchAPI.getRolloutHistory(10)
      ])

      setStats(statsRes.data)
      setMetrics(metricsRes.data)
      setHistory(historyRes.data.history || [])
      setRolloutPercentage(statsRes.data.target_rollout_percentage)
      setError('')
    } catch (err: any) {
      console.error('A/B Test 데이터 로드 오류:', err)
      setError('데이터를 불러오는데 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const handleUpdateRollout = async () => {
    if (!window.confirm(`롤아웃 비율을 ${rolloutPercentage}%로 변경하시겠습니까?`)) {
      return
    }

    setUpdating(true)
    setError('')

    try {
      await mlDispatchAPI.updateRollout(rolloutPercentage)
      alert('롤아웃 비율이 업데이트되었습니다')
      await fetchAllData()
    } catch (err: any) {
      console.error('롤아웃 업데이트 오류:', err)
      setError(err.response?.data?.detail || '롤아웃 업데이트에 실패했습니다')
    } finally {
      setUpdating(false)
    }
  }

  const getWinnerBadge = (winner: string) => {
    if (winner === 'treatment') {
      return <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded">🏆 ML 승리</span>
    } else if (winner === 'control') {
      return <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-medium rounded">기존 시스템 승리</span>
    } else {
      return <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded">동등</span>
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="ml-3 text-gray-700">A/B 테스트 데이터 로드 중...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">
          🧪 A/B Test Monitor
        </h2>
        <button
          onClick={fetchAllData}
          className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition"
        >
          🔄 새로고침
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {/* 실험 통계 */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <div className="text-sm text-gray-500 mb-1">전체 사용자</div>
            <div className="text-2xl font-bold text-gray-900">{stats.total_users}</div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 shadow-sm">
            <div className="text-sm text-blue-600 mb-1">Control 그룹</div>
            <div className="text-2xl font-bold text-blue-900">{stats.control_count}</div>
            <div className="text-xs text-blue-600 mt-1">
              {((stats.control_count / stats.total_users) * 100).toFixed(1)}%
            </div>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4 shadow-sm">
            <div className="text-sm text-green-600 mb-1">Treatment 그룹 (ML)</div>
            <div className="text-2xl font-bold text-green-900">{stats.treatment_count}</div>
            <div className="text-xs text-green-600 mt-1">
              {((stats.treatment_count / stats.total_users) * 100).toFixed(1)}%
            </div>
          </div>

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 shadow-sm">
            <div className="text-sm text-purple-600 mb-1">목표 롤아웃</div>
            <div className="text-2xl font-bold text-purple-900">{stats.target_rollout_percentage}%</div>
          </div>
        </div>
      )}

      {/* 성과 비교 */}
      {metrics && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">성과 비교</h3>
            {getWinnerBadge(metrics.winner)}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Control 그룹 */}
            <div className="border border-gray-200 rounded-lg p-4">
              <h4 className="font-semibold text-blue-900 mb-3">Control (기존 시스템)</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">총 배차:</span>
                  <span className="font-medium">{metrics.control.total_dispatches}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">성공률:</span>
                  <span className="font-medium">{(metrics.control.success_rate * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">평균 응답시간:</span>
                  <span className="font-medium">{metrics.control.avg_response_time.toFixed(2)}s</span>
                </div>
              </div>
            </div>

            {/* Treatment 그룹 */}
            <div className="border border-green-200 rounded-lg p-4 bg-green-50">
              <h4 className="font-semibold text-green-900 mb-3">Treatment (ML 시스템)</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">총 배차:</span>
                  <span className="font-medium">{metrics.treatment.total_dispatches}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">성공률:</span>
                  <span className="font-medium">{(metrics.treatment.success_rate * 100).toFixed(1)}%</span>
                </div>
                {metrics.treatment.avg_score && (
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">평균 점수:</span>
                    <span className="font-medium">{metrics.treatment.avg_score.toFixed(3)}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">평균 응답시간:</span>
                  <span className="font-medium">{metrics.treatment.avg_response_time.toFixed(2)}s</span>
                </div>
              </div>
            </div>
          </div>

          {/* 개선율 */}
          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-2">개선율</h4>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-2 rounded ${
                metrics.improvements.success_rate_percentage > 0 
                  ? 'bg-green-100 text-green-700' 
                  : metrics.improvements.success_rate_percentage < 0 
                  ? 'bg-red-100 text-red-700' 
                  : 'bg-gray-100 text-gray-700'
              }`}>
                <span className="font-medium">
                  성공률: {metrics.improvements.success_rate_percentage > 0 ? '+' : ''}
                  {metrics.improvements.success_rate_percentage.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 롤아웃 조정 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">롤아웃 비율 조정</h3>
        
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Treatment 그룹 비율 (%)
            </label>
            <input
              type="range"
              min="0"
              max="100"
              step="10"
              value={rolloutPercentage}
              onChange={(e) => setRolloutPercentage(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
          </div>

          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600 mb-2">
              {rolloutPercentage}%
            </div>
            <button
              onClick={handleUpdateRollout}
              disabled={updating || rolloutPercentage === (stats?.target_rollout_percentage || 0)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium rounded-lg transition"
            >
              {updating ? '업데이트 중...' : '적용'}
            </button>
          </div>
        </div>

        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            ⚠️ 권장 롤아웃 전략: 10% → 30% → 50% → 100%
          </p>
        </div>
      </div>

      {/* 롤아웃 히스토리 */}
      {history.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">롤아웃 변경 이력</h3>
          
          <div className="space-y-2">
            {history.map((item, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-4">
                  <span className="text-sm text-gray-500">
                    {new Date(item.timestamp).toLocaleString('ko-KR')}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded">
                      {item.old_percentage}%
                    </span>
                    <span className="text-gray-400">→</span>
                    <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded">
                      {item.new_percentage}%
                    </span>
                  </div>
                </div>
                <span className={`text-sm font-medium ${
                  item.new_percentage > item.old_percentage 
                    ? 'text-green-600' 
                    : 'text-red-600'
                }`}>
                  {item.new_percentage > item.old_percentage ? '↑' : '↓'} 
                  {Math.abs(item.new_percentage - item.old_percentage)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
