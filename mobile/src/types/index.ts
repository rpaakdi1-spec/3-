// API Types
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

export interface ApiError {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}

// User Types
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'dispatcher' | 'driver' | 'customer';
  is_active: boolean;
  phone?: string;
  avatar_url?: string;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Dispatch Types
export interface Dispatch {
  id: number;
  dispatch_number: string;
  status: 'pending' | 'assigned' | 'in_progress' | 'completed' | 'cancelled';
  vehicle_id: number | null;
  driver_id: number | null;
  order_id: number;
  scheduled_pickup_time: string;
  actual_pickup_time: string | null;
  scheduled_delivery_time: string;
  actual_delivery_time: string | null;
  created_at: string;
  updated_at: string;
  vehicle?: Vehicle;
  driver?: Driver;
  order?: Order;
}

// Vehicle Types
export interface Vehicle {
  id: number;
  vehicle_number: string;
  vehicle_plate_number: string;
  vehicle_type: 'refrigerated_truck' | 'freezer_truck' | 'dry_van' | 'reefer_trailer';
  capacity_kg: number;
  status: 'available' | 'in_use' | 'maintenance' | 'out_of_service';
  current_location?: {
    latitude: number;
    longitude: number;
    speed_kmh: number;
    heading: number;
    timestamp: string;
  };
  temperature?: {
    temperature_a: number | null;
    temperature_b: number | null;
    timestamp: string;
  };
  is_active: boolean;
  last_maintenance_date: string | null;
  next_maintenance_date: string | null;
  created_at: string;
  updated_at: string;
}

// Driver Types
export interface Driver {
  id: number;
  driver_name: string;
  driver_license_number: string;
  phone: string;
  email: string | null;
  status: 'available' | 'on_duty' | 'off_duty' | 'on_leave';
  rating: number;
  total_deliveries: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Order Types
export interface Order {
  id: number;
  order_number: string;
  customer_id: number;
  pickup_location: string;
  delivery_location: string;
  pickup_latitude: number;
  pickup_longitude: number;
  delivery_latitude: number;
  delivery_longitude: number;
  status: 'pending' | 'confirmed' | 'dispatched' | 'delivered' | 'cancelled';
  required_temperature_min: number | null;
  required_temperature_max: number | null;
  weight_kg: number;
  special_instructions: string | null;
  created_at: string;
  updated_at: string;
  customer?: Customer;
}

// Customer Types
export interface Customer {
  id: number;
  customer_name: string;
  contact_name: string;
  phone: string;
  email: string | null;
  address: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Alert Types
export interface Alert {
  id: number;
  alert_type: 'temperature' | 'delay' | 'maintenance' | 'fuel' | 'accident' | 'other';
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  entity_type: 'dispatch' | 'vehicle' | 'driver' | 'order';
  entity_id: number;
  is_resolved: boolean;
  resolved_at: string | null;
  created_at: string;
  updated_at: string;
}

// Dashboard Types
export interface DashboardMetrics {
  active_dispatches: number;
  completed_today: number;
  pending_orders: number;
  vehicles_in_transit: number;
  temperature_alerts: number;
  timestamp: string;
}

// Notification Types
export interface NotificationPayload {
  title: string;
  body: string;
  data?: Record<string, any>;
}

// Navigation Types
export type RootStackParamList = {
  Login: undefined;
  Main: undefined;
  DispatchDetail: { dispatchId: number };
  VehicleDetail: { vehicleId: number };
  DriverDetail: { driverId: number };
  OrderDetail: { orderId: number };
  CustomerDetail: { customerId: number };
  MapTracking: { vehicleId?: number; dispatchId?: number };
  TemperatureDetail: { vehicleId: number };
  AlertDetail: { alertId: number };
  ReportDetail: { reportType: string; reportId?: number };
};

export type MainTabParamList = {
  Dashboard: undefined;
  Dispatches: undefined;
  Vehicles: undefined;
  Drivers: undefined;
  Orders: undefined;
  Alerts: undefined;
  More: undefined;
};

// Storage Keys
export enum StorageKeys {
  AUTH_TOKEN = '@auth_token',
  USER_DATA = '@user_data',
  OFFLINE_DATA = '@offline_data',
  SETTINGS = '@settings',
  NOTIFICATION_TOKEN = '@notification_token',
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface PaginationParams {
  page?: number;
  size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

// Filters
export interface DispatchFilters extends PaginationParams {
  status?: Dispatch['status'];
  vehicle_id?: number;
  driver_id?: number;
  date_from?: string;
  date_to?: string;
}

export interface VehicleFilters extends PaginationParams {
  status?: Vehicle['status'];
  vehicle_type?: Vehicle['vehicle_type'];
}

export interface DriverFilters extends PaginationParams {
  status?: Driver['status'];
}

export interface OrderFilters extends PaginationParams {
  status?: Order['status'];
  customer_id?: number;
  date_from?: string;
  date_to?: string;
}

export interface AlertFilters extends PaginationParams {
  alert_type?: Alert['alert_type'];
  severity?: Alert['severity'];
  is_resolved?: boolean;
}
