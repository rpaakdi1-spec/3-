/**
 * Phase 12: 네이버 맵 컴포넌트
 * 차량 실시간 위치, 경로 표시, 클러스터링
 */
import React, { useEffect, useRef, useState } from 'react';
import { Loader2 } from 'lucide-react';

interface VehicleMarker {
  vehicle_id: number;
  license_plate: string;
  driver_name?: string;
  latitude: number;
  longitude: number;
  status: string;
  vehicle_type?: string;
  temperature_type?: string;
}

interface RouteData {
  distance_km: number;
  duration_min: number;
  route?: Array<[number, number]>;
}

interface NaverMapProps {
  vehicles?: VehicleMarker[];
  routes?: RouteData[];
  center?: { lat: number; lng: number };
  zoom?: number;
  onVehicleClick?: (vehicle: VehicleMarker) => void;
  height?: string;
}

declare global {
  interface Window {
    naver: any;
  }
}

const NaverMap: React.FC<NaverMapProps> = ({
  vehicles = [],
  routes = [],
  center = { lat: 37.5665, lng: 126.9780 }, // 서울 시청
  zoom = 12,
  onVehicleClick,
  height = '600px',
}) => {
  const mapRef = useRef<HTMLDivElement>(null);
  const [map, setMap] = useState<any>(null);
  const [markers, setMarkers] = useState<any[]>([]);
  const [polylines, setPolylines] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 네이버 맵 API 로드
  useEffect(() => {
    const loadNaverMap = () => {
      if (window.naver && window.naver.maps) {
        setLoading(false);
        return;
      }

      const script = document.createElement('script');
      script.src = `https://openapi.map.naver.com/openapi/v3/maps.js?ncpClientId=${
        import.meta.env.VITE_NAVER_MAP_CLIENT_ID || 'oimsa0yj4k'
      }`;
      script.async = true;
      script.onload = () => setLoading(false);
      script.onerror = () => {
        setError('네이버 맵을 로드할 수 없습니다');
        setLoading(false);
      };
      document.head.appendChild(script);
    };

    loadNaverMap();
  }, []);

  // 맵 초기화
  useEffect(() => {
    if (!loading && !error && mapRef.current && window.naver && !map) {
      const mapOptions = {
        center: new window.naver.maps.LatLng(center.lat, center.lng),
        zoom: zoom,
        mapTypeControl: true,
        mapTypeControlOptions: {
          style: window.naver.maps.MapTypeControlStyle.BUTTON,
          position: window.naver.maps.Position.TOP_RIGHT,
        },
        zoomControl: true,
        zoomControlOptions: {
          style: window.naver.maps.ZoomControlStyle.SMALL,
          position: window.naver.maps.Position.TOP_RIGHT,
        },
      };

      const newMap = new window.naver.maps.Map(mapRef.current, mapOptions);
      setMap(newMap);
    }
  }, [loading, error, map, center, zoom]);

  // 차량 마커 업데이트
  useEffect(() => {
    if (!map || !window.naver) return;

    // 기존 마커 제거
    markers.forEach(marker => marker.setMap(null));

    // 새 마커 생성
    const newMarkers = vehicles.map(vehicle => {
      const position = new window.naver.maps.LatLng(
        vehicle.latitude,
        vehicle.longitude
      );

      // 상태별 마커 색상
      const getMarkerColor = (status: string) => {
        switch (status) {
          case 'available':
            return '#10b981'; // green
          case 'busy':
            return '#f59e0b'; // amber
          case 'offline':
            return '#6b7280'; // gray
          default:
            return '#3b82f6'; // blue
        }
      };

      // 커스텀 마커 HTML
      const markerContent = `
        <div style="
          position: relative;
          width: 40px;
          height: 40px;
          cursor: pointer;
        ">
          <div style="
            width: 40px;
            height: 40px;
            background: ${getMarkerColor(vehicle.status)};
            border: 3px solid white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            font-size: 20px;
          ">
            🚚
          </div>
          <div style="
            position: absolute;
            bottom: -20px;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: bold;
            white-space: nowrap;
            box-shadow: 0 1px 4px rgba(0,0,0,0.2);
          ">
            ${vehicle.license_plate}
          </div>
        </div>
      `;

      const marker = new window.naver.maps.Marker({
        position: position,
        map: map,
        icon: {
          content: markerContent,
          size: new window.naver.maps.Size(40, 40),
          anchor: new window.naver.maps.Point(20, 20),
        },
      });

      // 정보창
      const infoWindow = new window.naver.maps.InfoWindow({
        content: `
          <div style="padding: 10px; min-width: 200px;">
            <h3 style="margin: 0 0 8px 0; font-size: 14px; font-weight: bold;">
              ${vehicle.license_plate}
            </h3>
            ${vehicle.driver_name ? `<p style="margin: 4px 0;">기사: ${vehicle.driver_name}</p>` : ''}
            <p style="margin: 4px 0;">상태: <span style="
              color: ${getMarkerColor(vehicle.status)};
              font-weight: bold;
            ">${vehicle.status === 'available' ? '가용' : vehicle.status === 'busy' ? '운행중' : '오프라인'}</span></p>
            ${vehicle.vehicle_type ? `<p style="margin: 4px 0;">차량: ${vehicle.vehicle_type}</p>` : ''}
            ${vehicle.temperature_type ? `<p style="margin: 4px 0;">온도: ${vehicle.temperature_type}</p>` : ''}
          </div>
        `,
      });

      // 클릭 이벤트
      window.naver.maps.Event.addListener(marker, 'click', () => {
        if (onVehicleClick) {
          onVehicleClick(vehicle);
        }
        infoWindow.open(map, marker);
      });

      return marker;
    });

    setMarkers(newMarkers);

    // 차량이 있으면 모든 차량이 보이도록 경계 조정
    if (vehicles.length > 0) {
      const bounds = new window.naver.maps.LatLngBounds();
      vehicles.forEach(vehicle => {
        bounds.extend(
          new window.naver.maps.LatLng(vehicle.latitude, vehicle.longitude)
        );
      });
      map.fitBounds(bounds, { top: 50, right: 50, bottom: 50, left: 50 });
    }
  }, [map, vehicles, onVehicleClick]);

  // 경로 표시
  useEffect(() => {
    if (!map || !window.naver) return;

    // 기존 경로 제거
    polylines.forEach(polyline => polyline.setMap(null));

    // 새 경로 생성
    const newPolylines = routes
      .filter(route => route.route && route.route.length > 0)
      .map(route => {
        const path = route.route!.map(
          ([lat, lng]) => new window.naver.maps.LatLng(lat, lng)
        );

        return new window.naver.maps.Polyline({
          map: map,
          path: path,
          strokeColor: '#3b82f6',
          strokeWeight: 5,
          strokeOpacity: 0.8,
          strokeStyle: 'solid',
        });
      });

    setPolylines(newPolylines);
  }, [map, routes]);

  if (loading) {
    return (
      <div
        className="flex items-center justify-center bg-gray-100 rounded-lg"
        style={{ height }}
      >
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-2 text-blue-500" />
          <p className="text-sm text-gray-600">지도 로딩중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="flex items-center justify-center bg-red-50 rounded-lg border border-red-200"
        style={{ height }}
      >
        <div className="text-center text-red-600">
          <p className="font-medium">{error}</p>
          <p className="text-sm mt-2">네이버 맵 API 키를 확인해주세요</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      <div ref={mapRef} style={{ width: '100%', height }} className="rounded-lg" />
      
      {/* 범례 */}
      <div className="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-3 text-sm">
        <div className="font-bold mb-2">차량 상태</div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
          <span>가용</span>
        </div>
        <div className="flex items-center gap-2 mb-1">
          <div className="w-3 h-3 rounded-full bg-amber-500"></div>
          <span>운행중</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-gray-500"></div>
          <span>오프라인</span>
        </div>
      </div>

      {/* 통계 */}
      {vehicles.length > 0 && (
        <div className="absolute top-4 right-4 bg-white rounded-lg shadow-lg p-3 text-sm">
          <div className="font-bold mb-2">차량 현황</div>
          <div className="space-y-1">
            <div>전체: {vehicles.length}대</div>
            <div className="text-green-600">
              가용: {vehicles.filter(v => v.status === 'available').length}대
            </div>
            <div className="text-amber-600">
              운행: {vehicles.filter(v => v.status === 'busy').length}대
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NaverMap;
