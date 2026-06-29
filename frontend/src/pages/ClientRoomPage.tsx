/**
 * 고객사용 실시간 위치 조회 페이지
 * - URL: /room/client/:clientToken
 * - 인증 없이 링크만으로 접근 가능
 * - 네이버 지도 기반 실시간 위치 표시
 * - 기사 GPS 경로 표시
 * - 업로드된 서류 확인
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import {
  MapPin, RefreshCw, CheckCircle, Clock, Truck,
  FileText, Thermometer, AlertCircle, Loader2,
  Eye, Download, Building2, Phone, Car
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';
const NAVER_CLIENT_ID = import.meta.env.VITE_NAVER_MAP_KEY_ID || import.meta.env.VITE_NAVER_MAP_CLIENT_ID || 'pkciiaux61';

interface LocationPoint {
  latitude: number;
  longitude: number;
  recorded_at: string;
}

interface DocumentInfo {
  id: number;
  document_type: string;
  stage: string;
  file_url: string;
  file_name: string;
  mime_type?: string;
  created_at: string;
}

interface RoomClientData {
  room_code: string;
  title: string;
  description?: string;
  status: string;
  driver_name?: string;
  vehicle_plate?: string;
  current_location: {
    latitude: number;
    longitude: number;
    updated_at: string;
  } | null;
  location_history: LocationPoint[];
  documents: DocumentInfo[];
  driver_joined_at?: string;
  completed_at?: string;
  is_completed: boolean;
  expires_at?: string;
}

const STATUS_LABELS: { [key: string]: { label: string; color: string } } = {
  '대기중': { label: '배송 대기', color: 'text-yellow-400 bg-yellow-400/10' },
  '진행중': { label: '배송 중', color: 'text-blue-400 bg-blue-400/10' },
  '완료': { label: '배송 완료', color: 'text-green-400 bg-green-400/10' },
  '취소': { label: '취소됨', color: 'text-red-400 bg-red-400/10' },
};

const ClientRoomPage: React.FC = () => {
  const { clientToken } = useParams<{ clientToken: string }>();

  const [data, setData] = useState<RoomClientData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [refreshing, setRefreshing] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<DocumentInfo | null>(null);

  const mapRef = useRef<HTMLDivElement>(null);
  const naverMapRef = useRef<any>(null);
  const markerRef = useRef<any>(null);
  const pathRef = useRef<any>(null);

  // 데이터 로드
  const fetchData = useCallback(async (showLoading = false) => {
    if (!clientToken) return;
    if (showLoading) setRefreshing(true);
    try {
      const res = await axios.get(`${API_BASE}/room/client/${clientToken}`);
      setData(res.data);
      setLastRefresh(new Date());
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || '데이터를 불러올 수 없습니다.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [clientToken]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // 10초마다 자동 갱신 (완료 전까지) — UVIS GPS 5분 주기 수신 감안
  useEffect(() => {
    if (data?.is_completed) return;
    const interval = setInterval(() => fetchData(false), 10000);
    return () => clearInterval(interval);
  }, [fetchData, data?.is_completed]);

  // 네이버 지도 초기화
  useEffect(() => {
    if (!data?.current_location) return;
    if (!mapRef.current) return;

    const initMap = () => {
      if (!(window as any).naver?.maps) return;

      const naver = (window as any).naver;
      const loc = data.current_location!;
      const center = new naver.maps.LatLng(loc.latitude, loc.longitude);

      if (!naverMapRef.current) {
        naverMapRef.current = new naver.maps.Map(mapRef.current, {
          center,
          zoom: 14,
          zoomControl: true,
          mapTypeControl: false,
        });
      } else {
        naverMapRef.current.setCenter(center);
      }

      // 현재 위치 마커 업데이트
      if (markerRef.current) {
        markerRef.current.setPosition(center);
      } else {
        markerRef.current = new naver.maps.Marker({
          position: center,
          map: naverMapRef.current,
          icon: {
            content: `<div style="
              background: #3b82f6;
              border: 3px solid white;
              border-radius: 50%;
              width: 20px; height: 20px;
              box-shadow: 0 2px 8px rgba(59,130,246,0.5);
              position: relative;
            ">
              <div style="
                position: absolute; top: -28px; left: 50%; transform: translateX(-50%);
                background: #1e40af; color: white; font-size: 10px;
                padding: 2px 6px; border-radius: 8px; white-space: nowrap;
                font-weight: bold;
              ">🚛 차량 위치</div>
            </div>`,
            anchor: new naver.maps.Point(10, 10),
          },
        });
      }

      // 경로 업데이트
      if (data.location_history.length > 1) {
        const path = data.location_history.map(
          p => new naver.maps.LatLng(p.latitude, p.longitude)
        );

        if (pathRef.current) {
          pathRef.current.setPath(path);
        } else {
          pathRef.current = new naver.maps.Polyline({
            map: naverMapRef.current,
            path,
            strokeColor: '#3b82f6',
            strokeWeight: 4,
            strokeOpacity: 0.7,
          });
        }
      }
    };

    if ((window as any).naver?.maps) {
      initMap();
    } else {
      // 지도 SDK 로드
      const script = document.getElementById('naver-map-script');
      if (!script) {
        const s = document.createElement('script');
        s.id = 'naver-map-script';
        s.src = `https://oapi.map.naver.com/openapi/v3/maps.js?ncpKeyId=${NAVER_CLIENT_ID}`;
        s.onload = initMap;
        document.head.appendChild(s);
      } else {
        script.addEventListener('load', initMap);
      }
    }
  }, [data?.current_location, data?.location_history]);

  // ====== 렌더링 ======

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center text-gray-600">
          <Loader2 className="animate-spin mx-auto mb-4 text-blue-500" size={48} />
          <p className="text-lg">위치 정보를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center max-w-sm">
          <AlertCircle className="mx-auto mb-4 text-red-400" size={64} />
          <h2 className="text-xl font-bold text-gray-800 mb-2">접근할 수 없습니다</h2>
          <p className="text-gray-500">{error}</p>
        </div>
      </div>
    );
  }

  const statusInfo = data?.status ? STATUS_LABELS[data.status] || { label: data.status, color: 'text-gray-600 bg-gray-100' } : null;

  const departureDocs = data?.documents.filter(d => d.stage === '출발') || [];
  const arrivalDocs = data?.documents.filter(d => d.stage === '도착') || [];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <div className="bg-white border-b shadow-sm sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2 mb-0.5">
                <Truck className="text-blue-600" size={18} />
                <h1 className="font-bold text-gray-900 text-sm leading-tight">{data?.title}</h1>
              </div>
              {statusInfo && (
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusInfo.color}`}>
                  {statusInfo.label}
                </span>
              )}
            </div>
            <button
              onClick={() => fetchData(true)}
              disabled={refreshing}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-600 rounded-lg text-xs font-medium hover:bg-blue-100 transition-colors"
            >
              <RefreshCw size={12} className={refreshing ? 'animate-spin' : ''} />
              새로고침
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-2xl mx-auto p-4 space-y-4">

        {/* 배송 정보 */}
        <div className="bg-white rounded-2xl p-4 shadow-sm border">
          <div className="grid grid-cols-2 gap-3 text-sm">
            {data?.driver_name && (
              <div className="flex items-center gap-2 text-gray-600">
                <Phone size={14} className="text-gray-400" />
                <span>기사: <strong>{data.driver_name}</strong></span>
              </div>
            )}
            {data?.vehicle_plate && (
              <div className="flex items-center gap-2 text-gray-600">
                <Car size={14} className="text-gray-400" />
                <span>차량: <strong>{data.vehicle_plate}</strong></span>
              </div>
            )}
            {data?.driver_joined_at && (
              <div className="flex items-center gap-2 text-gray-600">
                <Clock size={14} className="text-gray-400" />
                <span>출발: {new Date(data.driver_joined_at).toLocaleString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
              </div>
            )}
            {data?.completed_at && (
              <div className="flex items-center gap-2 text-green-600">
                <CheckCircle size={14} />
                <span>완료: {new Date(data.completed_at).toLocaleString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</span>
              </div>
            )}
          </div>
        </div>

        {/* 지도 */}
        <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
          <div className="px-4 py-3 border-b flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MapPin className="text-blue-600" size={16} />
              <span className="font-semibold text-gray-800">실시간 위치</span>
            </div>
            {data?.current_location && (
              <span className="text-xs text-gray-500">
                <Clock size={10} className="inline mr-1" />
                {new Date(data.current_location.updated_at).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })} 기준
              </span>
            )}
          </div>

          {data?.current_location ? (
            <div ref={mapRef} style={{ height: '320px', width: '100%' }} />
          ) : (
            <div className="h-48 flex flex-col items-center justify-center text-gray-400 bg-gray-50">
              <MapPin size={32} className="mb-2 opacity-30" />
              <p className="text-sm">차량 GPS 신호를 기다리는 중입니다.</p>
              <p className="text-xs mt-1 text-gray-300">차량 시동 ON 후 자동으로 위치가 표시됩니다.</p>
            </div>
          )}
        </div>

        {/* 운행 경로 수 */}
        {(data?.location_history?.length || 0) > 0 && (
          <div className="text-xs text-center text-gray-500">
            총 {data!.location_history.length}개 위치 기록됨
          </div>
        )}

        {/* 서류 현황 */}
        {(departureDocs.length > 0 || arrivalDocs.length > 0) && (
          <div className="bg-white rounded-2xl p-4 shadow-sm border">
            <h3 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
              <FileText className="text-purple-500" size={16} />
              서류 현황
            </h3>

            {departureDocs.length > 0 && (
              <div className="mb-3">
                <p className="text-xs font-semibold text-blue-600 mb-2">🚀 출발 서류</p>
                <div className="space-y-2">
                  {departureDocs.map(doc => (
                    <DocCard key={doc.id} doc={doc} onView={setSelectedDoc} />
                  ))}
                </div>
              </div>
            )}

            {arrivalDocs.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-orange-600 mb-2">🏁 도착 서류</p>
                <div className="space-y-2">
                  {arrivalDocs.map(doc => (
                    <DocCard key={doc.id} doc={doc} onView={setSelectedDoc} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* 완료 상태 */}
        {data?.is_completed && (
          <div className="bg-green-50 border border-green-200 rounded-2xl p-4 text-center">
            <CheckCircle className="mx-auto mb-2 text-green-500" size={32} />
            <p className="font-bold text-green-700">배송이 완료되었습니다</p>
            {data.completed_at && (
              <p className="text-xs text-green-600 mt-1">
                완료 시각: {new Date(data.completed_at).toLocaleString('ko-KR')}
              </p>
            )}
          </div>
        )}

        {/* 마지막 갱신 */}
        <p className="text-xs text-center text-gray-400">
          마지막 갱신: {lastRefresh.toLocaleTimeString('ko-KR')} (10초마다 자동 갱신)
        </p>

        <div className="pb-8" />
      </div>

      {/* 문서 뷰어 모달 */}
      {selectedDoc && (
        <div
          className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedDoc(null)}
        >
          <div
            className="bg-white rounded-2xl max-w-lg w-full overflow-hidden"
            onClick={e => e.stopPropagation()}
          >
            <div className="px-4 py-3 border-b flex items-center justify-between">
              <div>
                <p className="font-bold text-gray-800">{selectedDoc.document_type}</p>
                <p className="text-xs text-gray-500">{selectedDoc.stage} · {new Date(selectedDoc.created_at).toLocaleString('ko-KR')}</p>
              </div>
              <div className="flex gap-2">
                <a
                  href={selectedDoc.file_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg"
                  title="새 탭에서 열기"
                >
                  <Eye size={18} />
                </a>
                <button
                  onClick={() => setSelectedDoc(null)}
                  className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg"
                >
                  ✕
                </button>
              </div>
            </div>
            <div className="p-2">
              {selectedDoc.mime_type?.startsWith('image/') || selectedDoc.file_url.match(/\.(jpg|jpeg|png|gif|webp|heic)$/i) ? (
                <img
                  src={selectedDoc.file_url}
                  alt={selectedDoc.file_name}
                  className="w-full max-h-[70vh] object-contain rounded-xl"
                />
              ) : (
                <div className="flex flex-col items-center justify-center py-8 text-gray-500">
                  <FileText size={48} className="mb-2 opacity-30" />
                  <p className="text-sm">{selectedDoc.file_name}</p>
                  <a
                    href={selectedDoc.file_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm"
                  >
                    파일 열기
                  </a>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// 서류 카드 컴포넌트
const DocCard: React.FC<{ doc: DocumentInfo; onView: (d: DocumentInfo) => void }> = ({ doc, onView }) => (
  <div
    className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl cursor-pointer hover:bg-gray-100 transition-colors"
    onClick={() => onView(doc)}
  >
    {doc.document_type === '온도기록지' ? (
      <Thermometer size={18} className="text-red-400 flex-shrink-0" />
    ) : (
      <FileText size={18} className="text-blue-400 flex-shrink-0" />
    )}
    <div className="flex-1 min-w-0">
      <p className="text-sm font-medium text-gray-800 truncate">{doc.document_type}</p>
      <p className="text-xs text-gray-500">
        {new Date(doc.created_at).toLocaleString('ko-KR', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
      </p>
    </div>
    <Eye size={14} className="text-gray-400 flex-shrink-0" />
  </div>
);

export default ClientRoomPage;
