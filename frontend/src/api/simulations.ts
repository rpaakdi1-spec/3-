// Simulations API Client
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

// Types
export interface RuleSimulation {
  id: number;
  name: string;
  description?: string;
  rule_id?: number;
  rule_config: any;
  scenario_data: any;
  scenario_type: string;
  iterations: number;
  randomize_data: boolean;
  status: string;
  total_matches?: number;
  successful_matches?: number;
  failed_matches?: number;
  match_rate?: number;
  avg_response_time_ms?: number;
  min_response_time_ms?: number;
  max_response_time_ms?: number;
  estimated_cost?: number;
  estimated_distance_km?: number;
  estimated_time_minutes?: number;
  results?: any;
  errors?: any[];
  created_by?: string;
  started_at?: string;
  completed_at?: string;
  duration_seconds?: number;
  created_at: string;
  updated_at: string;
}

export interface SimulationCreateRequest {
  name: string;
  description?: string;
  rule_id?: number;
  rule_config: any;
  scenario_data: any;
  scenario_type?: string;
  iterations?: number;
  randomize_data?: boolean;
  created_by?: string;
}

export interface SimulationComparison {
  id: number;
  name: string;
  description?: string;
  simulation_a_id: number;
  simulation_b_id: number;
  winner?: string;
  comparison_metrics?: any;
  recommendation?: string;
  confidence_score?: number;
  created_at: string;
}

export interface ComparisonCreateRequest {
  name: string;
  description?: string;
  simulation_a_id: number;
  simulation_b_id: number;
}

export interface SimulationTemplate {
  id: number;
  name: string;
  description?: string;
  category?: string;
  difficulty: string;
  complexity_score?: number;
  usage_count: number;
  avg_success_rate?: number;
  scenario_data?: any;
  expected_results?: any;
}

export interface SimulationStatistics {
  period_days: number;
  total_simulations: number;
  completed_simulations: number;
  avg_match_rate: number;
  avg_response_time_ms: number;
}

// API Client
export const SimulationsAPI = {
  // 시뮬레이션 생성 및 실행
  create: async (data: SimulationCreateRequest): Promise<RuleSimulation> => {
    const response = await axios.post(`${API_BASE_URL}/simulations`, data);
    return response.data;
  },

  // 시뮬레이션 목록 조회
  list: async (params?: {
    skip?: number;
    limit?: number;
    status?: string;
    rule_id?: number;
  }): Promise<RuleSimulation[]> => {
    const response = await axios.get(`${API_BASE_URL}/simulations`, { params });
    return response.data;
  },

  // 시뮬레이션 상세 조회
  get: async (id: number): Promise<RuleSimulation> => {
    const response = await axios.get(`${API_BASE_URL}/simulations/${id}`);
    return response.data;
  },

  // 시뮬레이션 삭제
  delete: async (id: number): Promise<void> => {
    await axios.delete(`${API_BASE_URL}/simulations/${id}`);
  },

  // A/B 비교 실행
  compare: async (data: ComparisonCreateRequest): Promise<any> => {
    const response = await axios.post(`${API_BASE_URL}/simulations/compare`, data);
    return response.data;
  },

  // 비교 목록 조회
  listComparisons: async (params?: {
    skip?: number;
    limit?: number;
  }): Promise<SimulationComparison[]> => {
    const response = await axios.get(`${API_BASE_URL}/simulations/comparisons`, { params });
    return response.data;
  },

  // 템플릿 목록 조회
  listTemplates: async (params?: {
    category?: string;
    difficulty?: string;
  }): Promise<SimulationTemplate[]> => {
    const response = await axios.get(`${API_BASE_URL}/simulations/templates`, { params });
    return response.data;
  },

  // 템플릿 상세 조회
  getTemplate: async (id: number): Promise<SimulationTemplate> => {
    const response = await axios.get(`${API_BASE_URL}/simulations/templates/${id}`);
    return response.data;
  },

  // 통계 요약
  getStatistics: async (days: number = 7): Promise<SimulationStatistics> => {
    const response = await axios.get(`${API_BASE_URL}/simulations/statistics/summary`, {
      params: { days }
    });
    return response.data;
  },
};
