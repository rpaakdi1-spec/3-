import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Truck, MapPin, Package, Clock, AlertCircle, RefreshCw, Navigation, Loader2, CheckCircle } from 'lucide-react';
import Layout from '../components/common/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { toast } from 'react-hot-toast';
import apiClient from '../api/client';
import { Order } from '../types';

interface Vehicle {
  id: number;
  code: string;
  license_plate: string;
  vehicle_type: string;
  status: string;
  max_pallets: number;
  current_pallets?: number;
  driver_name?: string;
  assigned_orders?: AssignedOrder[];
  gps_data?: {
    latitude?: number;
    longitude?: number;
    current_address?: string;
    last_updated?: string;
  };
}

interface AssignedOrder {
  order_number: string;
  pickup_address?: string;
  delivery_address: string;
  pallet_count: number;
  temperature_zone: string;
  distance_km?: number;
  estimated_time?: number;
}

interface OptimizationResult {
  total_vehicles_used: number;
  total_pallets: number;
  total_distance_km: number;
  estimated_total_time_minutes: number;
  vehicle_assignments: VehicleAssignment[];
  dispatch_ids?: number[];
}

interface VehicleAssignment {
  vehicle: Vehicle;
  orders: AssignedOrder[];
  total_pallets: number;
  utilization_percentage: number;
  route_distance_km: number;
  estimated_time_minutes: number;
  dispatch_id?: number;
  confirmed?: boolean;
}

const OptimizationPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [isConfirmed, setIsConfirmed] = useState(false);
  const [confirmingVehicleId, setConfirmingVehicleId] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      // URL 파라미터에서 주문 ID 읽기
      const orderIdsParam = searchParams.get('order_ids');
      const orderIds = orderIdsParam ? orderIdsParam.split(',').map(id => parseInt(id)) : [];

      // 차량 목록 조회 (GPS 데이터 포함)
      const vehiclesData = await apiClient.getVehicles({ include_gps: true });
      const availableVehicles = (vehiclesData.items || vehiclesData || []).filter(
        (v: Vehicle) => v.status === '운행가능'
      );
      setVehicles(availableVehicles);

      // 주문 목록 조회
      if (orderIds.length > 0) {
        const ordersData = await apiClient.getOrders();
        const allOrders = ordersData.items || ordersData.data?.items || ordersData.data || [];
        const selectedOrders = allOrders.filter((order: Order) => orderIds.includes(order.id));
        setOrders(selectedOrders);
        
        if (selectedOrders.length === 0) {
          toast.error('선택한 주문을 찾을 수 없습니다.');
        } else {
          toast.success(`${selectedOrders.length}건의 주문을 불러왔습니다.`);
        }
      } else {
        // URL 파라미터가 없으면 PENDING 주문 자동 조회
        const ordersData = await apiClient.getOrders();
        const allOrders = ordersData.items || ordersData.data?.items || ordersData.data || [];
        const pendingOrders = allOrders.filter((order: Order) => 
          order.status === 'PENDING' || order.status === '배차대기'
        );
        setOrders(pendingOrders);
        
        if (pendingOrders.length > 0) {
          toast.success(`${pendingOrders.length}건의 대기 주문을 불러왔습니다.`);
        }
      }
    } catch (error) {
      console.error('데이터 로드 실패:', error);
      toast.error('데이터를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOptimize = async () => {
    if (orders.length === 0) {
      toast.error('최적화할 주문이 없습니다.');
      return;
    }

    setIsOptimizing(true);
    setIsConfirmed(false);
    try {
      toast.success('배차 최적화를 시작합니다...');
      
      // 실제 주문 데이터를 사용하여 Mock 결과 생성
      setTimeout(() => {
        // 주문을 차량에 배정 (간단한 알고리즘)
        const vehicleAssignments: VehicleAssignment[] = [];
        const ordersPerVehicle = Math.ceil(orders.length / Math.min(vehicles.length, 3));
        
        for (let i = 0; i < Math.min(vehicles.length, 3); i++) {
          const startIdx = i * ordersPerVehicle;
          const endIdx = Math.min(startIdx + ordersPerVehicle, orders.length);
          const assignedOrders = orders.slice(startIdx, endIdx);
          
          if (assignedOrders.length === 0) break;
          
          const totalPallets = assignedOrders.reduce((sum, order) => sum + (order.pallet_count || 0), 0);
          const vehicle = vehicles[i];
          
          vehicleAssignments.push({
            vehicle,
            orders: assignedOrders.map(order => ({
              order_number: order.order_number,
              pickup_address: order.pickup_address || order.pickup_location || order.pickup_client_name || '상차지 미정',
              delivery_address: order.delivery_address || order.delivery_location || order.delivery_client_name || '하차지 미정',
              pallet_count: order.pallet_count || 0,
              temperature_zone: order.temperature_zone || '상온',
              distance_km: 50 + Math.random() * 100, // Mock distance
              estimated_time: 60 + Math.random() * 120, // Mock time
            })),
            total_pallets: totalPallets,
            utilization_percentage: Math.round((totalPallets / vehicle.max_pallets) * 100),
            route_distance_km: 100 + Math.random() * 200,
            estimated_time_minutes: 180 + Math.random() * 180,
            dispatch_id: 1000 + i,
            confirmed: false,
          });
        }
        
        const totalPallets = orders.reduce((sum, order) => sum + (order.pallet_count || 0), 0);
        const totalDistance = vehicleAssignments.reduce((sum, va) => sum + va.route_distance_km, 0);
        const totalTime = vehicleAssignments.reduce((sum, va) => sum + va.estimated_time_minutes, 0);
        
        const mockResult: OptimizationResult = {
          total_vehicles_used: vehicleAssignments.length,
          total_pallets: totalPallets,
          total_distance_km: Math.round(totalDistance),
          estimated_total_time_minutes: Math.round(totalTime),
          dispatch_ids: orders.map(order => order.id),
          vehicle_assignments: vehicleAssignments,
        };
        
        setOptimizationResult(mockResult);
        toast.success('배차 최적화가 완료되었습니다!');
        setIsOptimizing(false);
      }, 2000);
    } catch (error) {
      console.error('최적화 실패:', error);
      toast.error('배차 최적화에 실패했습니다.');
      setIsOptimizing(false);
    }
  };

  const handleConfirmVehicle = async (vehicleId: number, dispatchId: number) => {
    setConfirmingVehicleId(vehicleId);
    try {
      // TODO: 실제 API 호출
      // await apiClient.confirmDispatch(dispatchId);
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 해당 차량의 confirmed 상태 업데이트
      if (optimizationResult) {
        const updatedAssignments = optimizationResult.vehicle_assignments.map(assignment => 
          assignment.vehicle.id === vehicleId 
            ? { ...assignment, confirmed: true }
            : assignment
        );
        setOptimizationResult({
          ...optimizationResult,
          vehicle_assignments: updatedAssignments,
        });
      }
      
      toast.success(`차량 ${vehicleId}번 배차가 확정되었습니다!`);
    } catch (error) {
      console.error('배차 확정 실패:', error);
      toast.error('배차 확정에 실패했습니다.');
    } finally {
      setConfirmingVehicleId(null);
    }
  };

  const handleConfirm = async () => {
    if (!optimizationResult?.dispatch_ids || optimizationResult.dispatch_ids.length === 0) {
      toast.error('확정할 배차 정보가 없습니다.');
      return;
    }

    setIsConfirming(true);
    try {
      // TODO: 실제 배차 확정 API 호출
      // await apiClient.confirmDispatches(optimizationResult.dispatch_ids);
      
      // 시뮬레이션 (실제로는 위 API 호출)
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setIsConfirmed(true);
      toast.success(`${optimizationResult.dispatch_ids.length}건의 배차가 확정되었습니다!`);
      
      // 3초 후 배차 관리 페이지로 이동
      setTimeout(() => {
        window.location.href = '/dispatches';
      }, 3000);
    } catch (error) {
      console.error('배차 확정 실패:', error);
      toast.error('배차 확정에 실패했습니다.');
    } finally {
      setIsConfirming(false);
    }
  };

  return (
    <Layout>
      <div className="p-4 sm:p-6">
        {/* 헤더 */}
        <div className="mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 flex items-center gap-2">
                <Truck className="w-7 h-7 sm:w-8 sm:h-8" />
                실시간 배차 최적화
              </h1>
              <p className="text-sm sm:text-base text-gray-600 mt-1">
                AI 기반 최적 경로 추천 및 차량 배정 {orders.length > 0 && `(${orders.length}건 대기)`}
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={loadData}
                disabled={isLoading || isOptimizing || isConfirming}
                variant="secondary"
                className="text-sm sm:text-base"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin mr-2" />
                ) : (
                  <RefreshCw className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                )}
                새로고침
              </Button>
              <Button
                onClick={handleOptimize}
                disabled={isLoading || isOptimizing || isConfirming || vehicles.length === 0}
                variant="secondary"
                className="text-sm sm:text-base"
              >
                {isOptimizing ? (
                  <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin mr-2" />
                ) : (
                  <Navigation className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                )}
                최적화 실행
              </Button>
              {optimizationResult && (
                <Button
                  onClick={handleConfirm}
                  disabled={isConfirming || isConfirmed}
                  className="text-sm sm:text-base bg-green-600 hover:bg-green-700"
                >
                  {isConfirming ? (
                    <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin mr-2" />
                  ) : isConfirmed ? (
                    <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                  ) : (
                    <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                  )}
                  {isConfirmed ? '확정 완료' : '배차 확정'}
                </Button>
              )}
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="flex justify-center items-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : (
          <>
            {/* 대기 중인 주문 정보 */}
            {orders.length > 0 && !optimizationResult && (
              <Card className="p-4 sm:p-6 mb-6 bg-blue-50 border-blue-200">
                <div className="flex items-start gap-3">
                  <Package className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-blue-900 mb-2">배차 대기 주문</h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2 text-sm">
                      <div>
                        <span className="text-blue-700">총 주문:</span>
                        <span className="font-semibold text-blue-900 ml-2">{orders.length}건</span>
                      </div>
                      <div>
                        <span className="text-blue-700">총 팔레트:</span>
                        <span className="font-semibold text-blue-900 ml-2">
                          {orders.reduce((sum, o) => sum + (o.pallet_count || 0), 0)}개
                        </span>
                      </div>
                      <div>
                        <span className="text-blue-700">사용 가능 차량:</span>
                        <span className="font-semibold text-blue-900 ml-2">{vehicles.length}대</span>
                      </div>
                      <div>
                        <span className="text-blue-700">예상 소요 차량:</span>
                        <span className="font-semibold text-blue-900 ml-2">
                          {Math.min(Math.ceil(orders.reduce((sum, o) => sum + (o.pallet_count || 0), 0) / 30), vehicles.length)}대
                        </span>
                      </div>
                    </div>
                    <div className="mt-3 pt-3 border-t border-blue-200">
                      <p className="text-xs text-blue-700">
                        💡 "최적화 실행" 버튼을 클릭하여 AI 기반 배차를 시작하세요.
                      </p>
                    </div>
                  </div>
                </div>
              </Card>
            )}

            {/* 확정 완료 알림 */}
            {isConfirmed && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                  <div>
                    <h3 className="font-semibold text-green-900">배차가 확정되었습니다!</h3>
                    <p className="text-sm text-green-700 mt-1">
                      곧 배차 관리 페이지로 이동합니다...
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* 통계 카드 */}
            {optimizationResult && (
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-6">
                <Card className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs sm:text-sm text-gray-600">사용 차량</p>
                      <p className="text-xl sm:text-2xl font-bold text-gray-900 mt-1">
                        {optimizationResult.total_vehicles_used}대
                      </p>
                    </div>
                    <Truck className="w-8 h-8 text-blue-500" />
                  </div>
                </Card>

                <Card className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs sm:text-sm text-gray-600">총 팔레트</p>
                      <p className="text-xl sm:text-2xl font-bold text-gray-900 mt-1">
                        {optimizationResult.total_pallets}개
                      </p>
                    </div>
                    <Package className="w-8 h-8 text-green-500" />
                  </div>
                </Card>

                <Card className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs sm:text-sm text-gray-600">총 거리</p>
                      <p className="text-xl sm:text-2xl font-bold text-gray-900 mt-1">
                        {optimizationResult.total_distance_km}km
                      </p>
                    </div>
                    <MapPin className="w-8 h-8 text-purple-500" />
                  </div>
                </Card>

                <Card className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs sm:text-sm text-gray-600">예상 시간</p>
                      <p className="text-xl sm:text-2xl font-bold text-gray-900 mt-1">
                        {Math.floor(optimizationResult.estimated_total_time_minutes / 60)}시간
                      </p>
                    </div>
                    <Clock className="w-8 h-8 text-orange-500" />
                  </div>
                </Card>
              </div>
            )}

            {/* 차량별 배정 현황 */}
            {optimizationResult ? (
              <div className="space-y-4">
                <h2 className="text-lg sm:text-xl font-bold text-gray-900">차량별 배정 현황</h2>
                
                {optimizationResult.vehicle_assignments.map((assignment, index) => (
                  <Card key={assignment.vehicle.id} className="p-4 sm:p-6">
                    {/* 차량 정보 */}
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-4 border-b">
                      <div className="flex items-center gap-3">
                        <div className="bg-blue-100 p-2 sm:p-3 rounded-lg">
                          <Truck className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600" />
                        </div>
                        <div>
                          <h3 className="font-bold text-base sm:text-lg text-gray-900">
                            차량 #{index + 1} - {assignment.vehicle.code}
                          </h3>
                          <p className="text-xs sm:text-sm text-gray-600">
                            {assignment.vehicle.license_plate} | {assignment.vehicle.driver_name || '미배정'}
                          </p>
                          {/* GPS 현재 위치 */}
                          {assignment.vehicle.gps_data?.current_address && (
                            <p className="text-xs text-blue-600 mt-1 flex items-center gap-1">
                              <MapPin className="w-3 h-3" />
                              현재 위치: {assignment.vehicle.gps_data.current_address}
                            </p>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex flex-wrap gap-2">
                        <span className="px-2 sm:px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs sm:text-sm font-medium">
                          적재율 {assignment.utilization_percentage}%
                        </span>
                        <span className="px-2 sm:px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs sm:text-sm font-medium">
                          {assignment.total_pallets}/{assignment.vehicle.max_pallets} 팔레트
                        </span>
                      </div>
                    </div>

                    {/* 경로 정보 */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4 mb-4">
                      <div className="flex items-center gap-2 text-sm">
                        <MapPin className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-600">총 거리:</span>
                        <span className="font-semibold">{assignment.route_distance_km.toFixed(2)}km</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Clock className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-600">예상 시간:</span>
                        <span className="font-semibold">
                          {Math.floor(assignment.estimated_time_minutes / 60)}시간 {assignment.estimated_time_minutes % 60}분
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Package className="w-4 h-4 text-gray-400" />
                        <span className="text-gray-600">배송 건수:</span>
                        <span className="font-semibold">{assignment.orders.length}건</span>
                      </div>
                    </div>
                    <div className="mb-4 p-2 bg-blue-50 rounded text-xs text-blue-700">
                      💡 총 거리: 모든 배송지를 순회하는 최적 경로의 총 주행거리입니다.
                    </div>

                    {/* 주문 목록 */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="text-sm font-semibold text-gray-700">배정된 주문</h4>
                        {assignment.dispatch_id && (
                          <Button
                            size="sm"
                            variant={assignment.confirmed ? "secondary" : "primary"}
                            onClick={() => handleConfirmVehicle(assignment.vehicle.id, assignment.dispatch_id!)}
                            disabled={confirmingVehicleId === assignment.vehicle.id || assignment.confirmed}
                            className={assignment.confirmed ? "bg-green-600" : ""}
                          >
                            {confirmingVehicleId === assignment.vehicle.id ? (
                              <>
                                <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                                확정 중...
                              </>
                            ) : assignment.confirmed ? (
                              <>
                                <CheckCircle className="w-4 h-4 mr-1" />
                                확정 완료
                              </>
                            ) : (
                              <>
                                <CheckCircle className="w-4 h-4 mr-1" />
                                이 차량 배차 확정
                              </>
                            )}
                          </Button>
                        )}
                      </div>
                      <div className="space-y-2">
                        {assignment.orders.map((order, orderIndex) => (
                          <div
                            key={order.order_number}
                            className="flex flex-col sm:flex-row sm:items-center justify-between p-3 bg-gray-50 rounded-lg gap-2"
                          >
                            <div className="flex items-center gap-3">
                              <span className="flex items-center justify-center w-6 h-6 bg-blue-600 text-white rounded-full text-xs font-bold flex-shrink-0">
                                {orderIndex + 1}
                              </span>
                              <div className="min-w-0">
                                <p className="font-medium text-sm sm:text-base text-gray-900 break-words">
                                  {order.order_number}
                                </p>
                                {/* 상차지 → 하차지 */}
                                <div className="space-y-1 mt-1">
                                  {order.pickup_address && (
                                    <p className="text-xs text-gray-600 break-words flex items-start gap-1">
                                      <span className="text-blue-600 font-semibold flex-shrink-0">🔼 상차지:</span>
                                      <span>{order.pickup_address}</span>
                                    </p>
                                  )}
                                  <p className="text-xs text-gray-600 break-words flex items-start gap-1">
                                    <span className="text-green-600 font-semibold flex-shrink-0">🔽 하차지:</span>
                                    <span>{order.delivery_address}</span>
                                  </p>
                                </div>
                              </div>
                            </div>
                            <div className="flex flex-wrap gap-2 sm:ml-auto">
                              <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs whitespace-nowrap">
                                {order.temperature_zone}
                              </span>
                              <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs whitespace-nowrap">
                                {order.pallet_count}팔레트
                              </span>
                              {order.distance_km && (
                                <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs whitespace-nowrap" title="출발지부터 이 배송지까지의 거리">
                                  📍 {order.distance_km.toFixed(1)}km
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : orders.length === 0 ? (
              <Card className="p-8 sm:p-12 text-center">
                <AlertCircle className="w-12 h-12 sm:w-16 sm:h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2">
                  배차할 주문이 없습니다
                </h3>
                <p className="text-sm sm:text-base text-gray-600 mb-4">
                  주문 관리 페이지에서 "AI 배차" 버튼을 클릭하여 주문을 선택하세요.
                </p>
                <Button onClick={() => window.location.href = '/orders'}>
                  <Package className="w-5 h-5 mr-2" />
                  주문 관리로 이동
                </Button>
              </Card>
            ) : (
              <Card className="p-8 sm:p-12 text-center">
                <AlertCircle className="w-12 h-12 sm:w-16 sm:h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2">
                  배차 최적화를 실행해주세요
                </h3>
                <p className="text-sm sm:text-base text-gray-600 mb-4">
                  "최적화 실행" 버튼을 클릭하여 AI 기반 배차 추천을 받으세요.
                </p>
                <Button onClick={handleOptimize} disabled={vehicles.length === 0 || orders.length === 0}>
                  <Navigation className="w-5 h-5 mr-2" />
                  최적화 실행
                </Button>
              </Card>
            )}

            {/* 사용 가능한 차량 목록 */}
            {vehicles.length > 0 && (
              <div className="mt-6">
                <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4">
                  사용 가능한 차량 ({vehicles.length}대)
                </h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                  {vehicles.map((vehicle) => (
                    <Card key={vehicle.id} className="p-4">
                      <div className="flex items-center gap-3 mb-3">
                        <Truck className="w-5 h-5 text-blue-600" />
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-gray-900 truncate">{vehicle.code}</p>
                          <p className="text-xs text-gray-600 truncate">{vehicle.license_plate}</p>
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">최대 적재:</span>
                        <span className="font-semibold">{vehicle.max_pallets} 팔레트</span>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  );
};

export default OptimizationPage;
