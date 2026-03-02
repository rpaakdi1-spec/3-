import React, { useState, useEffect } from 'react';
import Modal from '../common/Modal';
import Button from '../common/Button';
import { semiAutoDispatchAPI, VehicleSuggestion } from '../../api/semi-auto-dispatch';
import { Truck, MapPin, Clock, TrendingUp, AlertTriangle, Loader2, Star, Navigation } from 'lucide-react';
import toast from 'react-hot-toast';

interface SemiAutoDispatchModalProps {
  isOpen: boolean;
  onClose: () => void;
  orderId: number;
  orderInfo: {
    order_number: string;
    pickup_address: string;
    delivery_address: string;
    pickup_start_time?: string;
  };
  onDispatchComplete: () => void;
}

const SemiAutoDispatchModal: React.FC<SemiAutoDispatchModalProps> = ({
  isOpen,
  onClose,
  orderId,
  orderInfo,
  onDispatchComplete,
}) => {
  const [loading, setLoading] = useState(true);
  const [suggestions, setSuggestions] = useState<VehicleSuggestion[]>([]);
  const [selectedVehicleId, setSelectedVehicleId] = useState<number | null>(null);
  const [dispatching, setDispatching] = useState(false);
  const [maxDistance, setMaxDistance] = useState(150);
  const [timeWindow, setTimeWindow] = useState(2);

  useEffect(() => {
    if (isOpen) {
      loadSuggestions();
    }
  }, [isOpen, orderId, maxDistance, timeWindow]);

  const loadSuggestions = async () => {
    setLoading(true);
    try {
      const response = await semiAutoDispatchAPI.suggestVehicles(
        orderId,
        maxDistance,
        timeWindow
      );
      
      if (response.success) {
        setSuggestions(response.suggestions);
        // Auto-select the highest scoring vehicle
        if (response.suggestions.length > 0) {
          setSelectedVehicleId(response.suggestions[0].vehicle_id);
        }
      } else {
        toast.error('차량 제안을 불러올 수 없습니다');
      }
    } catch (error: any) {
      console.error('Failed to load vehicle suggestions:', error);
      toast.error(error.response?.data?.detail || '차량 제안 조회 실패');
    } finally {
      setLoading(false);
    }
  };

  const handleDispatch = async () => {
    if (!selectedVehicleId) {
      toast.error('차량을 선택해주세요');
      return;
    }

    setDispatching(true);
    try {
      const response = await semiAutoDispatchAPI.manualDispatch(orderId, selectedVehicleId);
      
      if (response.success) {
        toast.success(response.message);
        onDispatchComplete();
        onClose();
      } else {
        toast.error('배차에 실패했습니다');
      }
    } catch (error: any) {
      console.error('Failed to dispatch:', error);
      toast.error(error.response?.data?.detail || '배차 실패');
    } finally {
      setDispatching(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'waiting':
        return <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">대기 중</span>;
      case 'nearby_dropoff':
        return <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">하차 예정</span>;
      case 'in_transit':
        return <span className="px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded">운행 중</span>;
      default:
        return <span className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded">{status}</span>;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={
        <div>
          <div className="flex items-center gap-2">
            <Navigation className="w-5 h-5 text-blue-600" />
            <span>AI 배차 추천</span>
          </div>
          <div className="text-sm font-normal text-gray-600 mt-1">
            주문번호: {orderInfo.order_number}
          </div>
        </div>
      }
      size="xl"
    >
      <div className="space-y-4">
        {/* 주문 정보 */}
        <div className="bg-blue-50 p-4 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-2">주문 정보</h3>
          <div className="space-y-1 text-sm">
            <div className="flex items-start gap-2">
              <MapPin className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
              <span className="text-gray-700"><strong>상차:</strong> {orderInfo.pickup_address}</span>
            </div>
            <div className="flex items-start gap-2">
              <MapPin className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
              <span className="text-gray-700"><strong>하차:</strong> {orderInfo.delivery_address}</span>
            </div>
            {orderInfo.pickup_start_time && (
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-blue-600" />
                <span className="text-gray-700"><strong>상차 시간:</strong> {new Date(orderInfo.pickup_start_time).toLocaleString('ko-KR')}</span>
              </div>
            )}
          </div>
        </div>

        {/* 검색 옵션 */}
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              최대 거리 (km)
            </label>
            <input
              type="number"
              value={maxDistance}
              onChange={(e) => setMaxDistance(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              min="10"
              max="500"
              step="10"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              시간 여유 (시간)
            </label>
            <input
              type="number"
              value={timeWindow}
              onChange={(e) => setTimeWindow(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              min="1"
              max="12"
              step="1"
            />
          </div>
          <Button
            onClick={loadSuggestions}
            variant="secondary"
            disabled={loading}
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : '새로고침'}
          </Button>
        </div>

        {/* 차량 제안 목록 */}
        <div className="space-y-3">
          <h3 className="font-semibold text-gray-800 flex items-center gap-2">
            <Truck className="w-5 h-5 text-gray-600" />
            추천 차량 ({suggestions.length}개)
          </h3>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
              <span className="ml-3 text-gray-600">차량 정보를 불러오는 중...</span>
            </div>
          ) : suggestions.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Truck className="w-12 h-12 mx-auto mb-3 text-gray-400" />
              <p>배차 가능한 차량이 없습니다</p>
              <p className="text-sm mt-1">검색 조건을 변경해보세요</p>
            </div>
          ) : (
            <div className="max-h-[400px] overflow-y-auto space-y-3">
              {suggestions.map((suggestion) => (
                <div
                  key={suggestion.vehicle_id}
                  onClick={() => setSelectedVehicleId(suggestion.vehicle_id)}
                  className={`
                    border-2 rounded-lg p-4 cursor-pointer transition-all
                    ${selectedVehicleId === suggestion.vehicle_id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300 bg-white'
                    }
                  `}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        <Truck className="w-5 h-5 text-gray-600" />
                        <span className="font-semibold text-lg">{suggestion.vehicle_number}</span>
                      </div>
                      {getStatusBadge(suggestion.status)}
                    </div>
                    <div className="flex items-center gap-2">
                      <Star className={`w-5 h-5 ${getScoreColor(suggestion.score ?? 0)}`} />
                      <span className={`text-2xl font-bold ${getScoreColor(suggestion.score ?? 0)}`}>
                        {(suggestion.score ?? 0).toFixed(0)}
                      </span>
                    </div>
                  </div>

                  {suggestion.driver && (
                    <div className="text-sm text-gray-700 mb-2">
                      <strong>운전자:</strong> {suggestion.driver.name} ({suggestion.driver.phone})
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-3 text-sm mb-3">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-blue-600" />
                      <span className="text-gray-700">
                        <strong>거리:</strong> {suggestion.distance_km != null ? suggestion.distance_km.toFixed(1) : '계산중'} km
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-green-600" />
                      <span className="text-gray-700">
                        <strong>도착:</strong> 약 {suggestion.estimated_arrival_min ?? '-'}분
                      </span>
                    </div>
                  </div>

                  {/* 추천 이유 */}
                  {suggestion.reasons.length > 0 && (
                    <div className="mb-2">
                      <div className="flex items-center gap-1 mb-1">
                        <TrendingUp className="w-4 h-4 text-green-600" />
                        <span className="text-sm font-medium text-gray-700">추천 이유:</span>
                      </div>
                      <ul className="list-disc list-inside space-y-1 text-sm text-gray-600 ml-5">
                        {suggestion.reasons.map((reason, idx) => (
                          <li key={idx}>{reason}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* 주의사항 */}
                  {suggestion.warnings.length > 0 && (
                    <div>
                      <div className="flex items-center gap-1 mb-1">
                        <AlertTriangle className="w-4 h-4 text-yellow-600" />
                        <span className="text-sm font-medium text-gray-700">주의사항:</span>
                      </div>
                      <ul className="list-disc list-inside space-y-1 text-sm text-yellow-700 ml-5">
                        {suggestion.warnings.map((warning, idx) => (
                          <li key={idx}>{warning}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 액션 버튼 */}
        <div className="flex gap-3 pt-4 border-t">
          <Button
            onClick={onClose}
            variant="secondary"
            className="flex-1"
            disabled={dispatching}
          >
            취소
          </Button>
          <Button
            onClick={handleDispatch}
            variant="primary"
            className="flex-1"
            disabled={!selectedVehicleId || dispatching || suggestions.length === 0}
          >
            {dispatching ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin mr-2" />
                배차 중...
              </>
            ) : (
              '배차 완료'
            )}
          </Button>
        </div>
      </div>
    </Modal>
  );
};

export default SemiAutoDispatchModal;
