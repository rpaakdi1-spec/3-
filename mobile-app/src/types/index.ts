// User types
export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'admin' | 'dispatcher' | 'driver' | 'viewer';
  is_active: boolean;
}

// Dispatch types
export interface Dispatch {
  id: number;
  dispatch_number: string;
  dispatch_date: string;
  vehicle_id: number;
  vehicle_code?: string;
  driver_name?: string;
  total_orders: number;
  total_pallets: number;
  total_weight_kg: number;
  status: DispatchStatus;
  routes: DispatchRoute[];
  created_at: string;
  updated_at: string;
}

export type DispatchStatus =
  | 'DRAFT'
  | 'CONFIRMED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'CANCELLED';

export interface DispatchRoute {
  id: number;
  dispatch_id: number;
  sequence: number;
  route_type: RouteType;
  order_id?: number;
  location_name: string;
  address: string;
  latitude: number;
  longitude: number;
  estimated_arrival_time?: string;
  actual_arrival_time?: string;
  estimated_departure_time?: string;
  actual_departure_time?: string;
  estimated_work_duration_minutes?: number;
  current_pallets: number;
  current_weight_kg: number;
  status?: RouteStatus;
  notes?: string;
  photos?: RoutePhoto[];
}

export type RouteType =
  | 'GARAGE_START'
  | 'PICKUP'
  | 'DELIVERY'
  | 'GARAGE_END';

export type RouteStatus =
  | 'PENDING'
  | 'ARRIVED'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'SKIPPED';

export interface RoutePhoto {
  id: number;
  route_id: number;
  photo_type: 'pickup' | 'delivery';
  photo_url: string;
  uploaded_at: string;
}

// Location types
export interface Location {
  latitude: number;
  longitude: number;
  timestamp: string;
}

// Auth types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Navigation types
export type RootStackParamList = {
  Login: undefined;
  Main: undefined;
  DispatchDetail: { dispatchId: number };
  RouteDetail: { dispatchId: number; routeId: number };
  Camera: { 
    dispatchId: number; 
    routeId: number; 
    photoType: 'pickup' | 'delivery' 
  };
};

export type MainTabParamList = {
  Home: undefined;
  Dispatches: undefined;
  Profile: undefined;
};
