/**
 * Centralized API Configuration
 * 모든 API 호출에 대한 중앙 집중식 설정
 */

/**
 * API Base URLs
 */
export const API_CONFIG = {
  // Main Backend API
  BASE_URL: import.meta.env.VITE_API_URL || '/api/v1',
  
  // Billing Enhanced Module
  BILLING_URL: '/api/v1/billing/enhanced',
  
  // IoT Sensor API (별도 서버)
  IOT_URL: import.meta.env.VITE_IOT_API_URL || 'http://localhost:8001',
  
  // WebSocket URL
  WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
  
  // Request timeout (ms)
  TIMEOUT: 30000,
  
  // Retry configuration
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
} as const;

/**
 * API Endpoints
 */
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    REGISTER: '/auth/register',
  },
  
  // Orders
  ORDERS: {
    LIST: '/orders',
    DETAIL: (id: number) => `/orders/${id}`,
    CREATE: '/orders',
    UPDATE: (id: number) => `/orders/${id}`,
    DELETE: (id: number) => `/orders/${id}`,
  },
  
  // Dispatches
  DISPATCHES: {
    LIST: '/dispatches',
    DETAIL: (id: number) => `/dispatches/${id}`,
    AUTO: '/dispatches/auto',
    MANUAL: '/dispatches/manual',
    OPTIMIZE_CVRPTW: '/dispatches/optimize-cvrptw',
    STATUS: (id: number) => `/dispatches/${id}/status`,
    CONFIRM: '/dispatches/confirm',
    STATS: '/dispatches/stats/summary',
  },
  
  // Vehicles
  VEHICLES: {
    LIST: '/vehicles',
    AVAILABLE: '/vehicles/available',
    DETAIL: (id: number) => `/vehicles/${id}`,
    CREATE: '/vehicles',
    UPDATE: (id: number) => `/vehicles/${id}`,
  },
  
  // Clients
  CLIENTS: {
    LIST: '/clients',
    DETAIL: (id: number) => `/clients/${id}`,
    CREATE: '/clients',
    UPDATE: (id: number) => `/clients/${id}`,
    DELETE: (id: number) => `/clients/${id}`,
  },
  
  // Delivery Tracking
  DELIVERY_TRACKING: {
    PUBLIC: (trackingNumber: string) => `/delivery-tracking/public/${trackingNumber}`,
    GENERATE: '/delivery-tracking/generate',
    STATUS: '/delivery-tracking/status',
    TIMELINE: '/delivery-tracking/timeline',
    ROUTE: '/delivery-tracking/route',
    NOTIFY: '/delivery-tracking/notify',
    ESTIMATED_ARRIVAL: '/delivery-tracking/estimated-arrival',
  },
  
  // Traffic Service
  TRAFFIC: {
    ROUTE: '/traffic/route',
    ROUTE_SIMPLE: '/traffic/route/simple',
    ARRIVAL_ESTIMATE: '/traffic/arrival-estimate/simple',
    TEST: '/traffic/test',
    COMPARE: '/traffic/compare',
  },
  
  // Billing Enhanced
  BILLING: {
    PREVIEW: '/preview',
    DASHBOARD_FINANCIAL: '/dashboard/financial',
    DASHBOARD_TRENDS: '/dashboard/trends',
    DASHBOARD_TOP_CLIENTS: '/dashboard/top-clients',
    AUTO_SCHEDULE: '/auto-schedule',
    AUTO_SCHEDULE_DETAIL: (clientId: number) => `/auto-schedule/${clientId}`,
    AUTO_SCHEDULE_EXECUTE: '/auto-schedule/execute-due',
    SETTLEMENT_APPROVAL: '/settlement-approval',
    SETTLEMENT_APPROVAL_DETAIL: (id: number) => `/settlement-approval/${id}`,
    SETTLEMENT_APPROVAL_HISTORY: (id: number) => `/settlement-approval/${id}/history`,
    PAYMENT_REMINDER: '/payment-reminder',
    PAYMENT_REMINDER_SEND: '/payment-reminder/send-due',
    STATISTICS_BILLING: '/statistics/billing',
    STATISTICS_SETTLEMENT: '/statistics/settlement',
    EXPORT: '/export',
    EXPORT_TASK: (taskId: string) => `/export/${taskId}`,
  },
  
  // Monitoring
  MONITORING: {
    HEALTH: '/monitoring/health',
    METRICS: '/monitoring/metrics',
    DASHBOARD: '/monitoring/dashboard',
  },
  
  // Cache
  CACHE: {
    STATS: '/cache/stats',
    INVALIDATE: (type: string, id: string) => `/cache/invalidate/${type}/${id}`,
  },
  
  // AI Chat
  AI_CHAT: {
    PROCESS: '/ai-chat/process',
    HISTORY: '/ai-chat/history',
    HISTORY_DELETE: (historyId: number) => `/ai-chat/history/${historyId}`,
    HISTORY_STATS: '/ai-chat/history/stats',
  },
  
  // AI Usage & Cost
  AI_USAGE: {
    STATS: '/ai-usage/stats',
    LOGS: '/ai-usage/logs',
    COST_SUMMARY: '/ai-usage/cost-summary',
  },
  
  // Analytics
  ANALYTICS: {
    OVERVIEW: '/analytics/overview',
    DISPATCH_EFFICIENCY: '/analytics/dispatch-efficiency',
    VEHICLE_UTILIZATION: '/analytics/vehicle-utilization',
    CLIENT_INSIGHTS: '/analytics/client-insights',
    COST_ANALYSIS: '/analytics/cost-analysis',
  },
} as const;

/**
 * Helper function to build full URL
 */
export const buildUrl = (baseUrl: string, endpoint: string): string => {
  return `${baseUrl}${endpoint}`;
};

/**
 * Helper function to get auth headers
 */
export const getAuthHeaders = (): Record<string, string> => {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

/**
 * Environment check
 */
export const isDevelopment = import.meta.env.DEV;
export const isProduction = import.meta.env.PROD;

/**
 * Debug logging (only in development)
 */
export const apiLog = (message: string, ...args: any[]) => {
  if (isDevelopment) {
    console.log(`[API] ${message}`, ...args);
  }
};

export const apiError = (message: string, ...args: any[]) => {
  if (isDevelopment) {
    console.error(`[API Error] ${message}`, ...args);
  }
};
