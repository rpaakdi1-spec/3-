import React, { useState, useEffect } from 'react';
import { Truck, MapPin, Package, Clock, AlertCircle, RefreshCw, Navigation, Loader2 } from 'lucide-react';
import Layout from '../components/common/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { toast } from 'react-hot-toast';
import apiClient from '../api/client';

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
}

interface AssignedOrder {
  order_number: string;
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
}

interface VehicleAssignment {
  vehicle: Vehicle;
  orders: AssignedOrder[];
  total_pallets: number;
  utilization_percentage: number;
  route_distance_km: number;
  estimated_time_minutes: number;
}

const OptimizationPage: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      // 차량 목록 조회 (모든 차량)
      const vehiclesData = await apiClient.getVehicles();
      // 운행가능한 차량만 필터링
      const availableVehicles = (vehiclesData.items || vehiclesData || []).filter(
        (v: Vehicle) => v.status === '운행가능'
      );
      setVehicles(availableVehicles);
    } catch (error) {
      console.error('데이터 로드 실패:', error);
      toast.error('데이터를 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleOptimize = async () => {
    setIsOptimizing(true);
    try {
      // TODO: 실제 최적화 API 호출
      toast.success('배차 최적화를 시작합니다...');
      
      // 시뮬레이션 데이터 (실제로는 백엔드 API 호출)
      setTimeout(() => {
        const mockResult: OptimizationResult = {
          total_vehicles_used: 3,
          total_pallets: 125,
          total_distance_km: 350,
          estimated_total_time_minutes: 480,
          vehicle_assignments: vehicles.slice(0, 3).map((vehicle, index) => ({
            vehicle,
            orders: [
              {
                order_number: `ORD-${1000 + index * 4}`,
                delivery_address: '부산 해운대구',
                pallet_count: 10,
                temperature_zone: '냉동',
                distance_km: 120,
                estimated_time: 180,
              },
              {
                order_number: `ORD-${1001 + index * 4}`,
                delivery_address: '대구 수성구',
                pallet_count: 15,
                temperature_zone: '냉동',
                distance_km: 90,
                estimated_time: 150,
              },
            ],
            total_pallets: 25 + index * 10,
            utilization_percentage: 75 + index * 5,
            route_distance_km: 210 + index * 50,
            estimated_time_minutes: 330 + index * 60,
          })),
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
                AI 기반 최적 경로 추천 및 차량 배정
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={loadData}
                disabled={isLoading || isOptimizing}
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
                disabled={isLoading || isOptimizing || vehicles.length === 0}
                className="text-sm sm:text-base"
              >
                {isOptimizing ? (
                  <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 animate-spin mr-2" />
                ) : (
                  <Navigation className="w-4 h-4 sm:w-5 sm:h-5 mr-2" />
                )}
                최적화 실행
              </Button>
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="flex justify-center items-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : (
          <>
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
                        <span className="font-semibold">{assignment.route_distance_km}km</span>
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

                    {/* 주문 목록 */}
                    <div className="space-y-2">
                      <h4 className="text-sm font-semibold text-gray-700">배정된 주문</h4>
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
                                <p className="text-xs sm:text-sm text-gray-600 break-words">
                                  {order.delivery_address}
                                </p>
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
                                <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs whitespace-nowrap">
                                  {order.distance_km}km
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
            ) : (
              <Card className="p-8 sm:p-12 text-center">
                <AlertCircle className="w-12 h-12 sm:w-16 sm:h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg sm:text-xl font-semibold text-gray-900 mb-2">
                  배차 최적화를 실행해주세요
                </h3>
                <p className="text-sm sm:text-base text-gray-600 mb-4">
                  "최적화 실행" 버튼을 클릭하여 AI 기반 배차 추천을 받으세요.
                </p>
                <Button onClick={handleOptimize} disabled={vehicles.length === 0}>
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
