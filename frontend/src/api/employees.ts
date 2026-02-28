/**
 * Employee API Client
 * 인사관리 API
 */
import apiClient from './client';

export interface EmployeeRole {
  MASTER: 'MASTER';
  ADMIN: 'ADMIN';
  MANAGER: 'MANAGER';
  DRIVER: 'DRIVER';
}

export interface EmploymentType {
  FULL_TIME: 'FULL_TIME';
  CONTRACT: 'CONTRACT';
  PART_TIME: 'PART_TIME';
  DAILY: 'DAILY';
}

export interface Employee {
  id: number;
  employee_code: string;
  name: string;
  name_en?: string;
  phone: string;
  email?: string;
  address?: string;
  emergency_contact?: string;
  photo_url?: string;
  
  role: keyof EmployeeRole;
  employment_type: keyof EmploymentType;
  department?: string;
  position?: string;
  
  hire_date: string; // ISO date
  resignation_date?: string;
  work_start_time: string; // HH:MM
  work_end_time: string;
  max_work_hours: number;
  
  license_type?: string;
  license_number?: string;
  license_issue_date?: string;
  
  has_cargo_license: boolean;
  cargo_license_number?: string;
  cargo_license_expiry_date?: string;
  
  // 🆕 지게차 운전능력
  can_drive_forklift: boolean;
  has_forklift_certificate: boolean;
  forklift_certificate_number?: string;
  forklift_certificate_issue_date?: string;
  forklift_certificate_expiry_date?: string;
  
  base_salary?: number;
  meal_allowance: number;
  transportation_allowance: number;
  hazard_allowance: number;
  bank_name?: string;
  account_number?: string;
  account_holder?: string;
  
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  
  // Computed fields
  forklift_status: string;
  can_be_assigned_to_vehicle: boolean;
  days_until_forklift_expiry?: number;
  needs_forklift_training: boolean;
}

export interface EmployeeCreate extends Omit<Employee, 'id' | 'created_at' | 'updated_at' | 'forklift_status' | 'can_be_assigned_to_vehicle' | 'days_until_forklift_expiry' | 'needs_forklift_training'> {}

export interface EmployeeUpdate extends Partial<EmployeeCreate> {}

export interface EmployeeListResponse {
  total: number;
  page: number;
  page_size: number;
  items: Employee[];
}

export interface DriverPoolItem {
  id: number;
  employee_code: string;
  name: string;
  phone: string;
  license_type?: string;
  has_cargo_license: boolean;
  can_drive_forklift: boolean;
  has_forklift_certificate: boolean;
  forklift_status: string;
  work_hours: string;
  is_active: boolean;
}

export interface EmployeeStatistics {
  total_employees: number;
  active_employees: number;
  by_role: Record<string, number>;
  by_employment_type: Record<string, number>;
  drivers_with_cargo_license: number;
  drivers_with_forklift_ability: number;
  drivers_with_forklift_certificate: number;
  drivers_needing_training: number;
}

export interface EmployeeFilterParams {
  role?: string;
  employment_type?: string;
  is_active?: boolean;
  license_type?: string;
  has_cargo_license?: boolean;
  can_drive_forklift?: boolean;
  has_forklift_certificate?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
}

class EmployeeAPI {
  private baseURL = '/api/v1/employees';

  /**
   * 직원 목록 조회
   */
  async list(params?: EmployeeFilterParams): Promise<EmployeeListResponse> {
    const response = await apiClient.get<EmployeeListResponse>(this.baseURL, { params });
    return response.data;
  }

  /**
   * 직원 상세 조회
   */
  async get(id: number): Promise<Employee> {
    const response = await apiClient.get<Employee>(`${this.baseURL}/${id}`);
    return response.data;
  }

  /**
   * 직원 등록
   */
  async create(data: EmployeeCreate): Promise<Employee> {
    const response = await apiClient.post<Employee>(this.baseURL, data);
    return response.data;
  }

  /**
   * 직원 정보 수정
   */
  async update(id: number, data: EmployeeUpdate): Promise<Employee> {
    const response = await apiClient.put<Employee>(`${this.baseURL}/${id}`, data);
    return response.data;
  }

  /**
   * 직원 삭제 (소프트 삭제)
   */
  async delete(id: number): Promise<void> {
    await apiClient.delete(`${this.baseURL}/${id}`);
  }

  /**
   * 운전자 풀 조회
   */
  async getDriverPool(filters?: { only_available?: boolean; can_drive_forklift?: boolean }): Promise<DriverPoolItem[]> {
    const response = await apiClient.get<DriverPoolItem[]>(`${this.baseURL}/drivers/pool`, { params: filters });
    return response.data;
  }

  /**
   * 지게차 가능 운전자 조회
   */
  async getForkliftCapableDrivers(): Promise<{ total: number; with_certificate: number; without_certificate: number; drivers: DriverPoolItem[] }> {
    const response = await apiClient.get(`${this.baseURL}/drivers/forklift-capable`);
    return response.data;
  }

  /**
   * 직원 통계
   */
  async getStatistics(): Promise<EmployeeStatistics> {
    const response = await apiClient.get<EmployeeStatistics>(`${this.baseURL}/statistics/overview`);
    return response.data;
  }
}

export const employeeAPI = new EmployeeAPI();
export default employeeAPI;
