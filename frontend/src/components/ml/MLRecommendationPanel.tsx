/**
 * ML Recommendation Panel
 * 
 * Phase 3: ML 기반 배차 추천 UI 컴포넌트
 * - Top 3 차량 추천 표시
 * - 상세 점수 및 이유 표시
 * - 1-Click 배차 기능
 */

import { useState, useEffect } from 'react'
import { mlDispatchAPI } from '../../services/api'

interface MLRecommendation {
  rank: number
  vehicle_id: number
  vehicle_code: string
  score: number
  reason: string
  details: {
    distance_score: number
    rotation_score: number
    time_score: number
    preference_score: number
    voltage_ok: boolean
  }
}

interface OrderMLResult {
  order_id: number
  order_number: string
  temperature_zone: string
  pallet_count: number
  top_3: MLRecommendation[]
  error?: string
}

interface Props {
  orderIds: number[]
  onDispatchComplete?: () => void
}

export default function MLRecommendationPanel({ orderIds, onDispatchComplete }: Props) {
  const [loading, setLoading] = useState(false)
  const [recommendations, setRecommendations] = useState<OrderMLResult[]>([])
  const [error, setError] = useState('')
  const [dispatching, setDispatching] = useState<number | null>(null)

  useEffect(() => {
    if (orderIds.length > 0) {
      fetchMLRecommendations()
    }
  }, [orderIds])

  const fetchMLRecommendations = async () => {
    if (orderIds.length === 0) return

    setLoading(true)
    setError('')

    try {
      const response = await mlDispatchAPI.optimize(orderIds, 'recommend')
      
      if (response.data.results) {
        setRecommendations(response.data.results)
      } else {
        setError('추천 결과를 가져올 수 없습니다')
      }
    } catch (err: any) {
      console.error('ML 추천 오류:', err)
      setError(err.response?.data?.detail || 'ML 추천을 불러오는데 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const handleQuickDispatch = async (orderId: number, vehicleId: number, vehicleCode: string) => {
    if (!window.confirm(`주문을 차량 ${vehicleCode}에 배차하시겠습니까?`)) {
      return
    }

    setDispatching(orderId)
    setError('')

    try {
      // Auto mode로 ML 배차 실행
      const response = await mlDispatchAPI.optimize([orderId], 'auto')
      
      if (response.data.dispatches_created > 0) {
        alert(`배차 완료: ${vehicleCode}`)
        if (onDispatchComplete) {
          onDispatchComplete()
        }
      } else {
        setError('배차에 실패했습니다')
      }
    } catch (err: any) {
      console.error('배차 오류:', err)
      setError(err.response?.data?.detail || '배차 중 오류가 발생했습니다')
    } finally {
      setDispatching(null)
    }
  }

  if (orderIds.length === 0) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center">
        <p className="text-gray-500">주문을 선택하면 ML 추천이 표시됩니다</p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center justify-center space-x-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="text-gray-700">ML 추천 분석 중...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center space-x-2">
          <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          🤖 ML 추천 결과
        </h3>
        <button
          onClick={fetchMLRecommendations}
          className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition"
        >
          🔄 새로고침
        </button>
      </div>

      {recommendations.map((orderResult) => (
        <div
          key={orderResult.order_id}
          className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition"
        >
          {/* 주문 정보 헤더 */}
          <div className="border-b border-gray-100 pb-3 mb-3">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-semibold text-gray-900">
                  {orderResult.order_number}
                </h4>
                <div className="flex items-center space-x-3 mt-1 text-sm text-gray-600">
                  <span className={`px-2 py-0.5 rounded ${
                    orderResult.temperature_zone === '냉동' ? 'bg-blue-100 text-blue-700' :
                    orderResult.temperature_zone === '냉장' ? 'bg-green-100 text-green-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {orderResult.temperature_zone}
                  </span>
                  <span>{orderResult.pallet_count}파레트</span>
                </div>
              </div>
            </div>
          </div>

          {/* 에러 메시지 */}
          {orderResult.error && (
            <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-3">
              <p className="text-sm text-yellow-800">⚠️ {orderResult.error}</p>
            </div>
          )}

          {/* Top 3 추천 */}
          {orderResult.top_3 && orderResult.top_3.length > 0 && (
            <div className="space-y-2">
              {orderResult.top_3.map((rec) => (
                <div
                  key={rec.rank}
                  className={`border rounded-lg p-3 ${
                    rec.rank === 1
                      ? 'border-blue-300 bg-blue-50'
                      : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    {/* 좌측: 순위 & 차량 정보 */}
                    <div className="flex items-start space-x-3 flex-1">
                      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                        rec.rank === 1 ? 'bg-blue-600 text-white' :
                        rec.rank === 2 ? 'bg-gray-400 text-white' :
                        'bg-gray-300 text-white'
                      }`}>
                        {rec.rank}
                      </div>

                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="font-semibold text-gray-900">
                            {rec.vehicle_code}
                          </span>
                          <span className={`px-2 py-0.5 text-xs rounded ${
                            rec.score >= 0.8 ? 'bg-green-100 text-green-700' :
                            rec.score >= 0.7 ? 'bg-blue-100 text-blue-700' :
                            rec.score >= 0.6 ? 'bg-yellow-100 text-yellow-700' :
                            'bg-red-100 text-red-700'
                          }`}>
                            점수: {rec.score.toFixed(3)}
                          </span>
                        </div>

                        <p className="text-sm text-gray-600 mt-1">
                          {rec.reason}
                        </p>

                        {/* 상세 점수 */}
                        <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                          <div className="flex justify-between">
                            <span className="text-gray-500">거리:</span>
                            <span className="font-medium">{rec.details.distance_score.toFixed(2)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">회전:</span>
                            <span className="font-medium">{rec.details.rotation_score.toFixed(2)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">시간:</span>
                            <span className="font-medium">{rec.details.time_score.toFixed(2)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-500">선호:</span>
                            <span className="font-medium">{rec.details.preference_score.toFixed(2)}</span>
                          </div>
                        </div>

                        {/* 전압 상태 */}
                        {!rec.details.voltage_ok && (
                          <div className="mt-2 text-xs text-red-600">
                            ⚠️ 배터리 부족
                          </div>
                        )}
                      </div>
                    </div>

                    {/* 우측: 배차 버튼 (1순위만) */}
                    {rec.rank === 1 && (
                      <button
                        onClick={() => handleQuickDispatch(
                          orderResult.order_id,
                          rec.vehicle_id,
                          rec.vehicle_code
                        )}
                        disabled={dispatching === orderResult.order_id}
                        className="ml-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white text-sm font-medium rounded-lg transition"
                      >
                        {dispatching === orderResult.order_id ? '배차 중...' : '🚚 배차'}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
