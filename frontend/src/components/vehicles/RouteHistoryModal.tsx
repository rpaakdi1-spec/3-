import React, { useEffect, useState } from 'react';
import { X, Play, Pause, RotateCcw, MapPin, Navigation } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface RoutePoint {
  lat: number;
  lng: number;
  timestamp: string;
  speed: number;
  engine_status: number;
  recorded_at: string | null;
}

interface Stop {
  lat: number;
  lng: number;
  timestamp: string;
  type: string;
  duration_minutes: number | null;
}

interface RouteData {
  vehicle_id: number;
  vehicle_plate: string;
  vehicle_type: string;
  hours: number;
  route_points: RoutePoint[];
  stops: Stop[];
  total_points: number;
  total_distance_km: number;
  max_speed_kmh: number;
  avg_speed_kmh: number;
  start_time: string | null;
  end_time: string | null;
}

interface RouteHistoryModalProps {
  vehicleId: number;
  vehiclePlate: string;
  isOpen: boolean;
  onClose: () => void;
}

const RouteHistoryModal: React.FC<RouteHistoryModalProps> = ({
  vehicleId,
  vehiclePlate,
  isOpen,
  onClose,
}) => {
  const [data, setData] = useState<RouteData | null>(null);
  const [loading, setLoading] = useState(true);
  const [hours, setHours] = useState(24);
  const [map, setMap] = useState<any>(null);
  const [polyline, setPolyline] = useState<any>(null);
  const [markers, setMarkers] = useState<any[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  const fetchData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/v1/vehicles/${vehicleId}/gps/history?hours=${hours}`);
      if (!response.ok) {
        throw new Error('Failed to fetch GPS history');
      }
      const result = await response.json();
      setData(result);
      setLoading(false);
      
      // 지도에 경로 그리기
      if (result.route_points.length > 0) {
        drawRoute(result);
      }
    } catch (error) {
      console.error('Failed to fetch GPS history:', error);
      toast.error('GPS 이력 조회에 실패했습니다');
      setLoading(false);
    }
  };

  const drawRoute = (routeData: RouteData) => {
    if (!map || routeData.route_points.length === 0) return;

    // 기존 polyline 및 마커 제거
    if (polyline) {
      polyline.setMap(null);
    }
    markers.forEach((marker) => marker.setMap(null));
    setMarkers([]);

    // Naver Maps Polyline 생성
    const path = routeData.route_points.map((point) => new window.naver.maps.LatLng(point.lat, point.lng));

    const newPolyline = new window.naver.maps.Polyline({
      map: map,
      path: path,
      strokeColor: '#3B82F6',
      strokeWeight: 4,
      strokeOpacity: 0.8,
    });

    setPolyline(newPolyline);

    // 시작 마커
    const startMarker = new window.naver.maps.Marker({
      map: map,
      position: new window.naver.maps.LatLng(routeData.route_points[0].lat, routeData.route_points[0].lng),
      icon: {
        content: '<div style="background: #10B981; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">시작</div>',
        anchor: new window.naver.maps.Point(20, 20),
      },
    });

    // 종료 마커
    const lastPoint = routeData.route_points[routeData.route_points.length - 1];
    const endMarker = new window.naver.maps.Marker({
      map: map,
      position: new window.naver.maps.LatLng(lastPoint.lat, lastPoint.lng),
      icon: {
        content: '<div style="background: #EF4444; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;">종료</div>',
        anchor: new window.naver.maps.Point(20, 20),
      },
    });

    // 정차 마커
    const stopMarkers = routeData.stops.map((stop) => {
      return new window.naver.maps.Marker({
        map: map,
        position: new window.naver.maps.LatLng(stop.lat, stop.lng),
        icon: {
          content: '<div style="background: #F59E0B; color: white; padding: 4px 8px; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">P</div>',
          anchor: new window.naver.maps.Point(12, 12),
        },
      });
    });

    setMarkers([startMarker, endMarker, ...stopMarkers]);

    // 지도 중심 및 줌 조정
    const bounds = new window.naver.maps.LatLngBounds(
      new window.naver.maps.LatLng(routeData.route_points[0].lat, routeData.route_points[0].lng),
      new window.naver.maps.LatLng(lastPoint.lat, lastPoint.lng)
    );
    routeData.route_points.forEach((point) => {
      bounds.extend(new window.naver.maps.LatLng(point.lat, point.lng));
    });
    map.fitBounds(bounds);
  };

  useEffect(() => {
    if (!isOpen) return;

    fetchData();

    // Naver Maps 초기화
    if (!map && window.naver && window.naver.maps) {
      const mapDiv = document.getElementById('route-history-map');
      if (mapDiv) {
        const newMap = new window.naver.maps.Map(mapDiv, {
          center: new window.naver.maps.LatLng(35.8, 127.5),
          zoom: 7,
        });
        setMap(newMap);
      }
    }
  }, [isOpen, vehicleId, hours]);

  useEffect(() => {
    // 경로 재생 로직
    if (!isPlaying || !data || currentIndex >= data.route_points.length) {
      setIsPlaying(false);
      return;
    }

    const timer = setTimeout(() => {
      setCurrentIndex(currentIndex + 1);
    }, 500); // 0.5초마다 포인트 이동

    return () => clearTimeout(timer);
  }, [isPlaying, currentIndex, data]);

  if (!isOpen) return null;

  const getSpeedColor = (speed: number) => {
    if (speed === 0) return '#6B7280'; // Gray
    if (speed < 30) return '#10B981'; // Green
    if (speed < 60) return '#3B82F6'; // Blue
    if (speed < 90) return '#F59E0B'; // Orange
    return '#EF4444'; // Red
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-7xl w-full h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">경로 이력</h2>
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
            </select>

            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X size={24} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 flex overflow-hidden">
          {/* Map */}
          <div className="flex-1 relative">
            {loading ? (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
                <div className="animate-pulse text-gray-400">지도 로딩 중...</div>
              </div>
            ) : (
              <div id="route-history-map" className="w-full h-full"></div>
            )}
          </div>

          {/* Stats Panel */}
          <div className="w-80 bg-gray-50 p-4 overflow-y-auto border-l">
            {data && (
              <div className="space-y-4">
                {/* 통계 */}
                <div className="bg-white rounded-lg p-4 space-y-3">
                  <h3 className="font-semibold text-gray-900">주행 통계</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">총 거리</span>
                      <span className="font-semibold">{data.total_distance_km} km</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">평균 속도</span>
                      <span className="font-semibold">{data.avg_speed_kmh} km/h</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">최고 속도</span>
                      <span className="font-semibold">{data.max_speed_kmh} km/h</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">데이터 포인트</span>
                      <span className="font-semibold">{data.total_points}개</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">정차 지점</span>
                      <span className="font-semibold">{data.stops.length}개</span>
                    </div>
                  </div>
                </div>

                {/* 범례 */}
                <div className="bg-white rounded-lg p-4 space-y-2">
                  <h3 className="font-semibold text-gray-900 mb-2">범례</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-green-500 rounded"></div>
                      <span>시작 지점</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-red-500 rounded"></div>
                      <span>종료 지점</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-orange-500 rounded-full"></div>
                      <span>정차 지점</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-1 bg-blue-500"></div>
                      <span>이동 경로</span>
                    </div>
                  </div>
                </div>

                {/* 속도 범례 */}
                <div className="bg-white rounded-lg p-4 space-y-2">
                  <h3 className="font-semibold text-gray-900 mb-2">속도 범위</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-gray-500 rounded"></div>
                      <span>정차 (0 km/h)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-green-500 rounded"></div>
                      <span>저속 (&lt;30 km/h)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-blue-500 rounded"></div>
                      <span>중속 (30-60 km/h)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-orange-500 rounded"></div>
                      <span>고속 (60-90 km/h)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-red-500 rounded"></div>
                      <span>과속 (&gt;90 km/h)</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RouteHistoryModal;
