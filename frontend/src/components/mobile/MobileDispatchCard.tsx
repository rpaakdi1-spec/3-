import React from 'react';
import { Truck, User, Package, MapPin, Clock, AlertCircle } from 'lucide-react';

interface MobileDispatchCardProps {
  dispatch: {
    id: number;
    dispatch_number: string;
    dispatch_date: string;
    vehicle?: {
      license_plate: string;
      vehicle_type: string;
    };
    driver?: {
      name: string;
    };
    status: string;
    total_orders: number;
    total_pallets: number;
    estimated_duration_minutes?: number;
    is_urgent?: boolean;
  };
  onClick?: () => void;
}

const statusColors = {
  DRAFT: 'bg-gray-100 text-gray-700',
  CONFIRMED: 'bg-blue-100 text-blue-700',
  IN_PROGRESS: 'bg-yellow-100 text-yellow-700',
  COMPLETED: 'bg-green-100 text-green-700',
  CANCELLED: 'bg-red-100 text-red-700',
};

const statusLabels = {
  DRAFT: '임시저장',
  CONFIRMED: '확정',
  IN_PROGRESS: '진행중',
  COMPLETED: '완료',
  CANCELLED: '취소',
};

export const MobileDispatchCard: React.FC<MobileDispatchCardProps> = ({
  dispatch,
  onClick,
}) => {
  return (
    <div
      className="bg-white rounded-lg shadow-sm p-4 mb-3 active:bg-gray-50 cursor-pointer border border-gray-200"
      onClick={onClick}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-gray-900">{dispatch.dispatch_number}</h3>
            {dispatch.is_urgent && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-700">
                <AlertCircle className="w-3 h-3" />
                긴급
              </span>
            )}
          </div>
          <p className="text-sm text-gray-500 mt-1">{dispatch.dispatch_date}</p>
        </div>
        
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${
            statusColors[dispatch.status as keyof typeof statusColors] || statusColors.DRAFT
          }`}
        >
          {statusLabels[dispatch.status as keyof typeof statusLabels] || dispatch.status}
        </span>
      </div>

      {/* Vehicle & Driver */}
      <div className="space-y-2 mb-3">
        {dispatch.vehicle && (
          <div className="flex items-center text-sm">
            <Truck className="w-4 h-4 text-gray-400 mr-2" />
            <span className="text-gray-700">
              {dispatch.vehicle.license_plate}
              <span className="text-gray-400 ml-2">({dispatch.vehicle.vehicle_type})</span>
            </span>
          </div>
        )}
        
        {dispatch.driver && (
          <div className="flex items-center text-sm">
            <User className="w-4 h-4 text-gray-400 mr-2" />
            <span className="text-gray-700">{dispatch.driver.name}</span>
          </div>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-2 pt-3 border-t border-gray-100">
        <div className="flex items-center justify-center gap-1.5 text-sm">
          <Package className="w-4 h-4 text-gray-400" />
          <span className="text-gray-700">{dispatch.total_orders}건</span>
        </div>
        
        <div className="flex items-center justify-center gap-1.5 text-sm">
          <MapPin className="w-4 h-4 text-gray-400" />
          <span className="text-gray-700">{dispatch.total_pallets}팔레트</span>
        </div>
        
        {dispatch.estimated_duration_minutes && (
          <div className="flex items-center justify-center gap-1.5 text-sm">
            <Clock className="w-4 h-4 text-gray-400" />
            <span className="text-gray-700">
              {Math.floor(dispatch.estimated_duration_minutes / 60)}시간
            </span>
          </div>
        )}
      </div>
    </div>
  );
};
