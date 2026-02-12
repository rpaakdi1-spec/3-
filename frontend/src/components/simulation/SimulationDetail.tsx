import React from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';

interface SimulationDetail {
  id: number;
  name: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
  rule_conditions: any;
  test_data: any;
  results?: {
    total_orders: number;
    matched_orders: number;
    unmatched_orders: number;
    match_rate: number;
    avg_response_time_ms: number;
    min_response_time_ms: number;
    max_response_time_ms: number;
    total_distance_km?: number;
    total_cost?: number;
    total_time_minutes?: number;
    matched_results: Array<{
      order_id: number;
      driver_id: number;
      driver_name: string;
      distance_km: number;
      estimated_cost: number;
      estimated_time_minutes: number;
      match_score: number;
    }>;
  };
  error_message?: string;
}

interface SimulationDetailProps {
  simulation: SimulationDetail;
  onClose: () => void;
}

export const SimulationDetail: React.FC<SimulationDetailProps> = ({ simulation, onClose }) => {
  const { t } = useTranslation();

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-bold">{simulation.name}</h2>
              {simulation.description && (
                <p className="text-gray-600 mt-2">{simulation.description}</p>
              )}
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Status */}
          <div className="mb-6">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              simulation.status === 'completed' ? 'bg-green-100 text-green-800' :
              simulation.status === 'running' ? 'bg-blue-100 text-blue-800' :
              simulation.status === 'failed' ? 'bg-red-100 text-red-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {t(`simulation.status.${simulation.status}`, simulation.status)}
            </span>
          </div>

          {/* Results Summary */}
          {simulation.results && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-4">{t('simulation.results.summary', '결과 요약')}</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">{t('simulation.metrics.totalOrders', '전체 주문')}</p>
                  <p className="text-2xl font-bold text-blue-600">{simulation.results.total_orders}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">{t('simulation.metrics.matched', '매칭 성공')}</p>
                  <p className="text-2xl font-bold text-green-600">{simulation.results.matched_orders}</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">{t('simulation.metrics.matchRate', '성공률')}</p>
                  <p className="text-2xl font-bold text-purple-600">{simulation.results.match_rate.toFixed(1)}%</p>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600">{t('simulation.metrics.avgTime', '평균 시간')}</p>
                  <p className="text-2xl font-bold text-orange-600">{simulation.results.avg_response_time_ms}ms</p>
                </div>
              </div>
            </div>
          )}

          {/* Performance Metrics */}
          {simulation.results && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-4">{t('simulation.performance', '성능 지표')}</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="border p-4 rounded-lg">
                  <p className="text-sm text-gray-600">{t('simulation.metrics.minTime', '최소 시간')}</p>
                  <p className="text-xl font-semibold">{simulation.results.min_response_time_ms}ms</p>
                </div>
                <div className="border p-4 rounded-lg">
                  <p className="text-sm text-gray-600">{t('simulation.metrics.maxTime', '최대 시간')}</p>
                  <p className="text-xl font-semibold">{simulation.results.max_response_time_ms}ms</p>
                </div>
                <div className="border p-4 rounded-lg">
                  <p className="text-sm text-gray-600">{t('simulation.metrics.totalDistance', '총 거리')}</p>
                  <p className="text-xl font-semibold">
                    {simulation.results.total_distance_km?.toFixed(1) ?? 'N/A'}km
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Matched Results Table */}
          {simulation.results && simulation.results.matched_results.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-4">{t('simulation.matchedResults', '매칭 결과')}</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        {t('simulation.table.orderId', '주문 ID')}
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        {t('simulation.table.driverName', '기사명')}
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        {t('simulation.table.distance', '거리')}
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        {t('simulation.table.cost', '비용')}
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        {t('simulation.table.time', '시간')}
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        {t('simulation.table.score', '점수')}
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {simulation.results.matched_results.map((result, index) => (
                      <tr key={index}>
                        <td className="px-4 py-3 text-sm">#{result.order_id}</td>
                        <td className="px-4 py-3 text-sm">{result.driver_name}</td>
                        <td className="px-4 py-3 text-sm">{result.distance_km.toFixed(1)}km</td>
                        <td className="px-4 py-3 text-sm">₩{result.estimated_cost.toLocaleString()}</td>
                        <td className="px-4 py-3 text-sm">{result.estimated_time_minutes}분</td>
                        <td className="px-4 py-3 text-sm">
                          <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
                            {result.match_score.toFixed(1)}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Error Message */}
          {simulation.error_message && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <h3 className="text-lg font-semibold text-red-800 mb-2">
                {t('simulation.error', '오류')}
              </h3>
              <p className="text-red-700">{simulation.error_message}</p>
            </div>
          )}

          {/* Timestamps */}
          <div className="flex justify-between text-sm text-gray-500 pt-4 border-t">
            <p>{t('simulation.createdAt', '생성일')}: {format(new Date(simulation.created_at), 'yyyy-MM-dd HH:mm:ss')}</p>
            {simulation.completed_at && (
              <p>{t('simulation.completedAt', '완료일')}: {format(new Date(simulation.completed_at), 'yyyy-MM-dd HH:mm:ss')}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimulationDetail;
