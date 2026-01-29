// API Configuration
export const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api/v1' 
  : 'https://api.coldchain.example.com/api/v1';

export const API_TIMEOUT = 30000; // 30 seconds

// WebSocket Configuration
export const WS_BASE_URL = __DEV__
  ? 'ws://localhost:8000/ws'
  : 'wss://api.coldchain.example.com/ws';

// Colors
export const Colors = {
  primary: '#2563EB',
  primaryDark: '#1E40AF',
  primaryLight: '#60A5FA',
  
  secondary: '#10B981',
  secondaryDark: '#059669',
  secondaryLight: '#34D399',
  
  danger: '#EF4444',
  dangerDark: '#DC2626',
  dangerLight: '#F87171',
  
  warning: '#F59E0B',
  warningDark: '#D97706',
  warningLight: '#FBBF24',
  
  info: '#3B82F6',
  infoDark: '#2563EB',
  infoLight: '#60A5FA',
  
  success: '#10B981',
  successDark: '#059669',
  successLight: '#34D399',
  
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
  
  white: '#FFFFFF',
  black: '#000000',
  
  background: '#F9FAFB',
  surface: '#FFFFFF',
  border: '#E5E7EB',
  
  text: {
    primary: '#111827',
    secondary: '#6B7280',
    disabled: '#9CA3AF',
    inverse: '#FFFFFF',
  },
};

// Fonts
export const Fonts = {
  regular: 'System',
  medium: 'System',
  semibold: 'System',
  bold: 'System',
};

// Font Sizes
export const FontSizes = {
  xs: 12,
  sm: 14,
  md: 16,
  lg: 18,
  xl: 20,
  '2xl': 24,
  '3xl': 30,
  '4xl': 36,
};

// Spacing
export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  '2xl': 40,
  '3xl': 48,
};

// Border Radius
export const BorderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
};

// Shadows
export const Shadows = {
  sm: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  md: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 4,
  },
  lg: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.15,
    shadowRadius: 8,
    elevation: 8,
  },
};

// Status Colors
export const StatusColors = {
  dispatch: {
    pending: Colors.warning,
    assigned: Colors.info,
    in_progress: Colors.primary,
    completed: Colors.success,
    cancelled: Colors.gray[400],
  },
  vehicle: {
    available: Colors.success,
    in_use: Colors.primary,
    maintenance: Colors.warning,
    out_of_service: Colors.danger,
  },
  driver: {
    available: Colors.success,
    on_duty: Colors.primary,
    off_duty: Colors.gray[400],
    on_leave: Colors.warning,
  },
  order: {
    pending: Colors.warning,
    confirmed: Colors.info,
    dispatched: Colors.primary,
    delivered: Colors.success,
    cancelled: Colors.gray[400],
  },
  alert: {
    low: Colors.info,
    medium: Colors.warning,
    high: Colors.danger,
    critical: Colors.dangerDark,
  },
};

// Status Labels
export const StatusLabels = {
  dispatch: {
    pending: '대기',
    assigned: '배정됨',
    in_progress: '진행중',
    completed: '완료',
    cancelled: '취소됨',
  },
  vehicle: {
    available: '사용 가능',
    in_use: '사용중',
    maintenance: '정비중',
    out_of_service: '서비스 불가',
  },
  driver: {
    available: '대기중',
    on_duty: '근무중',
    off_duty: '비근무',
    on_leave: '휴가중',
  },
  order: {
    pending: '대기',
    confirmed: '확인됨',
    dispatched: '배차됨',
    delivered: '배송완료',
    cancelled: '취소됨',
  },
  alert: {
    low: '낮음',
    medium: '보통',
    high: '높음',
    critical: '심각',
  },
};

// Vehicle Types
export const VehicleTypeLabels = {
  refrigerated_truck: '냉장 트럭',
  freezer_truck: '냉동 트럭',
  dry_van: '드라이 밴',
  reefer_trailer: '냉동 트레일러',
};

// Alert Types
export const AlertTypeLabels = {
  temperature: '온도 경고',
  delay: '지연 경고',
  maintenance: '정비 필요',
  fuel: '연료 부족',
  accident: '사고',
  other: '기타',
};

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const MAX_PAGE_SIZE = 100;

// Refresh Intervals
export const REFRESH_INTERVALS = {
  DASHBOARD: 30000, // 30 seconds
  VEHICLE_TRACKING: 10000, // 10 seconds
  TEMPERATURE: 30000, // 30 seconds
  ALERTS: 60000, // 1 minute
};

// Temperature Thresholds
export const TEMPERATURE_THRESHOLDS = {
  CRITICAL_LOW: -25,
  WARNING_LOW: -20,
  NORMAL_MIN: -18,
  NORMAL_MAX: 5,
  WARNING_HIGH: 8,
  CRITICAL_HIGH: 10,
};

// Map Configuration
export const MAP_CONFIG = {
  DEFAULT_LATITUDE: 37.5665,
  DEFAULT_LONGITUDE: 126.9780,
  DEFAULT_ZOOM: 13,
  MARKER_COLORS: {
    vehicle: Colors.primary,
    pickup: Colors.success,
    delivery: Colors.danger,
    warehouse: Colors.info,
  },
};

// Date Formats
export const DATE_FORMATS = {
  DATE: 'YYYY-MM-DD',
  TIME: 'HH:mm',
  DATETIME: 'YYYY-MM-DD HH:mm',
  DATETIME_FULL: 'YYYY-MM-DD HH:mm:ss',
  DISPLAY_DATE: 'YYYY년 MM월 DD일',
  DISPLAY_DATETIME: 'YYYY년 MM월 DD일 HH:mm',
};

// Error Messages
export const ErrorMessages = {
  NETWORK_ERROR: '네트워크 연결을 확인해주세요',
  UNAUTHORIZED: '로그인이 필요합니다',
  FORBIDDEN: '접근 권한이 없습니다',
  NOT_FOUND: '요청한 데이터를 찾을 수 없습니다',
  SERVER_ERROR: '서버 오류가 발생했습니다',
  TIMEOUT: '요청 시간이 초과되었습니다',
  UNKNOWN: '알 수 없는 오류가 발생했습니다',
};
