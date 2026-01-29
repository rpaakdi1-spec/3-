/**
 * 공개 배송 추적 페이지
 * 
 * 고객이 추적번호를 입력하여 배송 상태를 조회할 수 있는 페이지
 * - 인증 불필요
 * - 추적번호만으로 조회 가능
 * - 실시간 배송 상태 및 타임라인 표시
 * - 지도로 현재 위치 표시
 */

import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import deliveryTrackingService, { PublicTrackingInfo } from '../../services/deliveryTrackingService';
import './PublicTracking.css';

const PublicTracking: React.FC = () => {
  const [trackingNumber, setTrackingNumber] = useState('');
  const [trackingInfo, setTrackingInfo] = useState<PublicTrackingInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!trackingNumber.trim()) {
      setError('추적번호를 입력해주세요');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await deliveryTrackingService.getPublicTracking(trackingNumber);
      setTrackingInfo(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || '추적 정보를 찾을 수 없습니다');
      setTrackingInfo(null);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case '배차대기':
        return 'warning';
      case '배차완료':
        return 'info';
      case '운송중':
        return 'primary';
      case '배송완료':
        return 'success';
      case '취소':
        return 'danger';
      default:
        return 'secondary';
    }
  };

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case 'ORDER_CREATED':
        return '📝';
      case 'DISPATCH_ASSIGNED':
        return '🚚';
      case 'PICKUP_SCHEDULED':
        return '📦';
      case 'IN_TRANSIT':
        return '🚛';
      case 'DELIVERY_SCHEDULED':
        return '📍';
      case 'DELIVERED':
        return '✅';
      default:
        return '📌';
    }
  };

  const getEventStatusClass = (status: string) => {
    switch (status) {
      case 'completed':
        return 'event-completed';
      case 'in_progress':
        return 'event-in-progress';
      case 'pending':
        return 'event-pending';
      default:
        return 'event-unknown';
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR');
  };

  return (
    <div className="public-tracking">
      <div className="tracking-header">
        <h1>배송 추적</h1>
        <p>추적번호를 입력하여 배송 상태를 확인하세요</p>
      </div>

      <div className="tracking-search">
        <input
          type="text"
          className="tracking-input"
          placeholder="추적번호 입력 (예: TRK-20260127-A3F5B2C1)"
          value={trackingNumber}
          onChange={(e) => setTrackingNumber(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button
          className="tracking-button"
          onClick={handleSearch}
          disabled={loading}
        >
          {loading ? '조회 중...' : '조회'}
        </button>
      </div>

      {error && (
        <div className="tracking-error">
          <span className="error-icon">⚠️</span>
          {error}
        </div>
      )}

      {trackingInfo && (
        <div className="tracking-results">
          {/* 배송 상태 카드 */}
          <div className="status-card">
            <div className="status-header">
              <h2>배송 상태</h2>
              <span className={`status-badge status-${getStatusColor(trackingInfo.status.status)}`}>
                {trackingInfo.status.status}
              </span>
            </div>
            <div className="status-content">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${trackingInfo.status.progress_percentage}%` }}
                />
                <span className="progress-text">{trackingInfo.status.progress_percentage}%</span>
              </div>
              <p className="status-description">{trackingInfo.status.status_description}</p>

              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">추적번호</span>
                  <span className="info-value">{trackingInfo.tracking_number}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">주문번호</span>
                  <span className="info-value">{trackingInfo.order_number}</span>
                </div>
                {trackingInfo.status.dispatch_number && (
                  <div className="info-item">
                    <span className="info-label">배차번호</span>
                    <span className="info-value">{trackingInfo.status.dispatch_number}</span>
                  </div>
                )}
                {trackingInfo.status.vehicle_number && (
                  <div className="info-item">
                    <span className="info-label">차량번호</span>
                    <span className="info-value">{trackingInfo.status.vehicle_number}</span>
                  </div>
                )}
                {trackingInfo.status.driver_name && (
                  <div className="info-item">
                    <span className="info-label">기사명</span>
                    <span className="info-value">{trackingInfo.status.driver_name}</span>
                  </div>
                )}
                {trackingInfo.status.driver_phone && (
                  <div className="info-item">
                    <span className="info-label">연락처</span>
                    <span className="info-value">{trackingInfo.status.driver_phone}</span>
                  </div>
                )}
                <div className="info-item">
                  <span className="info-label">온도대</span>
                  <span className="info-value">{trackingInfo.temperature_zone}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">팔레트 수</span>
                  <span className="info-value">{trackingInfo.pallet_count}개</span>
                </div>
              </div>
            </div>
          </div>

          {/* 배송 타임라인 */}
          <div className="timeline-card">
            <h2>배송 진행 상황</h2>
            <div className="timeline">
              {trackingInfo.timeline.map((event, index) => (
                <div key={index} className={`timeline-item ${getEventStatusClass(event.status)}`}>
                  <div className="timeline-marker">
                    <span className="timeline-icon">{getEventIcon(event.event_type)}</span>
                  </div>
                  <div className="timeline-content">
                    <div className="timeline-time">{formatDate(event.timestamp)}</div>
                    <div className="timeline-title">{event.title}</div>
                    <div className="timeline-description">{event.description}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 주소 정보 */}
          <div className="address-card">
            <h2>배송 정보</h2>
            <div className="address-grid">
              <div className="address-item">
                <span className="address-label">🔹 상차지</span>
                <span className="address-value">{trackingInfo.pickup_address || '-'}</span>
              </div>
              <div className="address-item">
                <span className="address-label">🔸 하차지</span>
                <span className="address-value">{trackingInfo.delivery_address || '-'}</span>
              </div>
            </div>
          </div>

          {/* 지도 (현재 위치) */}
          {trackingInfo.status.current_location && (
            <div className="map-card">
              <h2>현재 위치</h2>
              <p className="current-address">{trackingInfo.status.current_location.address}</p>
              <p className="current-time">
                업데이트: {formatDate(trackingInfo.status.current_location.recorded_at)}
              </p>
              <div className="map-container">
                <MapContainer
                  center={[
                    trackingInfo.status.current_location.latitude,
                    trackingInfo.status.current_location.longitude
                  ]}
                  zoom={13}
                  style={{ height: '400px', width: '100%' }}
                >
                  <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                  />
                  <Marker
                    position={[
                      trackingInfo.status.current_location.latitude,
                      trackingInfo.status.current_location.longitude
                    ]}
                  >
                    <Popup>
                      <div>
                        <strong>현재 위치</strong>
                        <br />
                        {trackingInfo.status.current_location.address}
                      </div>
                    </Popup>
                  </Marker>
                </MapContainer>
              </div>
            </div>
          )}

          {/* 예상 도착 시간 */}
          {trackingInfo.estimated_arrival && (
            <div className="arrival-card">
              <h2>예상 도착 시간</h2>
              <div className="arrival-time">
                <span className="arrival-icon">⏱️</span>
                <span className="arrival-value">{formatDate(trackingInfo.estimated_arrival)}</span>
              </div>
              <p className="arrival-note">
                * 교통 상황에 따라 실제 도착 시간이 변경될 수 있습니다
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PublicTracking;
