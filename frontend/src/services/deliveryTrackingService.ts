/**
 * 배송 추적 서비스
 * 
 * 고객용 배송 추적 시스템 API 호출
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';
const API_PREFIX = '/delivery-tracking';

export interface PublicTrackingInfo {
  tracking_number: string;
  order_number: string;
  status: {
    status: string;
    status_description: string;
    dispatch_number?: string;
    dispatch_date?: string;
    vehicle_number?: string;
    driver_name?: string;
    driver_phone?: string;
    estimated_delivery_date?: string;
    current_location?: {
      latitude: number;
      longitude: number;
      address: string;
      recorded_at: string;
    };
    progress_percentage: number;
  };
  timeline: Array<{
    timestamp?: string;
    event_type: string;
    title: string;
    description: string;
    status: string;
  }>;
  estimated_arrival?: string;
  pickup_address?: string;
  delivery_address?: string;
  temperature_zone: string;
  pallet_count: number;
}

export interface TrackingNumberCreate {
  order_id?: number;
  order_number?: string;
}

export interface TrackingNumberResponse {
  tracking_number: string;
  order_id: number;
  order_number: string;
  message: string;
}

export interface DeliveryStatus {
  status: string;
  status_description: string;
  dispatch_number?: string;
  dispatch_date?: string;
  vehicle_number?: string;
  driver_name?: string;
  driver_phone?: string;
  estimated_delivery_date?: string;
  current_location?: {
    latitude: number;
    longitude: number;
    address: string;
    recorded_at: string;
  };
  progress_percentage: number;
}

export interface TimelineEvent {
  timestamp?: string;
  event_type: string;
  title: string;
  description: string;
  status: string;
}

export interface DeliveryTimeline {
  order_id: number;
  order_number: string;
  timeline: TimelineEvent[];
}

export interface RoutePoint {
  sequence: number;
  route_type: string;
  location_name: string;
  address: string;
  latitude: number;
  longitude: number;
  estimated_arrival?: string;
  is_current_order: boolean;
  current_pallets: number;
  current_weight: number;
}

export interface RouteDetails {
  dispatch_number: string;
  dispatch_date: string;
  vehicle: {
    vehicle_number?: string;
    vehicle_type?: string;
    temperature_zone?: string;
  };
  driver: {
    name?: string;
    phone?: string;
  };
  routes: RoutePoint[];
  total_distance?: number;
  estimated_duration?: number;
}

export interface NotificationRequest {
  order_id: number;
  notification_type: string;
  recipient: string;
  channel: string;
}

export interface NotificationResponse {
  success: boolean;
  message: string;
  notification_type: string;
  channel: string;
  recipient: string;
}

export interface EstimatedArrival {
  order_id: number;
  order_number: string;
  estimated_arrival_time: string;
  message: string;
}

class DeliveryTrackingService {
  /**
   * 공개 배송 추적
   * @param trackingNumber 추적번호
   * @returns 공개 추적 정보
   */
  async getPublicTracking(trackingNumber: string): Promise<PublicTrackingInfo> {
    const response = await axios.get(`${API_BASE_URL}${API_PREFIX}/public/${trackingNumber}`);
    return response.data;
  }

  /**
   * 추적번호 생성
   * @param data 추적번호 생성 요청
   * @returns 추적번호 응답
   */
  async generateTrackingNumber(data: TrackingNumberCreate): Promise<TrackingNumberResponse> {
    const response = await axios.post(`${API_BASE_URL}${API_PREFIX}/generate`, data);
    return response.data;
  }

  /**
   * 배송 상태 조회
   * @param orderId 주문 ID (선택)
   * @param orderNumber 주문번호 (선택)
   * @returns 배송 상태
   */
  async getDeliveryStatus(orderId?: number, orderNumber?: string): Promise<DeliveryStatus> {
    const params: any = {};
    if (orderId) params.order_id = orderId;
    if (orderNumber) params.order_number = orderNumber;

    const response = await axios.get(`${API_BASE_URL}${API_PREFIX}/status`, { params });
    return response.data;
  }

  /**
   * 배송 타임라인 조회
   * @param orderId 주문 ID (선택)
   * @param orderNumber 주문번호 (선택)
   * @returns 배송 타임라인
   */
  async getDeliveryTimeline(orderId?: number, orderNumber?: string): Promise<DeliveryTimeline> {
    const params: any = {};
    if (orderId) params.order_id = orderId;
    if (orderNumber) params.order_number = orderNumber;

    const response = await axios.get(`${API_BASE_URL}${API_PREFIX}/timeline`, { params });
    return response.data;
  }

  /**
   * 배송 경로 조회
   * @param orderId 주문 ID (선택)
   * @param orderNumber 주문번호 (선택)
   * @returns 배송 경로 상세
   */
  async getRouteDetails(orderId?: number, orderNumber?: string): Promise<RouteDetails> {
    const params: any = {};
    if (orderId) params.order_id = orderId;
    if (orderNumber) params.order_number = orderNumber;

    const response = await axios.get(`${API_BASE_URL}${API_PREFIX}/route`, { params });
    return response.data;
  }

  /**
   * 알림 전송
   * @param request 알림 요청
   * @returns 알림 응답
   */
  async sendNotification(request: NotificationRequest): Promise<NotificationResponse> {
    const response = await axios.post(`${API_BASE_URL}${API_PREFIX}/notify`, request);
    return response.data;
  }

  /**
   * 예상 도착 시간 조회
   * @param orderId 주문 ID (선택)
   * @param orderNumber 주문번호 (선택)
   * @returns 예상 도착 시간
   */
  async getEstimatedArrival(orderId?: number, orderNumber?: string): Promise<EstimatedArrival> {
    const params: any = {};
    if (orderId) params.order_id = orderId;
    if (orderNumber) params.order_number = orderNumber;

    const response = await axios.get(`${API_BASE_URL}${API_PREFIX}/estimated-arrival`, { params });
    return response.data;
  }
}

export default new DeliveryTrackingService();
