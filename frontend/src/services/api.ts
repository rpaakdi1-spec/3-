import axios from 'axios'

const API_BASE_URL = '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

export const clientsAPI = {
  list: () => api.get('/clients/'),
  upload: (file: File, autoGeocode: boolean = true) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/clients/upload?auto_geocode=${autoGeocode}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  geocode: (clientIds: number[]) => api.post('/clients/geocode', { client_ids: clientIds }),
  downloadTemplate: () => api.get('/clients/template/download', { responseType: 'blob' }),
  create: (data: any) => api.post('/clients/', data),
  update: (id: number, data: any) => api.put(`/clients/${id}`, data),
  delete: (id: number) => api.delete(`/clients/${id}`),
}

export const vehiclesAPI = {
  list: (params?: { include_gps?: boolean }) => api.get('/vehicles/', { params }),
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/vehicles/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  downloadTemplate: () => api.get('/vehicles/template/download', { responseType: 'blob' }),
  syncUvis: () => api.post('/vehicles/sync/uvis'),
  create: (data: any) => api.post('/vehicles/', data),
  update: (id: number, data: any) => api.put(`/vehicles/${id}`, data),
  delete: (id: number) => api.delete(`/vehicles/${id}`),
}

export const ordersAPI = {
  list: (status?: string) => api.get('/orders/', { params: { status } }),
  pendingCount: () => api.get('/orders/pending/count'),
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/orders/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  downloadTemplate: () => api.get('/orders/template/download', { responseType: 'blob' }),
  create: (data: any) => api.post('/orders/', data),
  update: (id: number, data: any) => api.put(`/orders/${id}`, data),
  delete: (id: number) => api.delete(`/orders/${id}`),
}

export const dispatchesAPI = {
  list: () => api.get('/dispatches/'),
  optimize: (orderIds: number[], vehicleIds?: number[], dispatchDate?: string) =>
    api.post('/dispatches/optimize', { order_ids: orderIds, vehicle_ids: vehicleIds, dispatch_date: dispatchDate }),
  optimizeCVRPTW: (
    orderIds: number[], 
    vehicleIds?: number[], 
    dispatchDate?: string,
    timeLimit: number = 30,
    useTimeWindows: boolean = true,
    useRealRouting: boolean = false
  ) =>
    api.post(
      `/dispatches/optimize-cvrptw?time_limit=${timeLimit}&use_time_windows=${useTimeWindows}&use_real_routing=${useRealRouting}`,
      { order_ids: orderIds, vehicle_ids: vehicleIds, dispatch_date: dispatchDate }
    ),
  confirm: (dispatchIds: number[]) => api.post('/dispatches/confirm', { dispatch_ids: dispatchIds }),
  stats: () => api.get('/dispatches/stats/summary'),
  downloadExcel: (params?: { start_date?: string; end_date?: string; status?: string }) =>
    api.get('/dispatches/export/excel', { params, responseType: 'blob' }),
  delete: (id: number) => api.delete(`/dispatches/${id}`),
}

export const uvisAPI = {
  getVehicleLocation: (vehicleId: number) => api.get(`/uvis/vehicles/${vehicleId}/location`),
  getVehicleTemperature: (vehicleId: number) => api.get(`/uvis/vehicles/${vehicleId}/temperature`),
  getVehicleStatus: (vehicleId: number) => api.get(`/uvis/vehicles/${vehicleId}/status`),
  monitorVehicle: (vehicleId: number) => api.get(`/uvis/vehicles/${vehicleId}/monitor`),
  getBulkLocations: (vehicleIds?: number[]) => {
    const params = vehicleIds ? { vehicle_ids: vehicleIds } : {};
    return api.get('/uvis/vehicles/bulk/locations', { params });
  },
  getBulkTemperatures: (vehicleIds?: number[]) => {
    const params = vehicleIds ? { vehicle_ids: vehicleIds } : {};
    return api.get('/uvis/vehicles/bulk/temperatures', { params });
  },
  getDashboard: async () => {
    const response = await api.get('/uvis/dashboard');
    return response.data;
  },
  getRealtimeVehicles: (vehicleIds?: string) => 
    api.get('/uvis-gps/realtime/vehicles', { params: vehicleIds ? { vehicle_ids: vehicleIds } : {} }),
  syncGPS: (params?: { force_new_key?: boolean }) => 
    api.post('/uvis-gps/sync/gps', params || { force_new_key: false }),
  syncTemperature: (params?: { force_new_key?: boolean }) => 
    api.post('/uvis-gps/sync/temperature', params || { force_new_key: false }),
  syncAll: (params?: { force_new_key?: boolean }) => 
    api.post('/uvis-gps/sync/all', params || { force_new_key: false }),
}

// Phase 3: ML Dispatch API
export const mlDispatchAPI = {
  // Phase 2: Historical Simulation
  simulate: (targetDate: string) => 
    api.post(`/ml-dispatch/simulate?target_date=${targetDate}`),
  
  getSimulateMetrics: (startDate: string, endDate: string) => 
    api.get(`/ml-dispatch/simulate/metrics?start_date=${startDate}&end_date=${endDate}`),

  // Phase 2: Real-time ML Optimization
  optimize: (orderIds: number[], mode: 'recommend' | 'auto' = 'recommend') => 
    api.post(`/ml-dispatch/optimize?mode=${mode}`, { order_ids: orderIds }),

  getPerformance: (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    return api.get(`/ml-dispatch/performance?${params.toString()}`)
  },

  // Phase 3: A/B Testing
  getABTestAssignment: () => api.get('/ml-dispatch/ab-test/assignment'),
  
  updateRollout: (percentage: number) => 
    api.post(`/ml-dispatch/ab-test/rollout?percentage=${percentage}`),
  
  getABTestStats: () => api.get('/ml-dispatch/ab-test/stats'),
  
  getABTestMetrics: () => api.get('/ml-dispatch/ab-test/metrics'),
  
  getRolloutHistory: (limit: number = 20) => 
    api.get(`/ml-dispatch/ab-test/history?limit=${limit}`),
  
  forceAssignUser: (userId: number, group: 'control' | 'treatment') => 
    api.post(`/ml-dispatch/ab-test/force-assign?user_id=${userId}&group=${group}`)
}
