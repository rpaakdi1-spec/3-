import React, { useState } from 'react';
import { X } from 'lucide-react';
import UvisTemperatureChart from './UvisTemperatureChart';

interface TemperatureChartModalProps {
  vehicleId: number;
  vehiclePlate: string;
  isOpen: boolean;
  onClose: () => void;
}

const TemperatureChartModal: React.FC<TemperatureChartModalProps> = ({
  vehicleId,
  vehiclePlate,
  isOpen,
  onClose,
}) => {
  const [hours, setHours] = useState(24);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">온도 모니터링</h2>
            <p className="text-sm text-gray-600 mt-1">{vehiclePlate}</p>
          </div>
          <div className="flex items-center gap-3">
            {/* 시간 선택 */}
            <select
              value={hours}
              onChange={(e) => setHours(Number(e.target.value))}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={6}>최근 6시간</option>
              <option value={12}>최근 12시간</option>
              <option value={24}>최근 24시간</option>
              <option value={48}>최근 48시간</option>
              <option value={72}>최근 72시간</option>
              <option value={168}>최근 7일</option>
            </select>

            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          <UvisTemperatureChart
            vehicleId={vehicleId}
            hours={hours}
            autoRefresh={true}
            refreshInterval={30000}
          />
        </div>
      </div>
    </div>
  );
};

export default TemperatureChartModal;
