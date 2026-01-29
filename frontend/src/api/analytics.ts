/**
 * BI Dashboard API Service - Phase 10
 * BI 대시보드 API 서비스
 */
import axios from '../utils/axios';

export interface VehiclePerformance {
  vehicle_number: string;
  vehicle_type: string;
  period: {
    start: string;
    end: string;
  };
  fuel_efficiency: number;
  utilization_rate: number;
  efficiency_score: number;
  delivery_completion_rate: number;
  average_load_rate: number;
  total_distance_km: number;
  total_dispatches: number;
  total_deliveries: number;
}

export interface DriverEvaluation {
  driver_id: number;
  driver_name: string;
  overall_score: number;
  grade: string;
  scores: {
    delivery_completion: number;
    on_time_delivery: number;
    efficiency: number;
    safety: number;
    customer_satisfaction: number;
  };
  statistics: {
    total_dispatches: number;
    total_deliveries: number;
    completed_deliveries: number;
    completion_rate: number;
  };
  strengths: string[];
  areas_for_improvement: string[];
}

export interface CustomerSatisfaction {
  partner_id: number;
  partner_name: string;
  satisfaction_score: number;
  grade: string;
  metrics: {
    on_time_delivery_rate: number;
    order_completion_rate: number;
    avg_delivery_time_hours: number;
    temperature_violations: number;
    loyalty_score: number;
  };
  recommendations: string[];
}

export interface RouteEfficiency {
  dispatch_id: number;
  vehicle_number: string;
  overall_efficiency_score: number;
  metrics: {
    distance_efficiency: number;
    time_efficiency: number;
    sequence_efficiency: number;
    load_efficiency: number;
  };
  details: {
    total_distance_km: number;
    optimal_distance_km: number;
    distance_waste_km: number;
  };
  recommendations: string[];
}

export interface CostReport {
  period: {
    start: string;
    end: string;
  };
  costs: {
    fuel_cost: number;
    labor_cost: number;
    maintenance_cost: number;
    fixed_cost: number;
    total_cost: number;
  };
  revenue: {
    total_revenue: number;
    profit: number;
    profit_margin_percent: number;
  };
  metrics: {
    total_dispatches: number;
    total_deliveries: number;
    total_distance_km: number;
    cost_per_delivery: number;
    cost_per_km: number;
  };
  savings_opportunities: Array<{
    category: string;
    description: string;
    potential_savings: number;
    implementation_difficulty: string;
    actions: string[];
  }>;
  recommendations: string[];
}

// Vehicle Performance
export const getVehiclePerformance = async (
  vehicleId: number,
  startDate: string,
  endDate: string
): Promise<VehiclePerformance> => {
  const response = await axios.get(`/analytics/vehicles/${vehicleId}/performance`, {
    params: { start: startDate, end: endDate }
  });
  return response.data;
};

export const getFleetPerformanceSummary = async (
  startDate: string,
  endDate: string
) => {
  const response = await axios.get('/analytics/vehicles/fleet-summary', {
    params: { start: startDate, end: endDate }
  });
  return response.data;
};

export const getMaintenanceAlerts = async () => {
  const response = await axios.get('/analytics/vehicles/maintenance-alerts');
  return response.data;
};

export const compareVehicles = async (
  vehicleIds: number[],
  startDate: string,
  endDate: string
) => {
  const response = await axios.get('/analytics/vehicles/compare', {
    params: {
      vehicle_ids: vehicleIds.join(','),
      start: startDate,
      end: endDate
    }
  });
  return response.data;
};

// Driver Evaluation
export const getDriverEvaluation = async (
  driverId: number,
  startDate: string,
  endDate: string
): Promise<DriverEvaluation> => {
  const response = await axios.get(`/analytics/drivers/${driverId}/evaluation`, {
    params: { start: startDate, end: endDate }
  });
  return response.data;
};

export const getDriverRankings = async (
  startDate: string,
  endDate: string
): Promise<DriverEvaluation[]> => {
  const response = await axios.get('/analytics/drivers/rankings', {
    params: { start: startDate, end: endDate }
  });
  return response.data;
};

export const getDriverRecommendations = async (
  driverId: number,
  startDate: string,
  endDate: string
) => {
  const response = await axios.get(`/analytics/drivers/${driverId}/recommendations`, {
    params: { start: startDate, end: endDate }
  });
  return response.data;
};

// Customer Analytics
export const getCustomerSatisfaction = async (
  partnerId: number,
  startDate: string,
  endDate: string
): Promise<CustomerSatisfaction> => {
  const response = await axios.get(`/analytics/customers/${partnerId}/satisfaction`, {
    params: { start: startDate, end: endDate }
  });
  return response.data;
};

export const getTopCustomers = async (
  startDate: string,
  endDate: string,
  limit: number = 10
) => {
  const response = await axios.get('/analytics/customers/top', {
    params: { start: startDate, end: endDate, limit }
  });
  return response.data;
};

export const getChurnRiskCustomers = async (
  startDate: string,
  endDate: string
) => {
  const response = await axios.get('/analytics/customers/churn-risk', {
    params: { start: startDate, end: endDate }
  });
  return response.data;
};

// Route Efficiency
export const getRouteEfficiency = async (
  dispatchId: number
): Promise<RouteEfficiency> => {
  const response = await axios.get(`/analytics/routes/${dispatchId}/efficiency`);
  return response.data;
};

export const getFleetRouteEfficiency = async (
  startDate: string,
  endDate: string
) => {
  const response = await axios.get('/analytics/routes/fleet-efficiency', {
    params: { start: startDate, end: endDate }
  });
  return response.data;
};

export const getInefficientRoutes = async (
  startDate: string,
  endDate: string,
  threshold: number = 70
) => {
  const response = await axios.get('/analytics/routes/inefficient', {
    params: { start: startDate, end: endDate, threshold }
  });
  return response.data;
};

// Cost Optimization
export const getCostReport = async (
  startDate: string,
  endDate: string
): Promise<CostReport> => {
  const response = await axios.get('/analytics/costs/report', {
    params: { start: startDate, end: endDate }
  });
  return response.data;
};

export const getVehicleCosts = async (
  vehicleId: number,
  startDate: string,
  endDate: string
) => {
  const response = await axios.get(`/analytics/costs/vehicles/${vehicleId}`, {
    params: { start: startDate, end: endDate }
  });
  return response.data;
};

export const compareVehicleCosts = async (
  vehicleIds: number[],
  startDate: string,
  endDate: string
) => {
  const response = await axios.get('/analytics/costs/vehicles/compare', {
    params: {
      vehicle_ids: vehicleIds.join(','),
      start: startDate,
      end: endDate
    }
  });
  return response.data;
};

// Dashboard Summary
export const getDashboardSummary = async () => {
  const response = await axios.get('/analytics/dashboard');
  return response.data;
};
