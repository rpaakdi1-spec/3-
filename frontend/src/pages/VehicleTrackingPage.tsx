/**
 * Phase 12: 실시간 차량 추적 페이지
 * 네이버 맵 + WebSocket 실시간 업데이트
 */
import React, { useState, useEffect } from 'react';
import { MapPin, Truck, RefreshCw, Zap } from 'lucide-react';
import NaverMap from '../components/map/NaverMap';
import { wsClient } from '../services/websocket';
import api from '../services/api';

interface VehicleLocation {
  vehicle_id: number;
  license_plate: string;
  driver_name?: string;
  driver_phone?: string;
  latitude: number;
  longitude: number;
  status: string;
  vehicle_type?: string;
  temperature_type?: string;
  last_updated?: string;
}

const VehicleTrackingPage: React.FC = () => {
  const [vehicles, setVehicles] = useState<VehicleLocation[]>([]);
  const [selectedVehicle, setSelectedVehicle] = useState<VehicleLocation | null>(null);
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [filter, setFilter] = useState<string>('all');

  // 초기 차량 위치 로드
  useEffect(() => {
    loadVehicles();
  }, []);

  // WebSocket 연결
  useEffect(() => {
    const connect = async () => {
      try {
        await wsClient.connect('vehicle-tracking');
        setWsConnected(true);

        // 차량 위치 업데이트 수신
        wsClient.on('vehicle_positions', (data: any) => {
          console.log('📡 Vehicle positions update:', data);
          if (data.vehicles && Array.isArray(data.vehicles)) {
            setVehicles(prevVehicles => {
              const updatedVehicles = [...prevVehicles];
              
              data.vehicles.forEach((update: any) => {
                const index = updatedVehicles.findIndex(
                  v => v.vehicle_id === update.vehicle_id
                );
                
                if (index >= 0) {
                  updatedVehicles[index] = {
                    ...updatedVehicles[index],
                    ...update,
                  };
                } else {
                  updatedVehicles.push(update);
                }
              });
              
              return updatedVehicles;
            });
          }
        });

        // 배차 업데이트 수신
        wsClient.on('dispatch_update', (data: any) => {
          console.log('📢 Dispatch update:', data);
          // 배차된 차량 상태 업데이트
          if (data.data && data.data.vehicle) {
            setVehicles(prevVehicles =>
              prevVehicles.map(v =>
                v.vehicle_id === data.data.vehicle.id
                  ? { ...v, status: 'busy' }
                  : v
              )
            );
          }
        });
      } catch (error) {
        console.error('WebSocket connection failed:', error);
        setWsConnected(false);
      }
    };

    connect();

    return () => {
      wsClient.disconnect();
    };
  }, []);

  const loadVehicles = async () => {
    try {
      setLoading(true);
      const response = await api.get('/vehicles/map');
      setVehicles(response.data.vehicles || []);
    } catch (error) {
      console.error('Failed to load vehicles:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVehicleClick = (vehicle: VehicleLocation) => {
    setSelectedVehicle(vehicle);
  };

  const handleRefresh = () => {
    loadVehicles();
  };

  // 필터링된 차량
  const filteredVehicles = vehicles.filter(v => {
    if (filter === 'all') return true;
    return v.status === filter;
  });

  // 통계
  const stats = {
    total: vehicles.length,
    available: vehicles.filter(v => v.status === 'available').length,
    busy: vehicles.filter(v => v.status === 'busy').length,
    offline: vehicles.filter(v => v.status === 'offline').length,
  };

  return (
    <div className="p-6 space-y-6">
      {/* 헤더 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <MapPin className="w-7 h-7" />
            실시간 차량 추적
          </h1>
          <p className="text-gray-600 mt-1">
            모든 차량의 실시간 위치를 확인하세요
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* WebSocket 상태 */}
          <div
            className={`flex items-center gap-2 px-3 py-2 rounded-lg ${
              wsConnected
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            <Zap className={`w-4 h-4 ${wsConnected ? 'animate-pulse' : ''}`} />
            <span className="text-sm font-medium">
              {wsConnected ? '실시간 연결' : '연결 끊김'}
            </span>
          </div>

          {/* 새로고침 */}
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            새로고침
          </button>
        </div>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div
          className={`p-4 rounded-lg cursor-pointer transition-all ${
            filter === 'all'
              ? 'bg-blue-500 text-white shadow-lg'
              : 'bg-white border hover:shadow-md'
          }`}
          onClick={() => setFilter('all')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className={filter === 'all' ? 'text-blue-100' : 'text-gray-600'}>
                전체 차량
              </p>
              <p className="text-2xl font-bold mt-1">{stats.total}대</p>
            </div>
            <Truck className="w-8 h-8 opacity-50" />
          </div>
        </div>

        <div
          className={`p-4 rounded-lg cursor-pointer transition-all ${
            filter === 'available'
              ? 'bg-green-500 text-white shadow-lg'
              : 'bg-white border hover:shadow-md'
          }`}
          onClick={() => setFilter('available')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p
                className={
                  filter === 'available' ? 'text-green-100' : 'text-gray-600'
                }
              >
                가용 차량
              </p>
              <p className="text-2xl font-bold mt-1">{stats.available}대</p>
            </div>
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
          </div>
        </div>

        <div
          className={`p-4 rounded-lg cursor-pointer transition-all ${
            filter === 'busy'
              ? 'bg-amber-500 text-white shadow-lg'
              : 'bg-white border hover:shadow-md'
          }`}
          onClick={() => setFilter('busy')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className={filter === 'busy' ? 'text-amber-100' : 'text-gray-600'}>
                운행 중
              </p>
              <p className="text-2xl font-bold mt-1">{stats.busy}대</p>
            </div>
            <div className="w-4 h-4 rounded-full bg-amber-500"></div>
          </div>
        </div>

        <div
          className={`p-4 rounded-lg cursor-pointer transition-all ${
            filter === 'offline'
              ? 'bg-gray-500 text-white shadow-lg'
              : 'bg-white border hover:shadow-md'
          }`}
          onClick={() => setFilter('offline')}
        >
          <div className="flex items-center justify-between">
            <div>
              <p
                className={filter === 'offline' ? 'text-gray-100' : 'text-gray-600'}
              >
                오프라인
              </p>
              <p className="text-2xl font-bold mt-1">{stats.offline}대</p>
            </div>
            <div className="w-4 h-4 rounded-full bg-gray-500"></div>
          </div>
        </div>
      </div>

      {/* 지도 & 차량 목록 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 지도 */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <NaverMap
              vehicles={filteredVehicles}
              onVehicleClick={handleVehicleClick}
              height="700px"
            />
          </div>
        </div>

        {/* 차량 목록 */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-md p-4">
            <h2 className="text-lg font-bold mb-4">
              차량 목록 ({filteredVehicles.length})
            </h2>
            <div className="space-y-2 max-h-[700px] overflow-y-auto">
              {filteredVehicles.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Truck className="w-12 h-12 mx-auto mb-2 opacity-30" />
                  <p>표시할 차량이 없습니다</p>
                </div>
              ) : (
                filteredVehicles.map(vehicle => (
                  <div
                    key={vehicle.vehicle_id}
                    className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                      selectedVehicle?.vehicle_id === vehicle.vehicle_id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                    onClick={() => setSelectedVehicle(vehicle)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-bold">{vehicle.license_plate}</span>
                          <span
                            className={`px-2 py-0.5 rounded text-xs ${
                              vehicle.status === 'available'
                                ? 'bg-green-100 text-green-700'
                                : vehicle.status === 'busy'
                                ? 'bg-amber-100 text-amber-700'
                                : 'bg-gray-100 text-gray-700'
                            }`}
                          >
                            {vehicle.status === 'available'
                              ? '가용'
                              : vehicle.status === 'busy'
                              ? '운행중'
                              : '오프라인'}
                          </span>
                        </div>
                        {vehicle.driver_name && (
                          <p className="text-sm text-gray-600 mt-1">
                            {vehicle.driver_name}
                          </p>
                        )}
                        {vehicle.vehicle_type && (
                          <p className="text-xs text-gray-500 mt-1">
                            {vehicle.vehicle_type}
                            {vehicle.temperature_type &&
                              ` • ${vehicle.temperature_type}`}
                          </p>
                        )}
                      </div>
                      <MapPin className="w-5 h-5 text-gray-400" />
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* 선택된 차량 상세 */}
          {selectedVehicle && (
            <div className="bg-white rounded-lg shadow-md p-4 mt-4">
              <h3 className="font-bold mb-3">차량 상세 정보</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">차량번호:</span>
                  <span className="font-medium">{selectedVehicle.license_plate}</span>
                </div>
                {selectedVehicle.driver_name && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">기사명:</span>
                    <span className="font-medium">{selectedVehicle.driver_name}</span>
                  </div>
                )}
                {selectedVehicle.driver_phone && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">연락처:</span>
                    <span className="font-medium">{selectedVehicle.driver_phone}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-gray-600">상태:</span>
                  <span
                    className={`font-medium ${
                      selectedVehicle.status === 'available'
                        ? 'text-green-600'
                        : selectedVehicle.status === 'busy'
                        ? 'text-amber-600'
                        : 'text-gray-600'
                    }`}
                  >
                    {selectedVehicle.status === 'available'
                      ? '가용'
                      : selectedVehicle.status === 'busy'
                      ? '운행중'
                      : '오프라인'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">위치:</span>
                  <span className="font-medium text-xs">
                    {selectedVehicle.latitude.toFixed(4)}, {selectedVehicle.longitude.toFixed(4)}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VehicleTrackingPage;
