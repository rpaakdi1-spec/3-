/**
 * 게스트 배송 페이지
 * 
 * 회원가입 없이 1회용 링크로 접속하여 배송 작업 수행
 * - 배송 정보 조회
 * - GPS 자동 전송
 * - 서류 업로드 (거래명세표, 온도기록지)
 */

import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { Camera, Upload, Navigation, FileText, Thermometer, CheckCircle, AlertCircle, MapPin } from 'lucide-react';
import 'leaflet/dist/leaflet.css';

interface RouteInfo {
  sequence: number;
  type: string;
  location_name: string;
  address: string;
  latitude: number;
  longitude: number;
  estimated_arrival_time?: string;
  notes?: string;
}

interface DeliveryInfo {
  dispatch_number: string;
  dispatch_date: string;
  vehicle_plate: string | null;
  total_orders: number;
  total_distance_km: number | null;
  planned_start_time: string | null;
  planned_end_time: string | null;
  routes: RouteInfo[];
  status: string;
  is_expired: boolean;
}

export default function GuestDeliveryPage() {
  const { token } = useParams<{ token: string }>();
  const [deliveryInfo, setDeliveryInfo] = useState<DeliveryInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // GPS 상태
  const [gpsEnabled, setGpsEnabled] = useState(false);
  const [currentPosition, setCurrentPosition] = useState<{ lat: number; lon: number } | null>(null);
  const [lastGpsUpdate, setLastGpsUpdate] = useState<string | null>(null);
  const gpsWatchId = useRef<number | null>(null);
  
  // 서류 업로드 상태
  const [uploadedDocs, setUploadedDocs] = useState<{
    departure_transaction: boolean;
    departure_temperature: boolean;
    arrival_transaction: boolean;
    arrival_temperature: boolean;
    signature: boolean;
  }>({
    departure_transaction: false,
    departure_temperature: false,
    arrival_transaction: false,
    arrival_temperature: false,
    signature: false
  });
  
  const [uploading, setUploading] = useState(false);

  // 배송 정보 조회
  useEffect(() => {
    if (!token) return;
    
    const fetchDeliveryInfo = async () => {
      try {
        const response = await fetch(`/api/v1/guest/delivery/${token}`);
        if (!response.ok) {
          throw new Error('Failed to load delivery information');
        }
        const data = await response.json();
        setDeliveryInfo(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchDeliveryInfo();
  }, [token]);

  // GPS 자동 전송 시작
  const startGpsTracking = () => {
    if (!navigator.geolocation) {
      alert('이 브라우저는 GPS를 지원하지 않습니다.');
      return;
    }

    const watchId = navigator.geolocation.watchPosition(
      async (position) => {
        const { latitude, longitude, accuracy } = position.coords;
        setCurrentPosition({ lat: latitude, lon: longitude });
        setLastGpsUpdate(new Date().toLocaleTimeString());

        // 서버에 위치 전송
        try {
          await fetch(`/api/v1/guest/delivery/${token}/location`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              latitude,
              longitude,
              accuracy
            })
          });
        } catch (err) {
          console.error('GPS 전송 실패:', err);
        }
      },
      (error) => {
        console.error('GPS 에러:', error);
        alert('GPS 위치를 가져올 수 없습니다.');
      },
      {
        enableHighAccuracy: true,
        timeout: 30000,
        maximumAge: 0
      }
    );

    gpsWatchId.current = watchId;
    setGpsEnabled(true);
  };

  // GPS 전송 중지
  const stopGpsTracking = () => {
    if (gpsWatchId.current !== null) {
      navigator.geolocation.clearWatch(gpsWatchId.current);
      gpsWatchId.current = null;
    }
    setGpsEnabled(false);
  };

  // 서류 업로드
  const handleFileUpload = async (
    docType: 'transaction_statement' | 'temperature_record' | 'signature',
    stage: 'departure' | 'arrival'
  ) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/*,application/pdf';
    input.capture = 'environment'; // 카메라 우선

    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;

      setUploading(true);
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('document_type', docType === 'transaction_statement' ? '거래명세표' : docType === 'temperature_record' ? '온도기록지' : '서명');
        formData.append('stage', stage === 'departure' ? '출발' : '도착');

        const response = await fetch(`/api/v1/guest/delivery/${token}/documents`, {
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          throw new Error('업로드 실패');
        }

        // 업로드 성공 표시
        const docKey = `${stage}_${docType.split('_')[0]}` as keyof typeof uploadedDocs;
        setUploadedDocs(prev => ({ ...prev, [docKey]: true }));
        alert('업로드 완료!');
      } catch (err) {
        alert('업로드 실패: ' + (err instanceof Error ? err.message : 'Unknown error'));
      } finally {
        setUploading(false);
      }
    };

    input.click();
  };

  // 배송 완료
  const completeDelivery = async () => {
    if (!confirm('배송을 완료하시겠습니까?')) return;

    try {
      const response = await fetch(`/api/v1/guest/delivery/${token}/complete`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error('완료 처리 실패');
      }

      alert('배송이 완료되었습니다!');
      stopGpsTracking();
    } catch (err) {
      alert('완료 처리 실패: ' + (err instanceof Error ? err.message : 'Unknown error'));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">배송 정보 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error || !deliveryInfo) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">접속 오류</h2>
          <p className="text-gray-600 mb-4">{error || '배송 정보를 불러올 수 없습니다.'}</p>
          <p className="text-sm text-gray-500">링크가 만료되었거나 잘못된 링크입니다.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <div className="bg-blue-600 text-white p-4 shadow-lg">
        <div className="container mx-auto">
          <h1 className="text-2xl font-bold flex items-center">
            <MapPin className="mr-2" />
            냉장 배송
          </h1>
          <p className="text-sm opacity-90 mt-1">배차번호: {deliveryInfo.dispatch_number}</p>
        </div>
      </div>

      <div className="container mx-auto p-4 max-w-4xl">
        {/* GPS 상태 카드 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <Navigation className={`h-6 w-6 mr-3 ${gpsEnabled ? 'text-green-500' : 'text-gray-400'}`} />
              <div>
                <h3 className="font-semibold">GPS 위치 전송</h3>
                {gpsEnabled ? (
                  <p className="text-sm text-green-600">전송 중 (마지막: {lastGpsUpdate})</p>
                ) : (
                  <p className="text-sm text-gray-500">대기 중</p>
                )}
              </div>
            </div>
            <button
              onClick={gpsEnabled ? stopGpsTracking : startGpsTracking}
              className={`px-4 py-2 rounded-lg font-semibold ${
                gpsEnabled
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-green-500 hover:bg-green-600 text-white'
              }`}
            >
              {gpsEnabled ? '중지' : '시작'}
            </button>
          </div>

          {currentPosition && (
            <div className="mt-4 p-3 bg-gray-50 rounded text-sm">
              <p>위도: {currentPosition.lat.toFixed(6)}</p>
              <p>경도: {currentPosition.lon.toFixed(6)}</p>
            </div>
          )}
        </div>

        {/* 배송 정보 카드 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-4">
          <h3 className="text-lg font-bold mb-4">배송 정보</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-gray-600">배송일</p>
              <p className="font-semibold">{deliveryInfo.dispatch_date}</p>
            </div>
            <div>
              <p className="text-gray-600">차량번호</p>
              <p className="font-semibold">{deliveryInfo.vehicle_plate || '-'}</p>
            </div>
            <div>
              <p className="text-gray-600">주문 건수</p>
              <p className="font-semibold">{deliveryInfo.total_orders}건</p>
            </div>
            <div>
              <p className="text-gray-600">총 거리</p>
              <p className="font-semibold">{deliveryInfo.total_distance_km?.toFixed(1) || '-'} km</p>
            </div>
          </div>
        </div>

        {/* 경로 정보 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-4">
          <h3 className="text-lg font-bold mb-4">배송 경로</h3>
          <div className="space-y-3">
            {deliveryInfo.routes.map((route, idx) => (
              <div key={idx} className="flex items-start border-l-4 border-blue-500 pl-4 py-2">
                <span className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs mr-3 mt-0.5">
                  {route.sequence}
                </span>
                <div className="flex-1">
                  <p className="font-semibold">{route.location_name}</p>
                  <p className="text-sm text-gray-600">{route.address}</p>
                  {route.estimated_arrival_time && (
                    <p className="text-xs text-blue-600 mt-1">예상 도착: {route.estimated_arrival_time}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 서류 업로드 */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-4">
          <h3 className="text-lg font-bold mb-4">서류 업로드</h3>
          
          <div className="mb-6">
            <h4 className="font-semibold mb-3 text-green-700">출발 시</h4>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleFileUpload('transaction_statement', 'departure')}
                disabled={uploading}
                className={`p-4 border-2 rounded-lg flex flex-col items-center ${
                  uploadedDocs.departure_transaction
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-300 hover:border-blue-500'
                }`}
              >
                {uploadedDocs.departure_transaction ? (
                  <CheckCircle className="h-8 w-8 text-green-500 mb-2" />
                ) : (
                  <FileText className="h-8 w-8 text-gray-400 mb-2" />
                )}
                <span className="text-sm font-medium">거래명세표</span>
              </button>
              
              <button
                onClick={() => handleFileUpload('temperature_record', 'departure')}
                disabled={uploading}
                className={`p-4 border-2 rounded-lg flex flex-col items-center ${
                  uploadedDocs.departure_temperature
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-300 hover:border-blue-500'
                }`}
              >
                {uploadedDocs.departure_temperature ? (
                  <CheckCircle className="h-8 w-8 text-green-500 mb-2" />
                ) : (
                  <Thermometer className="h-8 w-8 text-gray-400 mb-2" />
                )}
                <span className="text-sm font-medium">온도기록지</span>
              </button>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-3 text-blue-700">도착 시</h4>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleFileUpload('transaction_statement', 'arrival')}
                disabled={uploading}
                className={`p-4 border-2 rounded-lg flex flex-col items-center ${
                  uploadedDocs.arrival_transaction
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-300 hover:border-blue-500'
                }`}
              >
                {uploadedDocs.arrival_transaction ? (
                  <CheckCircle className="h-8 w-8 text-green-500 mb-2" />
                ) : (
                  <FileText className="h-8 w-8 text-gray-400 mb-2" />
                )}
                <span className="text-sm font-medium">거래명세표</span>
              </button>
              
              <button
                onClick={() => handleFileUpload('temperature_record', 'arrival')}
                disabled={uploading}
                className={`p-4 border-2 rounded-lg flex flex-col items-center ${
                  uploadedDocs.arrival_temperature
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-300 hover:border-blue-500'
                }`}
              >
                {uploadedDocs.arrival_temperature ? (
                  <CheckCircle className="h-8 w-8 text-green-500 mb-2" />
                ) : (
                  <Thermometer className="h-8 w-8 text-gray-400 mb-2" />
                )}
                <span className="text-sm font-medium">온도기록지</span>
              </button>
            </div>
          </div>
        </div>

        {/* 완료 버튼 */}
        <button
          onClick={completeDelivery}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-lg shadow-lg transition-colors"
        >
          배송 완료
        </button>
      </div>
    </div>
  );
}
