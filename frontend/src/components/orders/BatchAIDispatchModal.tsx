import React, { useState, useEffect } from 'react';
import { X, Navigation, CheckCircle2, AlertCircle, Loader2, TrendingUp, MapPin, Clock, User } from 'lucide-react';
import Button from '../common/Button';
import Card from '../common/Card';
import toast from 'react-hot-toast';
import { semiAutoDispatchAPI } from '../../api/semi-auto-dispatch';
import apiClient from '../../api/client';

interface VehicleSuggestion {
  vehicle_id: number;
  vehicle_number: string;
  driver_name?: string;
  driver_phone?: string;
  status: string;
  current_location?: {
    latitude: number;
    longitude: number;
    address?: string;
  };
  distance_km?: number | null;
  estimated_arrival_min?: number | null;
  score: number | null;
  reasons: string[];
  warnings: string[];
  vehicle_info?: {
    max_weight_kg: number;
    max_pallets: number;
    vehicle_type: string;
    forklift_available: boolean;
  };
}

interface OrderWithSuggestions {
  order_id: number;
  order_number: string;
  pickup_address: string;
  delivery_address: string;
  pickup_time: string;
  pallet_count: number;
  temperature_zone: string;
  suggestions: VehicleSuggestion[];
  selected_vehicle_id: number | null;
  loading: boolean;
  error: string | null;
}

interface BatchAIDispatchModalProps {
  isOpen: boolean;
  onClose: () => void;
  orderIds: number[];
  onDispatchComplete: () => void;
}

const BatchAIDispatchModal: React.FC<BatchAIDispatchModalProps> = ({
  isOpen,
  onClose,
  orderIds,
  onDispatchComplete
}) => {
  const [ordersWithSuggestions, setOrdersWithSuggestions] = useState<OrderWithSuggestions[]>([]);
  const [isLoadingAll, setIsLoadingAll] = useState(false);
  const [isDispatching, setIsDispatching] = useState(false);
  const [maxDistance, setMaxDistance] = useState(300);
  const [timeWindow, setTimeWindow] = useState(2);

  useEffect(() => {
    if (isOpen && orderIds.length > 0) {
      loadAllSuggestions();
    }
  }, [isOpen, orderIds]);

  const loadAllSuggestions = async () => {
    setIsLoadingAll(true);
    try {
      const results: OrderWithSuggestions[] = [];

      for (const orderId of orderIds) {
        try {
          const response = await semiAutoDispatchAPI.suggestVehicles(orderId, maxDistance, timeWindow);
          
          if (response.success && response.order) {
            results.push({
              order_id: response.order.id,
              order_number: response.order.order_number,
              pickup_address: response.order.pickup_address,
              delivery_address: response.order.delivery_address,
              pickup_time: response.order.pickup_time,
              pallet_count: response.order.pallet_count,
              temperature_zone: response.order.temperature_zone,
              suggestions: response.suggestions || [],
              selected_vehicle_id: response.suggestions.length > 0 ? response.suggestions[0].vehicle_id : null,
              loading: false,
              error: null
            });
          } else {
            results.push({
              order_id: orderId,
              order_number: `주문 ${orderId}`,
              pickup_address: '-',
              delivery_address: '-',
              pickup_time: '-',
              pallet_count: 0,
              temperature_zone: '-',
              suggestions: [],
              selected_vehicle_id: null,
              loading: false,
              error: '차량 추천을 가져올 수 없습니다'
            });
          }
        } catch (error: any) {
          console.error(`Order ${orderId} suggestion error:`, error);
          results.push({
            order_id: orderId,
            order_number: `주문 ${orderId}`,
            pickup_address: '-',
            delivery_address: '-',
            pickup_time: '-',
            pallet_count: 0,
            temperature_zone: '-',
            suggestions: [],
            selected_vehicle_id: null,
            loading: false,
            error: error.message || '오류 발생'
          });
        }
      }

      setOrdersWithSuggestions(results);
    } catch (error: any) {
      console.error('Load suggestions error:', error);
      toast.error('차량 추천 로딩 중 오류가 발생했습니다');
    } finally {
      setIsLoadingAll(false);
    }
  };

  const handleVehicleSelect = (orderIndex: number, vehicleId: number) => {
    setOrdersWithSuggestions(prev => {
      const updated = [...prev];
      updated[orderIndex].selected_vehicle_id = vehicleId;
      return updated;
    });
  };

  const handleDispatchAll = async () => {
    // 선택된 차량이 있는 주문만 필터링
    const ordersToDispatch = ordersWithSuggestions.filter(
      order => order.selected_vehicle_id !== null && order.suggestions.length > 0
    );

    if (ordersToDispatch.length === 0) {
      toast.error('배차할 주문이 없습니다');
      return;
    }

    if (!window.confirm(`${ordersToDispatch.length}개 주문을 배차하시겠습니까?`)) {
      return;
    }

    setIsDispatching(true);
    let successCount = 0;
    let failCount = 0;

    try {
      for (const order of ordersToDispatch) {
        try {
          await semiAutoDispatchAPI.manualDispatch(order.order_id, order.selected_vehicle_id!);
          successCount++;
        } catch (error) {
          console.error(`Dispatch failed for order ${order.order_id}:`, error);
          failCount++;
        }
      }

      if (successCount > 0) {
        toast.success(`${successCount}개 주문이 배차되었습니다`);
        onDispatchComplete();
        onClose();
      }

      if (failCount > 0) {
        toast.error(`${failCount}개 주문 배차에 실패했습니다`);
      }
    } catch (error: any) {
      console.error('Batch dispatch error:', error);
      toast.error('일괄 배차 중 오류가 발생했습니다');
    } finally {
      setIsDispatching(false);
    }
  };

  const getScoreColor = (score: number | null) => {
    if (score === null || score === 0) return 'bg-gray-100 text-gray-700';
    if (score >= 80) return 'bg-green-100 text-green-700';
    if (score >= 60) return 'bg-yellow-100 text-yellow-700';
    return 'bg-red-100 text-red-700';
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'waiting':
        return <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">대기중</span>;
      case 'nearby_dropoff':
        return <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">하차 예정</span>;
      default:
        return <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">{status}</span>;
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-7xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-6 pb-4 border-b sticky top-0 bg-white z-10">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Navigation className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-bold">일괄 AI 배차</h2>
              <p className="text-sm text-gray-600">
                {orderIds.length}개 주문에 대한 차량 추천 및 배차
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filter Settings */}
        <Card className="mb-6 bg-gray-50">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">최대 거리:</label>
              <input
                type="number"
                value={maxDistance}
                onChange={(e) => setMaxDistance(Number(e.target.value))}
                className="w-24 px-3 py-1 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                min={50}
                max={500}
                step={50}
              />
              <span className="text-sm text-gray-600">km</span>
            </div>
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">시간 여유:</label>
              <input
                type="number"
                value={timeWindow}
                onChange={(e) => setTimeWindow(Number(e.target.value))}
                className="w-20 px-3 py-1 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                min={1}
                max={12}
                step={1}
              />
              <span className="text-sm text-gray-600">시간</span>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={loadAllSuggestions}
              disabled={isLoadingAll}
            >
              {isLoadingAll ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  로딩중...
                </>
              ) : (
                '새로고침'
              )}
            </Button>
          </div>
        </Card>

        {/* Loading State */}
        {isLoadingAll && (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
            <p className="text-gray-600">차량 추천 정보를 불러오는 중...</p>
          </div>
        )}

        {/* Orders with Suggestions */}
        {!isLoadingAll && (
          <div className="space-y-6">
            {ordersWithSuggestions.map((order, orderIndex) => (
              <Card key={order.order_id} className="border-2 border-gray-200">
                {/* Order Header */}
                <div className="bg-gray-50 -m-6 mb-4 p-4 rounded-t-lg border-b">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <span className="text-lg font-bold text-blue-600">
                        {order.order_number}
                      </span>
                      <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm">
                        {order.temperature_zone}
                      </span>
                      <span className="text-sm text-gray-600">
                        팔레트: {order.pallet_count}개
                      </span>
                      <span className="text-sm text-gray-600">
                        <Clock className="w-4 h-4 inline mr-1" />
                        {order.pickup_time?.substring(0, 5)}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600">
                      {order.suggestions.length > 0 ? (
                        <span className="text-green-600 font-medium">
                          {order.suggestions.length}개 차량 추천
                        </span>
                      ) : (
                        <span className="text-red-600 font-medium">
                          추천 차량 없음
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="mt-2 text-sm text-gray-600">
                    <MapPin className="w-4 h-4 inline mr-1" />
                    {order.pickup_address} → {order.delivery_address}
                  </div>
                </div>

                {/* Error State */}
                {order.error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="font-medium text-red-900">오류</p>
                        <p className="text-sm text-red-700 mt-1">{order.error}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* Vehicle Suggestions */}
                {order.suggestions.length > 0 ? (
                  <div className="space-y-3">
                    {order.suggestions.map((suggestion) => (
                      <div
                        key={suggestion.vehicle_id}
                        className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                          order.selected_vehicle_id === suggestion.vehicle_id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => handleVehicleSelect(orderIndex, suggestion.vehicle_id)}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <input
                                type="radio"
                                checked={order.selected_vehicle_id === suggestion.vehicle_id}
                                onChange={() => handleVehicleSelect(orderIndex, suggestion.vehicle_id)}
                                className="w-5 h-5 text-blue-600"
                              />
                              <span className="text-lg font-bold">{suggestion.vehicle_number}</span>
                              {getStatusBadge(suggestion.status)}
                              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreColor(suggestion.score)}`}>
                                점수: {suggestion.score ?? 0}
                              </span>
                            </div>

                            <div className="ml-8 grid grid-cols-2 gap-3 text-sm">
                              <div>
                                <User className="w-4 h-4 inline mr-1 text-gray-500" />
                                <span className="text-gray-700">
                                  {suggestion.driver_name || '미배정'} 
                                  {suggestion.driver_phone && ` (${suggestion.driver_phone})`}
                                </span>
                              </div>
                              <div>
                                <MapPin className="w-4 h-4 inline mr-1 text-gray-500" />
                                <span className="text-gray-700">
                                  {suggestion.distance_km !== null && suggestion.distance_km !== undefined
                                    ? `${suggestion.distance_km.toFixed(1)} km`
                                    : '계산중'}
                                </span>
                              </div>
                              <div>
                                <Clock className="w-4 h-4 inline mr-1 text-gray-500" />
                                <span className="text-gray-700">
                                  {suggestion.estimated_arrival_min !== null && suggestion.estimated_arrival_min !== undefined
                                    ? `약 ${suggestion.estimated_arrival_min}분`
                                    : '-'}
                                </span>
                              </div>
                              {suggestion.vehicle_info && (
                                <div className="text-gray-600">
                                  {suggestion.vehicle_info.vehicle_type} / 
                                  최대 {suggestion.vehicle_info.max_pallets}p / 
                                  {suggestion.vehicle_info.max_weight_kg / 1000}톤
                                </div>
                              )}
                            </div>

                            {/* Reasons */}
                            {suggestion.reasons.length > 0 && (
                              <div className="ml-8 mt-2 space-y-1">
                                {suggestion.reasons.map((reason, idx) => (
                                  <div key={idx} className="text-xs text-green-700 flex items-start gap-1">
                                    <CheckCircle2 className="w-3 h-3 flex-shrink-0 mt-0.5" />
                                    <span>{reason}</span>
                                  </div>
                                ))}
                              </div>
                            )}

                            {/* Warnings */}
                            {suggestion.warnings.length > 0 && (
                              <div className="ml-8 mt-2 space-y-1">
                                {suggestion.warnings.map((warning, idx) => (
                                  <div key={idx} className="text-xs text-orange-600 flex items-start gap-1">
                                    <AlertCircle className="w-3 h-3 flex-shrink-0 mt-0.5" />
                                    <span>{warning}</span>
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : !order.error && (
                  <div className="text-center py-8 text-gray-500">
                    <AlertCircle className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                    <p>추천 가능한 차량이 없습니다</p>
                    <p className="text-sm mt-1">검색 조건을 조정해보세요</p>
                  </div>
                )}
              </Card>
            ))}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-between items-center mt-6 pt-4 border-t sticky bottom-0 bg-white">
          <div className="text-sm text-gray-600">
            {ordersWithSuggestions.filter(o => o.selected_vehicle_id !== null).length} / {ordersWithSuggestions.length} 주문 배차 준비됨
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={onClose} disabled={isDispatching}>
              취소
            </Button>
            <Button
              onClick={handleDispatchAll}
              isLoading={isDispatching}
              disabled={isLoadingAll || ordersWithSuggestions.filter(o => o.selected_vehicle_id !== null).length === 0}
              className="bg-green-600 hover:bg-green-700"
            >
              <CheckCircle2 className="w-4 h-4 mr-2" />
              {isDispatching ? '배차 중...' : `${ordersWithSuggestions.filter(o => o.selected_vehicle_id !== null).length}개 주문 배차하기`}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default BatchAIDispatchModal;
