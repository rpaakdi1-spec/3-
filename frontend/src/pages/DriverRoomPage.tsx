/**
 * 기사용 위치공유 방 페이지 (모바일 최적화)
 * - URL: /room/driver/:driverToken
 * - 기사가 링크 클릭 시 자동 입장
 * - GPS 자동 수집 및 서버 전송 (30초 간격)
 * - 출발/도착 시 거래명세표, 온도기록지 사진 업로드
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import {
  MapPin, Upload, CheckCircle, XCircle, Loader2,
  Camera, FileText, Thermometer, Navigation, AlertCircle,
  Wifi, WifiOff, Clock, Car, Phone
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

interface RoomInfo {
  room_id: number;
  room_code: string;
  title: string;
  description?: string;
  client_name?: string;
  status: string;
  driver_name?: string;
  vehicle_plate?: string;
  documents: DocumentInfo[];
  is_completed: boolean;
  expires_at?: string;
}

interface DocumentInfo {
  id: number;
  document_type: string;
  stage: string;
  file_url: string;
  file_name: string;
  created_at: string;
}

interface UploadingState {
  [key: string]: boolean;
}

const DOCUMENT_TYPES = ['거래명세표', '온도기록지', '기타'];
const STAGES = ['출발', '도착'];

const DriverRoomPage: React.FC = () => {
  const { driverToken } = useParams<{ driverToken: string }>();

  const [roomInfo, setRoomInfo] = useState<RoomInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // GPS 상태
  const [gpsStatus, setGpsStatus] = useState<'idle' | 'active' | 'error'>('idle');
  const [lastLocation, setLastLocation] = useState<{ lat: number; lon: number; time: string } | null>(null);
  const [locationCount, setLocationCount] = useState(0);
  const watchIdRef = useRef<number | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const pendingLocationRef = useRef<GeolocationPosition | null>(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  // 업로드 상태
  const [uploading, setUploading] = useState<UploadingState>({});
  const [uploadSuccess, setUploadSuccess] = useState<{ [key: string]: boolean }>({});
  const [selectedStage, setSelectedStage] = useState<'출발' | '도착'>('출발');
  const fileInputRefs = useRef<{ [key: string]: HTMLInputElement | null }>({});

  // 완료 처리
  const [completing, setCompleting] = useState(false);
  const [completed, setCompleted] = useState(false);

  // 네트워크 상태 감지
  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // 방 정보 로드
  useEffect(() => {
    if (!driverToken) return;
    loadRoomInfo();
  }, [driverToken]);

  const loadRoomInfo = async () => {
    try {
      setLoading(true);
      const res = await axios.get(`${API_BASE}/room/driver/${driverToken}`);
      setRoomInfo(res.data);
      if (res.data.is_completed) setCompleted(true);
      setError(null);
    } catch (err: any) {
      const msg = err.response?.data?.detail || '방 정보를 불러올 수 없습니다.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  // GPS 위치 전송
  const sendLocation = useCallback(async (pos: GeolocationPosition) => {
    if (!driverToken || !isOnline) {
      pendingLocationRef.current = pos;
      return;
    }
    try {
      await axios.post(`${API_BASE}/room/driver/${driverToken}/location`, {
        latitude: pos.coords.latitude,
        longitude: pos.coords.longitude,
        accuracy: pos.coords.accuracy,
        speed: pos.coords.speed ? pos.coords.speed * 3.6 : null, // m/s → km/h
        heading: pos.coords.heading,
      });
      setLastLocation({
        lat: pos.coords.latitude,
        lon: pos.coords.longitude,
        time: new Date().toLocaleTimeString('ko-KR'),
      });
      setLocationCount(prev => prev + 1);
    } catch (err) {
      console.error('위치 전송 실패:', err);
    }
  }, [driverToken, isOnline]);

  // GPS 추적 시작
  const startGPS = useCallback(() => {
    if (!navigator.geolocation) {
      setGpsStatus('error');
      return;
    }

    setGpsStatus('active');

    // 첫 위치 즉시 가져오기
    navigator.geolocation.getCurrentPosition(
      (pos) => sendLocation(pos),
      (err) => {
        console.error('GPS 오류:', err);
        setGpsStatus('error');
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );

    // 30초마다 위치 업데이트
    intervalRef.current = setInterval(() => {
      navigator.geolocation.getCurrentPosition(
        (pos) => sendLocation(pos),
        (err) => console.error('GPS 주기 오류:', err),
        { enableHighAccuracy: true, timeout: 10000 }
      );
    }, 30000);
  }, [sendLocation]);

  // GPS 중지
  const stopGPS = useCallback(() => {
    if (watchIdRef.current !== null) {
      navigator.geolocation.clearWatch(watchIdRef.current);
      watchIdRef.current = null;
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setGpsStatus('idle');
  }, []);

  // 컴포넌트 언마운트 시 GPS 정리
  useEffect(() => {
    return () => stopGPS();
  }, [stopGPS]);

  // 온라인 복구 시 대기 중 위치 전송
  useEffect(() => {
    if (isOnline && pendingLocationRef.current) {
      sendLocation(pendingLocationRef.current);
      pendingLocationRef.current = null;
    }
  }, [isOnline, sendLocation]);

  // 파일 업로드
  const handleFileUpload = async (docType: string, stage: string, file: File) => {
    const key = `${stage}_${docType}`;
    setUploading(prev => ({ ...prev, [key]: true }));

    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', docType);
    formData.append('stage', stage);

    // 현재 위치 첨부 (가능한 경우)
    if (lastLocation) {
      formData.append('lat', String(lastLocation.lat));
      formData.append('lon', String(lastLocation.lon));
    }

    try {
      await axios.post(
        `${API_BASE}/room/driver/${driverToken}/documents`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );
      setUploadSuccess(prev => ({ ...prev, [key]: true }));
      // 업로드 성공 후 방 정보 새로고침
      await loadRoomInfo();
      setTimeout(() => setUploadSuccess(prev => ({ ...prev, [key]: false })), 3000);
    } catch (err: any) {
      const msg = err.response?.data?.detail || '업로드에 실패했습니다.';
      alert(`업로드 실패: ${msg}`);
    } finally {
      setUploading(prev => ({ ...prev, [key]: false }));
    }
  };

  const triggerFileInput = (docType: string, stage: string) => {
    const key = `${stage}_${docType}`;
    fileInputRefs.current[key]?.click();
  };

  // 운행 완료
  const handleComplete = async () => {
    if (!window.confirm('운행을 완료 처리하시겠습니까?')) return;
    setCompleting(true);
    try {
      await axios.post(`${API_BASE}/room/driver/${driverToken}/complete`);
      setCompleted(true);
      stopGPS();
    } catch (err: any) {
      alert(err.response?.data?.detail || '완료 처리에 실패했습니다.');
    } finally {
      setCompleting(false);
    }
  };

  // ====== 렌더링 ======

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center text-white">
          <Loader2 className="animate-spin mx-auto mb-4" size={48} />
          <p className="text-lg">방 정보를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="text-center text-white max-w-sm">
          <XCircle className="mx-auto mb-4 text-red-400" size={64} />
          <h2 className="text-xl font-bold mb-2">접근할 수 없습니다</h2>
          <p className="text-gray-400">{error}</p>
        </div>
      </div>
    );
  }

  if (completed || roomInfo?.is_completed) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="text-center text-white max-w-sm">
          <CheckCircle className="mx-auto mb-4 text-green-400" size={64} />
          <h2 className="text-2xl font-bold mb-2">운행 완료</h2>
          <p className="text-gray-300 mb-2">{roomInfo?.title}</p>
          <p className="text-gray-400 text-sm">수고하셨습니다! 안전 운행 감사합니다.</p>
        </div>
      </div>
    );
  }

  // 업로드된 문서 분류
  const uploadedDocs = roomInfo?.documents || [];
  const getUploadedDoc = (type: string, stage: string) =>
    uploadedDocs.find(d => d.document_type === type && d.stage === stage);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* 상단 헤더 */}
      <div className="bg-gray-800 border-b border-gray-700 px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Car className="text-blue-400" size={20} />
            <div>
              <h1 className="font-bold text-sm leading-tight">{roomInfo?.title}</h1>
              {roomInfo?.client_name && (
                <p className="text-gray-400 text-xs">{roomInfo.client_name}</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {isOnline ? (
              <Wifi size={16} className="text-green-400" />
            ) : (
              <WifiOff size={16} className="text-red-400" />
            )}
            <span className={`text-xs px-2 py-1 rounded-full ${
              gpsStatus === 'active' ? 'bg-green-500/20 text-green-400' :
              gpsStatus === 'error' ? 'bg-red-500/20 text-red-400' :
              'bg-gray-700 text-gray-400'
            }`}>
              {gpsStatus === 'active' ? '📍 GPS 켜짐' : gpsStatus === 'error' ? '⚠️ GPS 오류' : 'GPS 꺼짐'}
            </span>
          </div>
        </div>

        {/* 기사 정보 */}
        {(roomInfo?.driver_name || roomInfo?.vehicle_plate) && (
          <div className="mt-2 flex gap-4 text-xs text-gray-400">
            {roomInfo.driver_name && <span>👤 {roomInfo.driver_name}</span>}
            {roomInfo.vehicle_plate && <span>🚛 {roomInfo.vehicle_plate}</span>}
          </div>
        )}
      </div>

      <div className="p-4 space-y-4 max-w-lg mx-auto">

        {/* GPS 섹션 */}
        <div className="bg-gray-800 rounded-2xl p-4 border border-gray-700">
          <h2 className="font-bold text-base mb-3 flex items-center gap-2">
            <Navigation className="text-blue-400" size={18} />
            위치 공유
          </h2>

          {gpsStatus === 'idle' && (
            <button
              onClick={startGPS}
              className="w-full py-4 bg-blue-600 hover:bg-blue-700 active:bg-blue-800 rounded-xl font-bold text-lg transition-colors flex items-center justify-center gap-2"
            >
              <MapPin size={22} />
              위치 공유 시작
            </button>
          )}

          {gpsStatus === 'active' && (
            <div className="space-y-3">
              <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-3">
                <div className="flex items-center gap-2 text-green-400 mb-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  <span className="font-medium">위치 공유 중</span>
                </div>
                {lastLocation && (
                  <div className="text-xs text-gray-400 space-y-0.5">
                    <p>위도: {lastLocation.lat.toFixed(6)}</p>
                    <p>경도: {lastLocation.lon.toFixed(6)}</p>
                    <p className="flex items-center gap-1">
                      <Clock size={10} /> 마지막 전송: {lastLocation.time} ({locationCount}회)
                    </p>
                  </div>
                )}
              </div>
              <button
                onClick={stopGPS}
                className="w-full py-2 bg-red-600/20 border border-red-600/40 hover:bg-red-600/30 rounded-xl text-red-400 text-sm font-medium transition-colors"
              >
                위치 공유 중지
              </button>
            </div>
          )}

          {gpsStatus === 'error' && (
            <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-3">
              <div className="flex items-center gap-2 text-red-400 mb-2">
                <AlertCircle size={16} />
                <span>GPS를 사용할 수 없습니다</span>
              </div>
              <p className="text-xs text-gray-400">브라우저 설정에서 위치 접근을 허용해주세요.</p>
              <button
                onClick={startGPS}
                className="mt-2 text-xs text-blue-400 underline"
              >
                다시 시도
              </button>
            </div>
          )}
        </div>

        {/* 서류 업로드 섹션 */}
        <div className="bg-gray-800 rounded-2xl p-4 border border-gray-700">
          <h2 className="font-bold text-base mb-4 flex items-center gap-2">
            <Upload className="text-purple-400" size={18} />
            서류 사진 업로드
          </h2>

          {/* 단계 선택 탭 */}
          <div className="flex gap-2 mb-4">
            {STAGES.map(stage => (
              <button
                key={stage}
                onClick={() => setSelectedStage(stage as '출발' | '도착')}
                className={`flex-1 py-2.5 rounded-xl font-bold text-sm transition-colors ${
                  selectedStage === stage
                    ? stage === '출발'
                      ? 'bg-blue-600 text-white'
                      : 'bg-orange-600 text-white'
                    : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                }`}
              >
                {stage === '출발' ? '🚀 출발' : '🏁 도착'}
              </button>
            ))}
          </div>

          {/* 서류 유형별 업로드 버튼 */}
          <div className="space-y-3">
            {DOCUMENT_TYPES.map(docType => {
              const key = `${selectedStage}_${docType}`;
              const uploaded = getUploadedDoc(docType, selectedStage);
              const isUploading = uploading[key];
              const isSuccess = uploadSuccess[key];

              return (
                <div key={key} className="bg-gray-700/50 rounded-xl p-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {docType === '거래명세표' ? (
                        <FileText size={16} className="text-blue-400" />
                      ) : docType === '온도기록지' ? (
                        <Thermometer size={16} className="text-red-400" />
                      ) : (
                        <FileText size={16} className="text-gray-400" />
                      )}
                      <span className="font-medium text-sm">{docType}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${
                        selectedStage === '출발'
                          ? 'bg-blue-500/20 text-blue-300'
                          : 'bg-orange-500/20 text-orange-300'
                      }`}>{selectedStage}</span>
                    </div>
                    {uploaded && (
                      <CheckCircle size={16} className="text-green-400" />
                    )}
                  </div>

                  {uploaded ? (
                    <div className="text-xs text-green-400 mb-2">
                      ✅ 업로드 완료 ({new Date(uploaded.created_at).toLocaleString('ko-KR')})
                    </div>
                  ) : null}

                  {/* 히든 파일 인풋 */}
                  <input
                    type="file"
                    ref={el => fileInputRefs.current[key] = el}
                    className="hidden"
                    accept="image/*,.pdf"
                    capture="environment"
                    onChange={e => {
                      const file = e.target.files?.[0];
                      if (file) handleFileUpload(docType, selectedStage, file);
                      e.target.value = '';
                    }}
                  />

                  <button
                    onClick={() => triggerFileInput(docType, selectedStage)}
                    disabled={isUploading}
                    className={`w-full py-3 rounded-xl font-medium text-sm flex items-center justify-center gap-2 transition-colors ${
                      isSuccess
                        ? 'bg-green-600/30 border border-green-600/50 text-green-400'
                        : uploaded
                        ? 'bg-gray-600 hover:bg-gray-500 text-gray-200'
                        : 'bg-purple-600 hover:bg-purple-700 active:bg-purple-800 text-white'
                    }`}
                  >
                    {isUploading ? (
                      <>
                        <Loader2 size={16} className="animate-spin" />
                        업로드 중...
                      </>
                    ) : isSuccess ? (
                      <>
                        <CheckCircle size={16} />
                        업로드 완료!
                      </>
                    ) : (
                      <>
                        <Camera size={16} />
                        {uploaded ? '다시 촬영/업로드' : '사진 촬영 또는 파일 선택'}
                      </>
                    )}
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* 업로드 현황 요약 */}
        {uploadedDocs.length > 0 && (
          <div className="bg-gray-800 rounded-2xl p-4 border border-gray-700">
            <h3 className="font-bold text-sm mb-3 text-gray-300">📋 업로드 현황</h3>
            <div className="space-y-2">
              {uploadedDocs.map(doc => (
                <div key={doc.id} className="flex items-center gap-2 text-xs text-gray-400">
                  <CheckCircle size={12} className="text-green-400 flex-shrink-0" />
                  <span className={`px-1.5 py-0.5 rounded text-xs ${
                    doc.stage === '출발' ? 'bg-blue-500/20 text-blue-300' : 'bg-orange-500/20 text-orange-300'
                  }`}>{doc.stage}</span>
                  <span>{doc.document_type}</span>
                  <span className="text-gray-500 ml-auto">
                    {new Date(doc.created_at).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 운행 완료 버튼 */}
        <div className="bg-gray-800 rounded-2xl p-4 border border-gray-700">
          <p className="text-xs text-gray-400 mb-3">
            모든 서류 업로드 완료 후 운행 완료 버튼을 누르세요.
          </p>
          <button
            onClick={handleComplete}
            disabled={completing}
            className="w-full py-4 bg-green-600 hover:bg-green-700 active:bg-green-800 disabled:bg-gray-600 rounded-xl font-bold text-lg transition-colors flex items-center justify-center gap-2"
          >
            {completing ? (
              <>
                <Loader2 size={20} className="animate-spin" />
                처리 중...
              </>
            ) : (
              <>
                <CheckCircle size={20} />
                운행 완료
              </>
            )}
          </button>
        </div>

        <div className="pb-8" /> {/* 하단 여백 */}
      </div>
    </div>
  );
};

export default DriverRoomPage;
