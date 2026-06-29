import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { MapPin, Package, FileText, Clock, Truck, Download, CheckCircle, Circle, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';

interface LocationPoint {
  latitude: number;
  longitude: number;
  timestamp: string;
  speed?: number;
}

interface RouteStop {
  sequence: number;
  location_name: string;
  address: string;
  route_type: string;
  estimated_arrival_time?: string;
  is_completed: boolean;
}

interface Document {
  id: number;
  document_type: string;
  stage: string;
  file_url: string;
  file_name: string;
  file_size: number;
  uploaded_at: string;
  notes?: string;
}

interface TrackingData {
  tracking_number: string;
  dispatch_number: string;
  dispatch_date: string;
  status: string;
  vehicle_number: string;
  driver_name?: string;
  current_location?: LocationPoint;
  routes: RouteStop[];
  progress_percentage: number;
  estimated_arrival?: string;
  documents: Document[];
  total_pallets: number;
  customer_name?: string;
  last_updated: string;
}

const PublicTrackingPage: React.FC = () => {
  const { trackingNumber } = useParams<{ trackingNumber: string }>();
  const [trackingData, setTrackingData] = useState<TrackingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchTrackingData = async () => {
    try {
      const response = await fetch(
        `/api/v1/dispatch/tracking/public/${trackingNumber}`
      );

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('추적 번호를 찾을 수 없습니다.');
        } else if (response.status === 410) {
          throw new Error('추적 정보가 만료되었습니다.');
        }
        throw new Error('추적 정보를 불러오는데 실패했습니다.');
      }

      const data = await response.json();
      setTrackingData(data);
      setError(null);
    } catch (err: any) {
      setError(err.message);
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrackingData();

    const interval = autoRefresh
      ? setInterval(fetchTrackingData, 30000)
      : undefined;

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [trackingNumber, autoRefresh]);

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      '확정': 'bg-blue-100 text-blue-800',
      '진행중': 'bg-yellow-100 text-yellow-800',
      '배차완료': 'bg-green-100 text-green-800',
      '취소': 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getDocumentIcon = (type: string) => {
    if (type.includes('거래명세표')) return '📋';
    if (type.includes('온도기록')) return '🌡️';
    if (type.includes('서명')) return '✍️';
    return '📄';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">배송 정보를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error || !trackingData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-8">
          <div className="text-6xl mb-4">📦</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">추적 정보 없음</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <p className="text-sm text-gray-500 font-mono">{trackingNumber}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">실시간 배송 추적</h1>
              <p className="text-sm text-gray-500 mt-1">
                추적번호: <span className="font-mono font-semibold">{trackingData.tracking_number}</span>
              </p>
            </div>
            <div className="text-right">
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(trackingData.status)}`}>
                {trackingData.status}
              </div>
              <button
                onClick={() => fetchTrackingData()}
                className="ml-2 p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
                title="새로고침"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Progress + Routes */}
          <div className="lg:col-span-2 space-y-6">
            {/* Progress */}
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-lg font-semibold">배송 진행률</h2>
                <span className="text-2xl font-bold text-blue-600">
                  {trackingData.progress_percentage.toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className="bg-blue-600 h-4 rounded-full transition-all"
                  style={{ width: `${trackingData.progress_percentage}%` }}
                />
              </div>
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div>
                  <p className="text-sm text-gray-500">팔레트 수</p>
                  <p className="text-lg font-semibold">{trackingData.total_pallets}개</p>
                </div>
                {trackingData.estimated_arrival && (
                  <div>
                    <p className="text-sm text-gray-500">예상 완료</p>
                    <p className="text-lg font-semibold">{trackingData.estimated_arrival}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Current Location */}
            {trackingData.current_location && (
              <div className="bg-blue-50 rounded-lg shadow p-6">
                <div className="flex items-start">
                  <MapPin className="w-6 h-6 text-blue-600 mr-3 flex-shrink-0 mt-1" />
                  <div>
                    <h3 className="font-semibold text-blue-900">현재 위치</h3>
                    <p className="text-sm text-blue-700 mt-1">
                      위도: {trackingData.current_location.latitude.toFixed(6)}, 
                      경도: {trackingData.current_location.longitude.toFixed(6)}
                    </p>
                    {trackingData.current_location.speed && (
                      <p className="text-sm text-blue-600 mt-1">
                        속도: {trackingData.current_location.speed} km/h
                      </p>
                    )}
                    <p className="text-xs text-blue-500 mt-1">
                      업데이트: {new Date(trackingData.current_location.timestamp).toLocaleString('ko-KR')}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Routes */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">배송 경로</h2>
              <div className="space-y-4">
                {trackingData.routes.map((route, index) => (
                  <div key={index} className="flex items-start">
                    <div className="flex-shrink-0">
                      {route.is_completed ? (
                        <CheckCircle className="w-6 h-6 text-green-600" />
                      ) : (
                        <Circle className="w-6 h-6 text-gray-400" />
                      )}
                    </div>
                    <div className="ml-4 flex-1">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold">{route.location_name}</h3>
                        <span className="text-sm text-gray-500">{route.route_type}</span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{route.address}</p>
                      {route.estimated_arrival_time && (
                        <p className="text-xs text-gray-500 mt-1">
                          예상 도착: {route.estimated_arrival_time}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right: Info + Documents */}
          <div className="space-y-6">
            {/* Info */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">배차 정보</h2>
              <div className="space-y-3">
                <div className="flex items-center">
                  <Truck className="w-5 h-5 mr-3 text-gray-400" />
                  <div>
                    <p className="text-xs text-gray-500">차량번호</p>
                    <p className="font-semibold">{trackingData.vehicle_number}</p>
                  </div>
                </div>
                {trackingData.driver_name && (
                  <div className="flex items-center">
                    <Package className="w-5 h-5 mr-3 text-gray-400" />
                    <div>
                      <p className="text-xs text-gray-500">기사님</p>
                      <p className="font-semibold">{trackingData.driver_name}</p>
                    </div>
                  </div>
                )}
                <div className="flex items-center">
                  <FileText className="w-5 h-5 mr-3 text-gray-400" />
                  <div>
                    <p className="text-xs text-gray-500">배차번호</p>
                    <p className="font-semibold">{trackingData.dispatch_number}</p>
                  </div>
                </div>
                <div className="flex items-center">
                  <Clock className="w-5 h-5 mr-3 text-gray-400" />
                  <div>
                    <p className="text-xs text-gray-500">배차일자</p>
                    <p className="font-semibold">{trackingData.dispatch_date}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Documents */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">배송 서류</h2>
              {trackingData.documents.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-8">
                  아직 업로드된 서류가 없습니다.
                </p>
              ) : (
                <div className="space-y-3">
                  {trackingData.documents.map((doc) => (
                    <a
                      key={doc.id}
                      href={doc.file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="block border border-gray-200 rounded-lg p-3 hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-start flex-1">
                          <span className="text-2xl mr-3">{getDocumentIcon(doc.document_type)}</span>
                          <div className="flex-1 min-w-0">
                            <h3 className="font-medium truncate">
                              {doc.document_type} ({doc.stage})
                            </h3>
                            <p className="text-sm text-gray-500 truncate">{doc.file_name}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-xs text-gray-400">{formatFileSize(doc.file_size)}</span>
                              <span className="text-xs text-gray-400">•</span>
                              <span className="text-xs text-gray-400">
                                {new Date(doc.uploaded_at).toLocaleString('ko-KR', {
                                  month: 'short',
                                  day: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit',
                                })}
                              </span>
                            </div>
                          </div>
                        </div>
                        <Download className="w-5 h-5 text-blue-600 flex-shrink-0 ml-2" />
                      </div>
                      {doc.notes && (
                        <p className="text-xs text-gray-600 mt-2 ml-11">{doc.notes}</p>
                      )}
                    </a>
                  ))}
                </div>
              )}
            </div>

            {/* Auto Refresh */}
            <div className="bg-gray-50 rounded-lg p-4">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-2"
                />
                <span className="text-sm text-gray-700">30초마다 자동 새로고침</span>
              </label>
              <p className="text-xs text-gray-500 mt-2">
                마지막 업데이트: {new Date(trackingData.last_updated).toLocaleString('ko-KR')}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublicTrackingPage;
