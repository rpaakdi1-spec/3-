import React from 'react';
import { useTranslation } from 'react-i18next';

interface ComparisonData {
  simulation_a: {
    id: number;
    name: string;
    match_rate: number;
    avg_response_time_ms: number;
    total_distance_km?: number;
    total_cost?: number;
  };
  simulation_b: {
    id: number;
    name: string;
    match_rate: number;
    avg_response_time_ms: number;
    total_distance_km?: number;
    total_cost?: number;
  };
  comparison: {
    match_rate_diff: number;
    response_time_diff: number;
    distance_diff?: number;
    cost_diff?: number;
    winner: 'a' | 'b' | 'tie';
    recommendation: string;
  };
}

interface ComparisonViewProps {
  comparison: ComparisonData;
  onClose: () => void;
}

export const ComparisonView: React.FC<ComparisonViewProps> = ({ comparison, onClose }) => {
  const { t } = useTranslation();

  const getWinnerClass = (isWinner: boolean) => {
    return isWinner ? 'bg-green-50 border-green-500' : 'bg-gray-50 border-gray-300';
  };

  const getDiffColor = (diff: number) => {
    if (diff > 0) return 'text-green-600';
    if (diff < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const formatDiff = (diff: number, unit: string = '') => {
    const sign = diff > 0 ? '+' : '';
    return `${sign}${diff.toFixed(1)}${unit}`;
  };

  const winnerA = comparison.comparison.winner === 'a';
  const winnerB = comparison.comparison.winner === 'b';

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-5xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <h2 className="text-2xl font-bold">{t('simulation.comparison.title', '시뮬레이션 비교')}</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Comparison Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {/* Simulation A */}
            <div className={`border-2 rounded-lg p-6 ${getWinnerClass(winnerA)}`}>
              <h3 className="text-lg font-semibold mb-4 flex items-center justify-between">
                {comparison.simulation_a.name}
                {winnerA && (
                  <span className="px-3 py-1 bg-green-600 text-white text-xs rounded-full">
                    {t('simulation.comparison.winner', '우승')}
                  </span>
                )}
              </h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">{t('simulation.metrics.matchRate', '매칭 성공률')}</p>
                  <p className="text-2xl font-bold">{comparison.simulation_a.match_rate.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">{t('simulation.metrics.avgTime', '평균 응답 시간')}</p>
                  <p className="text-2xl font-bold">{comparison.simulation_a.avg_response_time_ms}ms</p>
                </div>
                {comparison.simulation_a.total_distance_km !== undefined && (
                  <div>
                    <p className="text-sm text-gray-600">{t('simulation.metrics.totalDistance', '총 거리')}</p>
                    <p className="text-2xl font-bold">{comparison.simulation_a.total_distance_km.toFixed(1)}km</p>
                  </div>
                )}
                {comparison.simulation_a.total_cost !== undefined && (
                  <div>
                    <p className="text-sm text-gray-600">{t('simulation.metrics.totalCost', '총 비용')}</p>
                    <p className="text-2xl font-bold">₩{comparison.simulation_a.total_cost.toLocaleString()}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Differences */}
            <div className="flex flex-col justify-center items-center bg-blue-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold mb-4">{t('simulation.comparison.differences', '차이')}</h3>
              <div className="space-y-4 w-full">
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-1">{t('simulation.metrics.matchRate', '매칭률')}</p>
                  <p className={`text-xl font-bold ${getDiffColor(comparison.comparison.match_rate_diff)}`}>
                    {formatDiff(comparison.comparison.match_rate_diff, '%')}
                  </p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-1">{t('simulation.metrics.responseTime', '응답 시간')}</p>
                  <p className={`text-xl font-bold ${getDiffColor(-comparison.comparison.response_time_diff)}`}>
                    {formatDiff(comparison.comparison.response_time_diff, 'ms')}
                  </p>
                </div>
                {comparison.comparison.distance_diff !== undefined && (
                  <div className="text-center">
                    <p className="text-sm text-gray-600 mb-1">{t('simulation.metrics.distance', '거리')}</p>
                    <p className={`text-xl font-bold ${getDiffColor(-comparison.comparison.distance_diff)}`}>
                      {formatDiff(comparison.comparison.distance_diff, 'km')}
                    </p>
                  </div>
                )}
                {comparison.comparison.cost_diff !== undefined && (
                  <div className="text-center">
                    <p className="text-sm text-gray-600 mb-1">{t('simulation.metrics.cost', '비용')}</p>
                    <p className={`text-xl font-bold ${getDiffColor(-comparison.comparison.cost_diff)}`}>
                      {formatDiff(comparison.comparison.cost_diff, '원')}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Simulation B */}
            <div className={`border-2 rounded-lg p-6 ${getWinnerClass(winnerB)}`}>
              <h3 className="text-lg font-semibold mb-4 flex items-center justify-between">
                {comparison.simulation_b.name}
                {winnerB && (
                  <span className="px-3 py-1 bg-green-600 text-white text-xs rounded-full">
                    {t('simulation.comparison.winner', '우승')}
                  </span>
                )}
              </h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600">{t('simulation.metrics.matchRate', '매칭 성공률')}</p>
                  <p className="text-2xl font-bold">{comparison.simulation_b.match_rate.toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">{t('simulation.metrics.avgTime', '평균 응답 시간')}</p>
                  <p className="text-2xl font-bold">{comparison.simulation_b.avg_response_time_ms}ms</p>
                </div>
                {comparison.simulation_b.total_distance_km !== undefined && (
                  <div>
                    <p className="text-sm text-gray-600">{t('simulation.metrics.totalDistance', '총 거리')}</p>
                    <p className="text-2xl font-bold">{comparison.simulation_b.total_distance_km.toFixed(1)}km</p>
                  </div>
                )}
                {comparison.simulation_b.total_cost !== undefined && (
                  <div>
                    <p className="text-sm text-gray-600">{t('simulation.metrics.totalCost', '총 비용')}</p>
                    <p className="text-2xl font-bold">₩{comparison.simulation_b.total_cost.toLocaleString()}</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Recommendation */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {t('simulation.comparison.recommendation', 'AI 추천')}
            </h3>
            <p className="text-gray-700">{comparison.comparison.recommendation}</p>
          </div>
        </div>
      </div>
    </div>
  );
};
