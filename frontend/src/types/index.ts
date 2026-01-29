export interface User {
  id: number;
  username: string;
  email: string;
  role: 'ADMIN' | 'DISPATCHER' | 'DRIVER' | 'CLIENT';
  is_active: boolean;
  created_at: string;
}

export interface Client {
  id: number;
  name: string;
  business_number: string;
  contact_person: string;
  phone: string;
  email?: string;
  address: string;
  is_active: boolean;
  created_at: string;
}

export interface Vehicle {
  id: number;
  license_plate: string;
  vehicle_type: 'FROZEN' | 'REFRIGERATED' | 'BOTH';
  capacity_ton: number;
  temp_min: number;
  temp_max: number;
  status: 'AVAILABLE' | 'DISPATCHED' | 'MAINTENANCE';
  current_location_lat?: number;
  current_location_lon?: number;
  last_location_update?: string;
  is_active: boolean;
}

export interface Order {
  id: number;
  order_number: string;
  client_id: number;
  client_name?: string;
  pickup_address: string;
  pickup_latitude: number;
  pickup_longitude: number;
  delivery_address: string;
  delivery_latitude: number;
  delivery_longitude: number;
  cargo_type: 'FROZEN' | 'REFRIGERATED' | 'BOTH';
  temperature_min: number;
  temperature_max: number;
  pallet_count: number;
  weight_kg?: number;  // Optional - deprecated
  volume_cbm: number;
  desired_pickup_time?: string;
  desired_delivery_time?: string;
  special_instructions?: string;
  status: 'PENDING' | 'DISPATCHED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  created_at: string;
  updated_at: string;
}

export interface Dispatch {
  id: number;
  dispatch_number: string;
  order_id: number;
  order_number?: string;
  vehicle_id: number;
  vehicle_plate?: string;
  driver_id: number;
  driver_name?: string;
  estimated_departure?: string;
  actual_departure?: string;
  estimated_arrival?: string;
  actual_arrival?: string;
  distance_km: number;
  estimated_duration_minutes: number;
  status: 'ASSIGNED' | 'IN_PROGRESS' | 'PICKUP_COMPLETE' | 'DELIVERY_COMPLETE' | 'COMPLETED' | 'CANCELLED';
  current_location_lat?: number;
  current_location_lon?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface TrackingInfo {
  tracking_number: string;
  order_number: string;
  status: string;
  current_location: {
    latitude: number;
    longitude: number;
    address: string;
  };
  estimated_arrival?: string;
  driver_contact?: string;
  history: Array<{
    status: string;
    timestamp: string;
    notes?: string;
  }>;
}

export interface DashboardStats {
  total_orders: number;
  pending_orders: number;
  active_dispatches: number;
  completed_today: number;
  available_vehicles: number;
  active_vehicles: number;
  revenue_today?: number;
  revenue_month?: number;
}

export interface MetricData {
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  active_dispatches: number;
  pending_orders: number;
  available_vehicles: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface PaginatedResponse<T> {
  total: number;
  items: T[];
  page?: number;
  size?: number;
}
