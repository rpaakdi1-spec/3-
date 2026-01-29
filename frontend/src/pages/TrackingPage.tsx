import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../api/client';
import { TrackingInfo } from '../types';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Package, MapPin, Phone, Clock, CheckCircle2, Truck as TruckIcon } from 'lucide-react';
import { QRCodeSVG } from 'qrcode.react';
import toast from 'react-hot-toast';
import 'leaflet/dist/leaflet.css';

const TrackingPage: React.FC = () => {
  const { trackingNumber } = useParams<{ trackingNumber: string }>();
  const [tracking, setTracking] = useState<TrackingInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (trackingNumber) {
      fetchTrackingInfo();
      const interval = setInterval(fetchTrackingInfo, 15000); // Refresh every 15 seconds
      return () => clearInterval(interval);
    }
  }, [trackingNumber]);

  const fetchTrackingInfo = async () => {
    try {
      const data = await apiClient.getTrackingInfo(trackingNumber!);
      setTracking(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || '배송 정보를 찾을 수 없습니다');
      toast.error('배송 정보를 불러오는데 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const getStatusInfo = (status: string) => {
    const statusMap: Record<string, { label: string; color: string; icon: React.ElementType }> = {
      ASSIGNED: { label: '배차 완료', color: 'text-yellow-600', icon: CheckCircle2 },
      IN_PROGRESS: { label: '배송 중', color: 'text-green-600', icon: TruckIcon },
      PICKUP_COMPLETE: { label: '상차 완료', color: 'text-blue-600', icon: Package },
      DELIVERY_COMPLETE: { label: '배송 완료', color: 'text-purple-600', icon: CheckCircle2 },
      COMPLETED: { label: '완료', color: 'text-gray-600', icon: CheckCircle2 },
    };
    return statusMap[status] || { label: status, color: 'text-gray-600', icon: Package };
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">배송 정보를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error || !tracking) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <Package size={64} className="mx-auto text-gray-300 mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">배송 정보를 찾을 수 없습니다</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <p className="text-sm text-gray-500">추적번호를 다시 확인해주세요</p>
        </div>
      </div>
    );
  }

  const statusInfo = getStatusInfo(tracking.status);
  const StatusIcon = statusInfo.icon;

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-blue-600 text-white py-8">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-center mb-4">
            <TruckIcon size={48} />
          </div>
          <h1 className="text-3xl font-bold text-center">배송 추적</h1>
          <p className="text-center text-blue-100 mt-2">실시간 배송 현황을 확인하세요</p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Tracking Number & Status */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between">
              <div className="mb-4 md:mb-0">
                <p className="text-sm text-gray-600 mb-1">추적번호</p>
                <p className="text-2xl font-bold text-gray-900">{tracking.tracking_number}</p>
                <p className="text-sm text-gray-600 mt-1">주문번호: {tracking.order_number}</p>
              </div>
              <div className="flex items-center space-x-3">
                <StatusIcon className={statusInfo.color} size={32} />
                <div>
                  <p className="text-sm text-gray-600">현재 상태</p>
                  <p className={`text-xl font-bold ${statusInfo.color}`}>{statusInfo.label}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Map */}
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="p-4 bg-gray-50 border-b">
              <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                <MapPin className="mr-2" size={20} />
                현재 위치
              </h2>
            </div>
            <div className="h-96">
              <MapContainer
                center={[tracking.current_location.latitude, tracking.current_location.longitude]}
                zoom={13}
                style={{ height: '100%', width: '100%' }}
              >
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <Marker position={[tracking.current_location.latitude, tracking.current_location.longitude]}>
                  <Popup>
                    <div className="p-2">
                      <p className="font-semibold">{tracking.order_number}</p>
                      <p className="text-sm text-gray-600">{tracking.current_location.address}</p>
                    </div>
                  </Popup>
                </Marker>
              </MapContainer>
            </div>
            <div className="p-4 bg-gray-50 border-t">
              <p className="text-sm text-gray-600">
                <MapPin className="inline mr-1" size={16} />
                {tracking.current_location.address}
              </p>
            </div>
          </div>

          {/* Info Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {tracking.estimated_arrival && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-start">
                  <Clock className="text-blue-600 mr-3 mt-1" size={24} />
                  <div>
                    <p className="text-sm text-gray-600 mb-1">예상 도착 시간</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {new Date(tracking.estimated_arrival).toLocaleString('ko-KR', {
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {tracking.driver_contact && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-start">
                  <Phone className="text-green-600 mr-3 mt-1" size={24} />
                  <div>
                    <p className="text-sm text-gray-600 mb-1">기사 연락처</p>
                    <a
                      href={`tel:${tracking.driver_contact}`}
                      className="text-lg font-semibold text-green-600 hover:text-green-700"
                    >
                      {tracking.driver_contact}
                    </a>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Timeline */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">배송 이력</h2>
            <div className="space-y-4">
              {tracking.history.map((item, index) => (
                <div key={index} className="flex">
                  <div className="flex flex-col items-center mr-4">
                    <div
                      className={`w-3 h-3 rounded-full ${
                        index === 0 ? 'bg-blue-600' : 'bg-gray-300'
                      }`}
                    />
                    {index < tracking.history.length - 1 && (
                      <div className="w-0.5 h-full bg-gray-300 mt-1" />
                    )}
                  </div>
                  <div className="flex-1 pb-4">
                    <p className="font-medium text-gray-900">{getStatusInfo(item.status).label}</p>
                    <p className="text-sm text-gray-600 mt-1">
                      {new Date(item.timestamp).toLocaleString('ko-KR')}
                    </p>
                    {item.notes && <p className="text-sm text-gray-500 mt-1">{item.notes}</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* QR Code */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="text-center">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">QR 코드로 공유하기</h2>
              <div className="inline-block p-4 bg-white border-2 border-gray-200 rounded-lg">
                <QRCodeSVG value={window.location.href} size={200} />
              </div>
              <p className="text-sm text-gray-600 mt-4">
                QR 코드를 스캔하여 배송 정보를 확인할 수 있습니다
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrackingPage;
