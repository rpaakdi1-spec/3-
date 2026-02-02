/**
 * API Service for ML Dispatch
 * 
 * Phase 3: ML Dispatch API 통신 레이어
 */

import { api } from './api'

export const mlDispatchAPI = {
  // Phase 2: Historical Simulation
  async simulate(targetDate: string) {
    return api.post(`/ml-dispatch/simulate?target_date=${targetDate}`)
  },

  async getSimulateMetrics(startDate: string, endDate: string) {
    return api.get(`/ml-dispatch/simulate/metrics?start_date=${startDate}&end_date=${endDate}`)
  },

  // Phase 2: Real-time ML Optimization
  async optimize(orderIds: number[], mode: 'recommend' | 'auto' = 'recommend') {
    return api.post(`/ml-dispatch/optimize?mode=${mode}`, { order_ids: orderIds })
  },

  async getPerformance(startDate?: string, endDate?: string) {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    return api.get(`/ml-dispatch/performance?${params.toString()}`)
  },

  // Phase 3: A/B Testing
  async getABTestAssignment() {
    return api.get('/ml-dispatch/ab-test/assignment')
  },

  async updateRollout(percentage: number) {
    return api.post(`/ml-dispatch/ab-test/rollout?percentage=${percentage}`)
  },

  async getABTestStats() {
    return api.get('/ml-dispatch/ab-test/stats')
  },

  async getABTestMetrics() {
    return api.get('/ml-dispatch/ab-test/metrics')
  },

  async getRolloutHistory(limit: number = 20) {
    return api.get(`/ml-dispatch/ab-test/history?limit=${limit}`)
  },

  async forceAssignUser(userId: number, group: 'control' | 'treatment') {
    return api.post(`/ml-dispatch/ab-test/force-assign?user_id=${userId}&group=${group}`)
  }
}
