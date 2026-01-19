import axios from 'axios'

const API_BASE_URL = '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const clientsAPI = {
  list: () => api.get('/clients'),
  upload: (file: File, autoGeocode: boolean = true) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post(`/clients/upload?auto_geocode=${autoGeocode}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  geocode: (clientIds: number[]) => api.post('/clients/geocode', { client_ids: clientIds }),
}

export const vehiclesAPI = {
  list: () => api.get('/vehicles'),
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/vehicles/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export const ordersAPI = {
  list: (status?: string) => api.get('/orders', { params: { status } }),
  pendingCount: () => api.get('/orders/pending/count'),
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/orders/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export const dispatchesAPI = {
  list: () => api.get('/dispatches'),
  optimize: (orderIds: number[], vehicleIds?: number[], dispatchDate?: string) =>
    api.post('/dispatches/optimize', { order_ids: orderIds, vehicle_ids: vehicleIds, dispatch_date: dispatchDate }),
  confirm: (dispatchIds: number[]) => api.post('/dispatches/confirm', { dispatch_ids: dispatchIds }),
  stats: () => api.get('/dispatches/stats/summary'),
}
