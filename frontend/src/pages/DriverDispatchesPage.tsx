import React, { useEffect, useState, useRef } from 'react';
import { Truck, MapPin, Clock, Upload, FileText, Thermometer, FileSignature, CheckCircle, AlertCircle, Camera, Navigation } from 'lucide-react';
import apiClient from '../api/client';
import Card from '../components/common/Card';
import Loading from '../components/common/Loading';
import toast from 'react-hot-toast';

interface DriverDispatch {
  id: number;
  dispatch_number: string;
  dispatch_date: string;
  status: string;
  vehicle_plate: string;
  route_summary?: string;
  estimated_arrival?: string;
  tracking_number?: string;
  // Documents uploaded
  documents?: {
    departure_transaction?: boolean;
    departure_temperature?: boolean;
    arrival_transaction?: boolean;
    arrival_temperature?: boolean;
    arrival_signature?: boolean;
  };
}

interface UploadedDocument {
  id: number;
  document_type: string;
  stage: string;
  file_url: string;
  uploaded_at: string;
}

const DriverDispatchesPage: React.FC = () => {
  const [dispatches, setDispatches] = useState<DriverDispatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDispatch, setSelectedDispatch] = useState<DriverDispatch | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadStage, setUploadStage] = useState<'departure' | 'arrival'>('departure');
  const [uploadingFiles, setUploadingFiles] = useState<{ [key: string]: boolean }>({});
  const [documents, setDocuments] = useState<UploadedDocument[]>([]);
  
  // GPS Tracking
  const [gpsEnabled, setGpsEnabled] = useState(false);
  const [lastLocation, setLastLocation] = useState<{ lat: number; lon: number } | null>(null);
  const [vehicleId, setVehicleId] = useState<string | null>(null);
  const watchIdRef = useRef<number | null>(null);
  const locationIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    fetchDispatches();
    const interval = setInterval(fetchDispatches, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  // GPS Auto-collection
  useEffect(() => {
    if (gpsEnabled && vehicleId) {
      startGPSTracking();
    } else {
      stopGPSTracking();
    }

    return () => {
      stopGPSTracking();
    };
  }, [gpsEnabled, vehicleId]);

  const startGPSTracking = () => {
    if (!navigator.geolocation) {
      toast.error('이 브라우저는 GPS를 지원하지 않습니다');
      return;
    }

    // Watch position with high accuracy
    watchIdRef.current = navigator.geolocation.watchPosition(
      (position) => {
        const location = {
          lat: position.coords.latitude,
          lon: position.coords.longitude
        };
        setLastLocation(location);
      },
      (error) => {
        console.error('GPS 오류:', error);
        if (error.code === error.PERMISSION_DENIED) {
          toast.error('위치 권한이 거부되었습니다. 브라우저 설정에서 위치 권한을 허용해주세요.');
          setGpsEnabled(false);
        }
      },
      {
        enableHighAccuracy: true,
        maximumAge: 10000,
        timeout: 27000
      }
    );

    // Send location to backend every 30 seconds
    locationIntervalRef.current = setInterval(() => {
      if (lastLocation && vehicleId) {
        sendLocationToBackend(lastLocation);
      }
    }, 30000);

    toast.success('🗺️ GPS 추적이 시작되었습니다');
  };

  const stopGPSTracking = () => {
    if (watchIdRef.current !== null) {
      navigator.geolocation.clearWatch(watchIdRef.current);
      watchIdRef.current = null;
    }
    if (locationIntervalRef.current) {
      clearInterval(locationIntervalRef.current);
      locationIntervalRef.current = null;
    }
  };

  const sendLocationToBackend = async (location: { lat: number; lon: number }) => {
    if (!vehicleId) return;

    try {
      await apiClient.post('/uvis/gps/location', {
        vehicle_id: vehicleId,
        latitude: location.lat,
        longitude: location.lon,
        timestamp: new Date().toISOString()
      });
      console.log('📍 위치 전송 성공:', location);
    } catch (error) {
      console.error('위치 전송 실패:', error);
    }
  };

  const toggleGPS = () => {
    if (!gpsEnabled) {
      // Extract vehicle ID from first dispatch
      const firstDispatch = dispatches.find(d => d.status === '진행중' || d.status === '확정');
      if (firstDispatch) {
        setVehicleId(firstDispatch.vehicle_plate);
        setGpsEnabled(true);
      } else {
        toast.error('진행 중인 배차가 없습니다');
      }
    } else {
      setGpsEnabled(false);
      setVehicleId(null);
      toast.success('GPS 추적이 중지되었습니다');
    }
  };

  const fetchDispatches = async () => {
    try {
      // Fetch driver's assigned dispatches
      const response = await apiClient.get('/driver/dispatches');
      setDispatches(response.data || []);
      if (loading) setLoading(false);
    } catch (error) {
      console.error('배차 목록 조회 실패:', error);
      toast.error('배차 목록을 불러오는데 실패했습니다');
      if (loading) setLoading(false);
    }
  };

  const fetchDocuments = async (dispatchId: number) => {
    try {
      const response = await apiClient.get(`/dispatch/documents?dispatch_id=${dispatchId}`);
      setDocuments(response.data || []);
    } catch (error) {
      console.error('서류 목록 조회 실패:', error);
    }
  };

  const openUploadModal = async (dispatch: DriverDispatch, stage: 'departure' | 'arrival') => {
    setSelectedDispatch(dispatch);
    setUploadStage(stage);
    setShowUploadModal(true);
    await fetchDocuments(dispatch.id);
  };

  const uploadDocument = async (
    documentType: 'transaction_statement' | 'temperature_record' | 'signature',
    file: File
  ) => {
    if (!selectedDispatch) return;

    const uploadKey = `${uploadStage}_${documentType}`;
    setUploadingFiles(prev => ({ ...prev, [uploadKey]: true }));

    try {
      const formData = new FormData();
      formData.append('dispatch_id', selectedDispatch.id.toString());
      formData.append('document_type', documentType);
      formData.append('stage', uploadStage);
      formData.append('file', file);

      await apiClient.post('/dispatch/documents/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      toast.success('✅ 서류가 업로드되었습니다!');
      await fetchDocuments(selectedDispatch.id);
      await fetchDispatches(); // Refresh dispatch list
    } catch (error: any) {
      console.error('서류 업로드 실패:', error);
      toast.error(error.response?.data?.detail || '서류 업로드에 실패했습니다');
    } finally {
      setUploadingFiles(prev => ({ ...prev, [uploadKey]: false }));
    }
  };

  const handleFileSelect = async (
    documentType: 'transaction_statement' | 'temperature_record' | 'signature',
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('파일 크기는 10MB를 초과할 수 없습니다');
      return;
    }

    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf'];
    if (!validTypes.includes(file.type)) {
      toast.error('JPG, PNG, PDF 파일만 업로드 가능합니다');
      return;
    }

    await uploadDocument(documentType, file);
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      임시저장: 'bg-gray-100 text-gray-800',
      확정: 'bg-yellow-100 text-yellow-800',
      진행중: 'bg-green-100 text-green-800',
      완료: 'bg-blue-100 text-blue-800',
      취소: 'bg-red-100 text-red-800',
    };
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${styles[status as keyof typeof styles] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };

  const isDocumentUploaded = (documentType: string, stage: string): boolean => {
    return documents.some(doc => 
      doc.document_type === documentType && doc.stage === stage
    );
  };

  const getDocumentLabel = (type: string): string => {
    const labels: { [key: string]: string } = {
      transaction_statement: '거래명세표',
      temperature_record: '온도기록지',
      signature: '서명'
    };
    return labels[type] || type;
  };

  if (loading) {
    return <Loading />;
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">내 배차 목록</h1>
          <p className="text-gray-600 mt-2">오늘의 배송 일정 및 서류 관리</p>
        </div>
        
        {/* GPS Toggle Button */}
        <button
          onClick={toggleGPS}
          className={`px-4 py-2 rounded-lg flex items-center gap-2 font-medium transition-colors ${
            gpsEnabled
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-gray-200 hover:bg-gray-300 text-gray-700'
          }`}
        >
          <Navigation size={20} className={gpsEnabled ? 'animate-pulse' : ''} />
          {gpsEnabled ? 'GPS 추적 중' : 'GPS 시작'}
        </button>
      </div>

      {/* GPS Status Info */}
      {gpsEnabled && lastLocation && (
        <Card>
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <MapPin size={20} className="text-green-600" />
                <div>
                  <p className="font-medium text-green-900">GPS 추적 활성화</p>
                  <p className="text-sm text-green-700">
                    위치: {lastLocation.lat.toFixed(6)}, {lastLocation.lon.toFixed(6)}
                  </p>
                </div>
              </div>
              <span className="text-xs text-green-600 font-mono">30초마다 자동 전송</span>
            </div>
          </div>
        </Card>
      )}

      {/* Dispatch List */}
      {dispatches.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <Truck size={48} className="mx-auto mb-4 text-gray-300" />
            <p className="text-gray-500">배정된 배차가 없습니다</p>
          </div>
        </Card>
      ) : (
        <div className="grid gap-4">
          {dispatches.map((dispatch) => (
            <Card key={dispatch.id}>
              <div className="p-4">
                {/* Header */}
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {dispatch.dispatch_number}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {new Date(dispatch.dispatch_date).toLocaleDateString('ko-KR')}
                    </p>
                  </div>
                  <div>
                    {getStatusBadge(dispatch.status)}
                  </div>
                </div>

                {/* Info */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <Truck size={16} className="mr-2" />
                    {dispatch.vehicle_plate}
                  </div>
                  {dispatch.estimated_arrival && (
                    <div className="flex items-center text-sm text-gray-600">
                      <Clock size={16} className="mr-2" />
                      도착 예정: {new Date(dispatch.estimated_arrival).toLocaleTimeString('ko-KR', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  )}
                </div>

                {/* Document Upload Buttons */}
                {dispatch.status !== '완료' && dispatch.status !== '취소' && (
                  <div className="border-t border-gray-200 pt-4">
                    <p className="text-sm font-medium text-gray-700 mb-3">📄 서류 업로드</p>
                    <div className="flex gap-3">
                      <button
                        onClick={() => openUploadModal(dispatch, 'departure')}
                        className="flex-1 px-4 py-3 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg flex items-center justify-center text-sm font-medium text-blue-700"
                      >
                        <Upload size={16} className="mr-2" />
                        출발 시 서류
                      </button>
                      <button
                        onClick={() => openUploadModal(dispatch, 'arrival')}
                        className="flex-1 px-4 py-3 bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg flex items-center justify-center text-sm font-medium text-green-700"
                      >
                        <CheckCircle size={16} className="mr-2" />
                        도착 시 서류
                      </button>
                    </div>
                  </div>
                )}

                {/* Tracking Info */}
                {dispatch.tracking_number && (
                  <div className="mt-4 bg-gray-50 border border-gray-200 rounded-lg p-3">
                    <p className="text-xs text-gray-600 mb-1">추적 번호</p>
                    <p className="text-sm font-mono text-gray-900">{dispatch.tracking_number}</p>
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Upload Modal */}
      {showUploadModal && selectedDispatch && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setShowUploadModal(false)}>
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {uploadStage === 'departure' ? '📤 출발 시 서류 업로드' : '📥 도착 시 서류 업로드'}
                </h2>
                <p className="text-sm text-gray-600 mt-1">{selectedDispatch.dispatch_number}</p>
              </div>
              <button
                onClick={() => setShowUploadModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-4">
              {/* Transaction Statement */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <FileText size={20} className="mr-2 text-blue-600" />
                    <span className="font-medium text-gray-900">거래명세표</span>
                  </div>
                  {isDocumentUploaded('transaction_statement', uploadStage) ? (
                    <CheckCircle size={20} className="text-green-600" />
                  ) : (
                    <AlertCircle size={20} className="text-gray-400" />
                  )}
                </div>
                <input
                  type="file"
                  accept="image/*,application/pdf"
                  capture="environment"
                  onChange={(e) => handleFileSelect('transaction_statement', e)}
                  disabled={uploadingFiles[`${uploadStage}_transaction_statement`]}
                  className="hidden"
                  id="transaction-upload"
                />
                <label
                  htmlFor="transaction-upload"
                  className={`block w-full px-4 py-3 border-2 border-dashed rounded-lg text-center cursor-pointer ${
                    uploadingFiles[`${uploadStage}_transaction_statement`]
                      ? 'border-gray-300 bg-gray-50 cursor-wait'
                      : isDocumentUploaded('transaction_statement', uploadStage)
                      ? 'border-green-300 bg-green-50 hover:bg-green-100'
                      : 'border-blue-300 bg-blue-50 hover:bg-blue-100'
                  }`}
                >
                  {uploadingFiles[`${uploadStage}_transaction_statement`] ? (
                    <span className="text-gray-600">업로드 중...</span>
                  ) : isDocumentUploaded('transaction_statement', uploadStage) ? (
                    <>
                      <Camera size={24} className="mx-auto mb-2 text-green-600" />
                      <span className="text-green-700 font-medium">✓ 업로드 완료 (재업로드)</span>
                    </>
                  ) : (
                    <>
                      <Camera size={24} className="mx-auto mb-2 text-blue-600" />
                      <span className="text-blue-700 font-medium">사진 촬영 또는 파일 선택</span>
                    </>
                  )}
                </label>
              </div>

              {/* Temperature Record */}
              <div className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <Thermometer size={20} className="mr-2 text-orange-600" />
                    <span className="font-medium text-gray-900">온도기록지</span>
                  </div>
                  {isDocumentUploaded('temperature_record', uploadStage) ? (
                    <CheckCircle size={20} className="text-green-600" />
                  ) : (
                    <AlertCircle size={20} className="text-gray-400" />
                  )}
                </div>
                <input
                  type="file"
                  accept="image/*,application/pdf"
                  capture="environment"
                  onChange={(e) => handleFileSelect('temperature_record', e)}
                  disabled={uploadingFiles[`${uploadStage}_temperature_record`]}
                  className="hidden"
                  id="temperature-upload"
                />
                <label
                  htmlFor="temperature-upload"
                  className={`block w-full px-4 py-3 border-2 border-dashed rounded-lg text-center cursor-pointer ${
                    uploadingFiles[`${uploadStage}_temperature_record`]
                      ? 'border-gray-300 bg-gray-50 cursor-wait'
                      : isDocumentUploaded('temperature_record', uploadStage)
                      ? 'border-green-300 bg-green-50 hover:bg-green-100'
                      : 'border-orange-300 bg-orange-50 hover:bg-orange-100'
                  }`}
                >
                  {uploadingFiles[`${uploadStage}_temperature_record`] ? (
                    <span className="text-gray-600">업로드 중...</span>
                  ) : isDocumentUploaded('temperature_record', uploadStage) ? (
                    <>
                      <Camera size={24} className="mx-auto mb-2 text-green-600" />
                      <span className="text-green-700 font-medium">✓ 업로드 완료 (재업로드)</span>
                    </>
                  ) : (
                    <>
                      <Camera size={24} className="mx-auto mb-2 text-orange-600" />
                      <span className="text-orange-700 font-medium">사진 촬영 또는 파일 선택</span>
                    </>
                  )}
                </label>
              </div>

              {/* Signature (Arrival only) */}
              {uploadStage === 'arrival' && (
                <div className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <FileSignature size={20} className="mr-2 text-purple-600" />
                      <span className="font-medium text-gray-900">서명</span>
                    </div>
                    {isDocumentUploaded('signature', uploadStage) ? (
                      <CheckCircle size={20} className="text-green-600" />
                    ) : (
                      <AlertCircle size={20} className="text-gray-400" />
                    )}
                  </div>
                  <input
                    type="file"
                    accept="image/*,application/pdf"
                    capture="environment"
                    onChange={(e) => handleFileSelect('signature', e)}
                    disabled={uploadingFiles[`${uploadStage}_signature`]}
                    className="hidden"
                    id="signature-upload"
                  />
                  <label
                    htmlFor="signature-upload"
                    className={`block w-full px-4 py-3 border-2 border-dashed rounded-lg text-center cursor-pointer ${
                      uploadingFiles[`${uploadStage}_signature`]
                        ? 'border-gray-300 bg-gray-50 cursor-wait'
                        : isDocumentUploaded('signature', uploadStage)
                        ? 'border-green-300 bg-green-50 hover:bg-green-100'
                        : 'border-purple-300 bg-purple-50 hover:bg-purple-100'
                    }`}
                  >
                    {uploadingFiles[`${uploadStage}_signature`] ? (
                      <span className="text-gray-600">업로드 중...</span>
                    ) : isDocumentUploaded('signature', uploadStage) ? (
                      <>
                        <Camera size={24} className="mx-auto mb-2 text-green-600" />
                        <span className="text-green-700 font-medium">✓ 업로드 완료 (재업로드)</span>
                      </>
                    ) : (
                      <>
                        <Camera size={24} className="mx-auto mb-2 text-purple-600" />
                        <span className="text-purple-700 font-medium">사진 촬영 또는 파일 선택</span>
                      </>
                    )}
                  </label>
                </div>
              )}

              {/* Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start">
                <AlertCircle className="text-blue-600 mr-3 flex-shrink-0 mt-0.5" size={20} />
                <div className="text-sm text-blue-800">
                  <p className="font-medium mb-1">업로드 안내</p>
                  <ul className="list-disc list-inside space-y-1 text-blue-700">
                    <li>JPG, PNG, PDF 파일만 업로드 가능합니다</li>
                    <li>파일 크기는 10MB 이하로 제한됩니다</li>
                    <li>모바일에서는 카메라로 직접 촬영할 수 있습니다</li>
                    <li>업로드한 서류는 고객사에서 다운로드할 수 있습니다</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
              <button
                onClick={() => setShowUploadModal(false)}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg"
              >
                닫기
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DriverDispatchesPage;
