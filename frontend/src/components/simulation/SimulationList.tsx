import React from 'react';
import { useTranslation } from 'react-i18next';
import { format } from 'date-fns';

interface Simulation {
  id: number;
  name: string;
  description?: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
  metrics?: {
    total_orders: number;
    matched_orders: number;
    match_rate: number;
    avg_response_time_ms: number;
  };
}

interface SimulationListProps {
  simulations: Simulation[];
  onSelect: (simulation: Simulation) => void;
  onDelete: (simulationId: number) => void;
}

export const SimulationList: React.FC<SimulationListProps> = ({
  simulations,
  onSelect,
  onDelete,
}) => {
  const { t } = useTranslation();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">{t('simulation.list.title', '시뮬레이션 목록')}</h2>
      
      {simulations.length === 0 ? (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-500">{t('simulation.list.empty', '시뮬레이션 기록이 없습니다')}</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {simulations.map((simulation) => (
            <div
              key={simulation.id}
              className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => onSelect(simulation)}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg">{simulation.name}</h3>
                  {simulation.description && (
                    <p className="text-sm text-gray-600 mt-1">{simulation.description}</p>
                  )}
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(simulation.status)}`}>
                  {t(`simulation.status.${simulation.status}`, simulation.status)}
                </span>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
                {simulation.metrics && (
                  <>
                    <div>
                      <p className="text-xs text-gray-500">{t('simulation.metrics.totalOrders', '전체 주문')}</p>
                      <p className="text-lg font-semibold">{simulation.metrics.total_orders}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">{t('simulation.metrics.matched', '매칭 성공')}</p>
                      <p className="text-lg font-semibold">{simulation.metrics.matched_orders}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">{t('simulation.metrics.matchRate', '성공률')}</p>
                      <p className="text-lg font-semibold">{simulation.metrics.match_rate.toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">{t('simulation.metrics.avgTime', '평균 시간')}</p>
                      <p className="text-lg font-semibold">{simulation.metrics.avg_response_time_ms}ms</p>
                    </div>
                  </>
                )}
              </div>

              <div className="flex justify-between items-center mt-4 pt-4 border-t">
                <p className="text-xs text-gray-500">
                  {t('simulation.createdAt', '생성일')}: {format(new Date(simulation.created_at), 'yyyy-MM-dd HH:mm')}
                </p>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(simulation.id);
                  }}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  {t('common.delete', '삭제')}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SimulationList;
