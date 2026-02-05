import React from 'react';
import { Truck, MapPin, Thermometer, Weight, CheckCircle, AlertCircle, Wrench } from 'lucide-react';

interface MobileVehicleCardProps {
  vehicle: {
    id: number;
    license_plate: string;
    vehicle_type: string;
    capacity_ton: number;
    temp_min?: number;
    temp_max?: number;
    status: string;
    current_location_lat?: number;
    current_location_lon?: number;
    last_location_update?: string;
  };
  onEdit?: () => void;
  onViewLocation?: () => void;
}

const statusColors = {
  AVAILABLE: 'bg-green-100 text-green-700',
  DISPATCHED: 'bg-blue-100 text-blue-700',
  MAINTENANCE: 'bg-yellow-100 text-yellow-700',
  INACTIVE: 'bg-gray-100 text-gray-700',
};

const statusIcons = {
  AVAILABLE: CheckCircle,
  DISPATCHED: Truck,
  MAINTENANCE: Wrench,
  INACTIVE: AlertCircle,
};

const statusLabels = {
  AVAILABLE: '가용',
  DISPATCHED: '배차중',
  MAINTENANCE: '정비',
  INACTIVE: '비활성',
};

const vehicleTypeLabels: { [key: string]: string } = {
  FROZEN: '냉동',
  REFRIGERATED: '냉장',
  BOTH: '냉동/냉장',
};

export const MobileVehicleCard: React.FC<MobileVehicleCardProps> = ({
  vehicle,
  onEdit,
  onViewLocation,
}) => {
  const StatusIcon = statusIcons[vehicle.status as keyof typeof statusIcons] || AlertCircle;
  
  const hasLocation = vehicle.current_location_lat && vehicle.current_location_lon;

  return (
    <div
      className="bg-white rounded-lg shadow-sm p-4 mb-3 border border-gray-200"
      onClick={onEdit}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <Truck className="w-5 h-5 text-blue-600" />
            <h3 className="font-bold text-lg text-gray-900">{vehicle.license_plate}</h3>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            {vehicleTypeLabels[vehicle.vehicle_type] || vehicle.vehicle_type}
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <span
            className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
              statusColors[vehicle.status as keyof typeof statusColors] || statusColors.INACTIVE
            }`}
          >
            <StatusIcon className="w-3 h-3" />
            {statusLabels[vehicle.status as keyof typeof statusLabels] || vehicle.status}
          </span>
        </div>
      </div>

      {/* Specs */}
      <div className="grid grid-cols-2 gap-3 mb-3">
        <div className="flex items-center gap-2 text-sm">
          <Weight className="w-4 h-4 text-gray-400" />
          <span className="text-gray-700">{vehicle.capacity_ton}톤</span>
        </div>
        
        {vehicle.temp_min !== undefined && vehicle.temp_max !== undefined && (
          <div className="flex items-center gap-2 text-sm">
            <Thermometer className="w-4 h-4 text-gray-400" />
            <span className="text-gray-700">
              {vehicle.temp_min}°C ~ {vehicle.temp_max}°C
            </span>
          </div>
        )}
      </div>

      {/* Location */}
      {hasLocation && (
        <div className="pt-3 border-t border-gray-100">
          <button
            onClick={(e) => {
              e.stopPropagation();
              onViewLocation?.();
            }}
            className="flex items-center gap-2 text-sm text-blue-600 hover:text-blue-800 active:scale-95 transition-transform"
          >
            <MapPin className="w-4 h-4" />
            <span>현재 위치 보기</span>
            {vehicle.last_location_update && (
              <span className="text-xs text-gray-400">
                ({new Date(vehicle.last_location_update).toLocaleTimeString('ko-KR', {
                  hour: '2-digit',
                  minute: '2-digit',
                })})
              </span>
            )}
          </button>
        </div>
      )}
    </div>
  );
};
