/**
 * IoT 센서 API 서비스
 * HTTP 수집기(포트 8001)와 통신
 */

import axios from 'axios';

// IoT 센서 API 기본 URL (포트 8001)
const IOT_API_BASE_URL = import.meta.env.VITE_IOT_API_URL || 'http://localhost:8001';

const iotApi = axios.create({
  baseURL: IOT_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 센서 데이터 타입 정의
export interface SensorData {
  vehicle_id: string;
  sensor_id: string;
  temperature: number;
  timestamp: string;
  status: 'normal' | 'warning' | 'critical';
  battery_level?: number;
  humidity?: number;
  alert_level?: string;
  messages?: string[];
}

export interface SensorStatistics {
  total: number;
  normal: number;
  warning: number;
  critical: number;
  offline?: number;
}

export interface Alert {
  id: string;
  vehicle_id: string;
  sensor_id: string;
  alert_level: 'INFO' | 'WARNING' | 'CRITICAL';
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

export interface SensorHistory {
  timestamp: string;
  temperature: number;
  humidity?: number;
  battery_level?: number;
  status: string;
}

export interface VehicleSensorDetail {
  vehicle_id: string;
  sensor_id: string;
  current_temperature: number;
  current_status: string;
  battery_level?: number;
  last_update: string;
  history: SensorHistory[];
  alerts: Alert[];
}

/**
 * 센서 데이터 목록 조회 (최신 데이터)
 */
export const getSensorData = async (): Promise<SensorData[]> => {
  try {
    const response = await iotApi.get('/api/v1/sensors/latest');
    return response.data;
  } catch (error) {
    console.error('센서 데이터 조회 실패:', error);
    // 백엔드가 아직 준비되지 않았을 경우 더미 데이터 반환
    return [
      {
        vehicle_id: 'V001',
        sensor_id: 'TEMP001',
        temperature: -19.5,
        timestamp: new Date().toISOString(),
        status: 'normal',
        battery_level: 85,
        humidity: 45,
      },
      {
        vehicle_id: 'V002',
        sensor_id: 'TEMP002',
        temperature: -26.8,
        timestamp: new Date().toISOString(),
        status: 'warning',
        battery_level: 72,
        humidity: 48,
        alert_level: 'WARNING',
        messages: ['온도 경고: -26.8°C (정상 범위: -25.0~-18.0°C)'],
      },
      {
        vehicle_id: 'V003',
        sensor_id: 'TEMP003',
        temperature: -9.5,
        timestamp: new Date().toISOString(),
        status: 'critical',
        battery_level: 45,
        humidity: 52,
        alert_level: 'CRITICAL',
        messages: ['온도 위험: -9.5°C (정상 범위: -25.0~-18.0°C)'],
      },
    ];
  }
};

/**
 * 센서 통계 조회
 */
export const getSensorStatistics = async (): Promise<SensorStatistics> => {
  try {
    const response = await iotApi.get('/api/v1/sensors/statistics');
    return response.data;
  } catch (error) {
    console.error('센서 통계 조회 실패:', error);
    // 더미 데이터
    return {
      total: 3,
      normal: 1,
      warning: 1,
      critical: 1,
      offline: 0,
    };
  }
};

/**
 * 차량별 센서 상세 정보 조회
 */
export const getVehicleSensorDetail = async (vehicleId: string): Promise<VehicleSensorDetail> => {
  try {
    const response = await iotApi.get(`/api/v1/sensors/vehicle/${vehicleId}`);
    return response.data;
  } catch (error) {
    console.error('차량 센서 상세 조회 실패:', error);
    // 더미 데이터
    const now = new Date();
    const history: SensorHistory[] = [];
    
    // 최근 24시간 데이터 생성 (1시간 간격)
    for (let i = 24; i >= 0; i--) {
      const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000);
      history.push({
        timestamp: timestamp.toISOString(),
        temperature: -20 + Math.random() * 10 - 5,
        humidity: 45 + Math.random() * 10,
        battery_level: 80 - i * 2,
        status: i > 20 ? 'normal' : i > 10 ? 'warning' : 'critical',
      });
    }

    return {
      vehicle_id: vehicleId,
      sensor_id: `TEMP${vehicleId.substring(1)}`,
      current_temperature: -19.5,
      current_status: 'normal',
      battery_level: 85,
      last_update: now.toISOString(),
      history,
      alerts: [
        {
          id: '1',
          vehicle_id: vehicleId,
          sensor_id: `TEMP${vehicleId.substring(1)}`,
          alert_level: 'WARNING',
          message: '온도 경고: -26.8°C',
          timestamp: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(),
          acknowledged: false,
        },
      ],
    };
  }
};

/**
 * 알림 목록 조회
 */
export const getAlerts = async (limit = 100): Promise<Alert[]> => {
  try {
    const response = await iotApi.get(`/api/v1/alerts?limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('알림 조회 실패:', error);
    // 더미 데이터
    const now = new Date();
    return [
      {
        id: '1',
        vehicle_id: 'V002',
        sensor_id: 'TEMP002',
        alert_level: 'WARNING',
        message: '온도 경고: -26.8°C (정상 범위: -25.0~-18.0°C)',
        timestamp: new Date(now.getTime() - 10 * 60 * 1000).toISOString(),
        acknowledged: false,
      },
      {
        id: '2',
        vehicle_id: 'V003',
        sensor_id: 'TEMP003',
        alert_level: 'CRITICAL',
        message: '온도 위험: -9.5°C (정상 범위: -25.0~-18.0°C)',
        timestamp: new Date(now.getTime() - 5 * 60 * 1000).toISOString(),
        acknowledged: false,
      },
      {
        id: '3',
        vehicle_id: 'V003',
        sensor_id: 'TEMP003',
        alert_level: 'WARNING',
        message: '배터리 부족: 45%',
        timestamp: new Date(now.getTime() - 30 * 60 * 1000).toISOString(),
        acknowledged: true,
      },
    ];
  }
};

/**
 * 알림 확인 처리
 */
export const acknowledgeAlert = async (alertId: string): Promise<void> => {
  try {
    await iotApi.post(`/api/v1/alerts/${alertId}/acknowledge`);
  } catch (error) {
    console.error('알림 확인 처리 실패:', error);
    throw error;
  }
};

/**
 * 헬스체크
 */
export const checkHealth = async (): Promise<{ status: string; timestamp: string }> => {
  try {
    const response = await iotApi.get('/health');
    return response.data;
  } catch (error) {
    console.error('헬스체크 실패:', error);
    return {
      status: 'offline',
      timestamp: new Date().toISOString(),
    };
  }
};

export default {
  getSensorData,
  getSensorStatistics,
  getVehicleSensorDetail,
  getAlerts,
  acknowledgeAlert,
  checkHealth,
};
