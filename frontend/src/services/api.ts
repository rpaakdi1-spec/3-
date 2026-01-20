import axios from 'axios'

const API_BASE_URL = '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

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
}

export const vehiclesAPI = {
  list: () => api.get('/vehicles/'),
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/vehicles/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  downloadTemplate: () => api.get('/vehicles/template/download', { responseType: 'blob' }),
  create: (data: any) => api.post('/vehicles/', data),
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
}

export const dispatchesAPI = {
  list: () => api.get('/dispatches'),
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
}
