/**
 * Mobile Order Card
 * 모바일 최적화된 주문 카드
 */
import React from 'react';
import { Order } from '../../types';
import { MapPin, Package, Thermometer, Calendar, Clock } from 'lucide-react';

interface MobileOrderCardProps {
  order: Order;
  onSelect?: (order: Order) => void;
  isSelected?: boolean;
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'PENDING':
      return 'bg-yellow-100 text-yellow-800';
    case 'ASSIGNED':
      return 'bg-blue-100 text-blue-800';
    case 'IN_TRANSIT':
      return 'bg-purple-100 text-purple-800';
    case 'DELIVERED':
      return 'bg-green-100 text-green-800';
    case 'CANCELLED':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case 'PENDING':
      return '대기';
    case 'ASSIGNED':
      return '배차완료';
    case 'IN_TRANSIT':
      return '운송중';
    case 'DELIVERED':
      return '배송완료';
    case 'CANCELLED':
      return '취소';
    default:
      return status;
  }
};

const getTempZoneColor = (zone: string) => {
  if (zone === '냉동') return 'text-blue-600';
  if (zone === '냉장') return 'text-green-600';
  return 'text-orange-600';
};

export const MobileOrderCard: React.FC<MobileOrderCardProps> = ({
  order,
  onSelect,
  isSelected = false,
}) => {
  return (
    <div
      onClick={() => onSelect && onSelect(order)}
      className={`
        bg-white rounded-lg border p-4 mb-3 shadow-sm
        ${isSelected ? 'border-indigo-500 ring-2 ring-indigo-100' : 'border-gray-200'}
        ${onSelect ? 'active:bg-gray-50' : ''}
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="text-sm font-semibold text-gray-900">
            {order.order_number}
          </div>
          <div className="text-xs text-gray-500 mt-0.5">
            {order.order_date}
          </div>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
          {getStatusText(order.status)}
        </span>
      </div>

      {/* Route */}
      <div className="space-y-2 mb-3">
        <div className="flex items-start gap-2">
          <MapPin size={16} className="text-green-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="text-xs text-gray-500">상차</div>
            <div className="text-sm text-gray-900 truncate">
              {order.pickup_client_name || order.pickup_address || '미정'}
            </div>
          </div>
        </div>

        <div className="flex items-start gap-2">
          <MapPin size={16} className="text-red-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1 min-w-0">
            <div className="text-xs text-gray-500">하차</div>
            <div className="text-sm text-gray-900 truncate">
              {order.delivery_client_name || order.delivery_address || '미정'}
            </div>
          </div>
        </div>
      </div>

      {/* Details */}
      <div className="flex items-center gap-3 text-xs text-gray-600">
        <div className="flex items-center gap-1">
          <Package size={14} />
          <span>{order.pallet_count}판</span>
        </div>
        <div className={`flex items-center gap-1 ${getTempZoneColor(order.temperature_zone)}`}>
          <Thermometer size={14} />
          <span>{order.temperature_zone}</span>
        </div>
        {order.weight_kg && order.weight_kg > 0 && (
          <div className="flex items-center gap-1">
            <span>{order.weight_kg}kg</span>
          </div>
        )}
      </div>

      {/* Time */}
      {(order.pickup_start_time || order.delivery_start_time) && (
        <div className="mt-2 pt-2 border-t border-gray-100 flex items-center gap-3 text-xs text-gray-500">
          {order.pickup_start_time && (
            <div className="flex items-center gap-1">
              <Clock size={12} />
              <span>상차 {order.pickup_start_time}</span>
            </div>
          )}
          {order.delivery_start_time && (
            <div className="flex items-center gap-1">
              <Clock size={12} />
              <span>하차 {order.delivery_start_time}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MobileOrderCard;
