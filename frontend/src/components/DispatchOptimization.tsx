import { useEffect, useState } from 'react'
import { ordersAPI, dispatchesAPI } from '../services/api'

interface Order {
  id: number
  order_number: string
  temperature_zone: string
  pallet_count: number
  weight_kg: number
  pickup_client_name: string
  delivery_client_name: string
}

interface OptimizationSettings {
  algorithm: 'greedy' | 'cvrptw'
  timeLimit: number
  useTimeWindows: boolean
  useRealRouting: boolean
}

function DispatchOptimization() {
  const [orders, setOrders] = useState<Order[]>([])
  const [selectedOrders, setSelectedOrders] = useState<number[]>([])
  const [optimizing, setOptimizing] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string>('')
  
  // New: Optimization settings
  const [settings, setSettings] = useState<OptimizationSettings>({
    algorithm: 'cvrptw',
    timeLimit: 30,
    useTimeWindows: true,
    useRealRouting: false
  })

  useEffect(() => {
    loadPendingOrders()
  }, [])

  const loadPendingOrders = async () => {
    console.log('배차 대기 주문 로드 중...')
    try {
      const response = await ordersAPI.list('배차대기')
      console.log('주문 API 응답:', response.data)
      const orderItems = response.data.items || []
      console.log(`로드된 주문: ${orderItems.length}건`)
      setOrders(orderItems)
    } catch (err) {
      console.error('Failed to load orders:', err)
      setError('주문 목록을 불러오는데 실패했습니다')
    }
  }

  const handleSelectAll = () => {
    if (selectedOrders.length === orders.length) {
      setSelectedOrders([])
    } else {
      setSelectedOrders(orders.map(o => o.id))
    }
  }

  const handleSelectOrder = (orderId: number) => {
    if (selectedOrders.includes(orderId)) {
      setSelectedOrders(selectedOrders.filter(id => id !== orderId))
    } else {
      setSelectedOrders([...selectedOrders, orderId])
    }
  }

  const handleDeleteOrder = async (orderId: number, orderNumber: string) => {
    if (!window.confirm(`주문 "${orderNumber}"을(를) 삭제하시겠습니까?`)) {
      return
    }

    try {
      await ordersAPI.delete(orderId)
      setError('')
      // Remove from selected orders if it was selected
      setSelectedOrders(prev => prev.filter(id => id !== orderId))
      // Reload orders
      await loadPendingOrders()
    } catch (err: any) {
      console.error('Order deletion error:', err)
      let errorMessage = '주문 삭제 중 오류가 발생했습니다'
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      }
      setError(errorMessage)
    }
  }

  const handleOptimize = async () => {
    if (selectedOrders.length === 0) {
      setError('최소 1개 이상의 주문을 선택해주세요')
      return
    }

    console.log('=== AI 배차 최적화 시작 ===')
    console.log('선택된 주문:', selectedOrders)
    console.log('알고리즘:', settings.algorithm)
    console.log('설정:', settings)

    setOptimizing(true)
    setError('')
    setResult(null)

    try {
      const today = new Date().toISOString().split('T')[0]
      console.log('배차 날짜:', today)
      
      let response
      if (settings.algorithm === 'cvrptw') {
        console.log('CVRPTW 알고리즘 실행 중...')
        // CVRPTW 알고리즘
        response = await dispatchesAPI.optimizeCVRPTW(
          selectedOrders,
          undefined,
          today,
          settings.timeLimit,
          settings.useTimeWindows,
          settings.useRealRouting
        )
        console.log('CVRPTW 응답:', response.data)
      } else {
        console.log('Greedy 알고리즘 실행 중...')
        // Greedy 알고리즘 (기본)
        response = await dispatchesAPI.optimize(selectedOrders, undefined, today)
        console.log('Greedy 응답:', response.data)
      }
      
      setResult(response.data)
      
      if (response.data.success) {
        console.log('✅ 배차 최적화 성공!')
        // Reload orders
        await loadPendingOrders()
        setSelectedOrders([])
      } else {
        console.warn('⚠️ 배차 최적화 실패:', response.data.error)
        setError(response.data.error || '배차 최적화에 실패했습니다')
      }
    } catch (err: any) {
      console.error('❌ 배차 최적화 오류:', err)
      console.error('오류 응답:', err.response)
      
      let errorMessage = '최적화 중 오류가 발생했습니다'
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      } else if (err.message) {
        errorMessage = err.message
      }
      
      setError(errorMessage)
    } finally {
      setOptimizing(false)
      console.log('=== AI 배차 최적화 종료 ===')
    }
  }

  return (
    <div>
      <div className="card">
        <h2>AI 배차 최적화</h2>
        <p style={{ marginBottom: '20px', color: '#666' }}>
          배차 대기 중인 주문을 선택하고 AI 최적화를 실행하세요.
        </p>

        {/* Optimization Settings */}
        <div className="settings-panel" style={{ 
          background: '#f8f9fa', 
          padding: '16px', 
          borderRadius: '8px', 
          marginBottom: '20px' 
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '12px' }}>⚙️ 최적화 설정</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            {/* Algorithm Selection */}
            <div>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
                알고리즘
              </label>
              <select
                value={settings.algorithm}
                onChange={(e) => setSettings({...settings, algorithm: e.target.value as 'greedy' | 'cvrptw'})}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              >
                <option value="greedy">Greedy (빠름, 품질 낮음)</option>
                <option value="cvrptw">CVRPTW (느림, 품질 높음) ⭐</option>
              </select>
            </div>

            {/* Time Limit */}
            {settings.algorithm === 'cvrptw' && (
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
                  시간 제한 (초): {settings.timeLimit}
                </label>
                <input
                  type="range"
                  min="5"
                  max="120"
                  step="5"
                  value={settings.timeLimit}
                  onChange={(e) => setSettings({...settings, timeLimit: parseInt(e.target.value)})}
                  style={{ width: '100%' }}
                />
              </div>
            )}
          </div>

          {/* CVRPTW Options */}
          {settings.algorithm === 'cvrptw' && (
            <div style={{ marginTop: '16px', display: 'flex', gap: '24px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  checked={settings.useTimeWindows}
                  onChange={(e) => setSettings({...settings, useTimeWindows: e.target.checked})}
                />
                <span>시간 제약 사용 (Time Windows)</span>
              </label>
              
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <input
                  type="checkbox"
                  checked={settings.useRealRouting}
                  onChange={(e) => setSettings({...settings, useRealRouting: e.target.checked})}
                />
                <span>실제 경로 (Naver API) 🗺️</span>
              </label>
            </div>
          )}

          {settings.algorithm === 'cvrptw' && settings.useRealRouting && (
            <div style={{ 
              marginTop: '12px', 
              padding: '8px 12px', 
              background: '#fff3cd', 
              border: '1px solid #ffc107',
              borderRadius: '4px',
              fontSize: '14px'
            }}>
              ⚠️ Naver API 사용 시 초기 실행이 느릴 수 있습니다 (캐시 미적용 시)
            </div>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}
        {result && result.success && (
          <div className="success-message">
            <strong>✅ 최적화 완료!</strong>
            <ul style={{ marginTop: '8px', marginLeft: '20px' }}>
              <li>처리한 주문: {result.total_orders}건</li>
              <li>생성된 배차: {result.total_dispatches}개</li>
              {result.total_distance_km && (
                <li>총 거리: {result.total_distance_km.toFixed(2)} km</li>
              )}
              {result.temperature_zones && (
                <li>
                  온도대별: {result.temperature_zones.map((z: any) => 
                    `${z.zone}(${z.orders}건/${z.dispatches}개)`
                  ).join(', ')}
                </li>
              )}
            </ul>
          </div>
        )}

        <div style={{ marginBottom: '20px' }}>
          <button
            className="button"
            onClick={handleOptimize}
            disabled={selectedOrders.length === 0 || optimizing}
            style={{
              backgroundColor: settings.algorithm === 'cvrptw' ? '#28a745' : '#007bff',
              cursor: selectedOrders.length === 0 || optimizing ? 'not-allowed' : 'pointer',
              opacity: selectedOrders.length === 0 || optimizing ? 0.6 : 1
            }}
          >
            {optimizing ? '최적화 중...' : `${settings.algorithm === 'cvrptw' ? '🚀 CVRPTW' : '⚡ Greedy'} 배차 최적화 실행 (${selectedOrders.length}건)`}
          </button>
        </div>

        <div style={{ marginBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0 }}>
            배차 대기 주문 ({orders.length}건)
            {selectedOrders.length > 0 && (
              <span style={{ 
                marginLeft: '12px', 
                color: '#28a745', 
                fontWeight: 'bold',
                fontSize: '16px'
              }}>
                ✓ {selectedOrders.length}건 선택됨
              </span>
            )}
          </h3>
          <button
            className="button secondary"
            onClick={handleSelectAll}
            style={{ 
              fontSize: '14px', 
              padding: '8px 16px',
              backgroundColor: selectedOrders.length === orders.length && orders.length > 0 ? '#6c757d' : '#007bff',
              color: 'white'
            }}
          >
            {selectedOrders.length === orders.length && orders.length > 0 ? '✗ 전체 해제' : '✓ 전체 선택'}
          </button>
        </div>

        {orders.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#999', padding: '40px 0' }}>
            배차 대기 중인 주문이 없습니다
          </p>
        ) : (
          <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: '50px' }}>
                    <input
                      type="checkbox"
                      checked={selectedOrders.length === orders.length && orders.length > 0}
                      onChange={handleSelectAll}
                      style={{ cursor: 'pointer' }}
                      title={selectedOrders.length === orders.length ? '전체 해제' : '전체 선택'}
                    />
                  </th>
                  <th>주문번호</th>
                  <th>온도대</th>
                  <th>팔레트</th>
                  <th>중량(kg)</th>
                  <th>상차지</th>
                  <th>하차지</th>
                  <th style={{ width: '80px' }}>관리</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id} style={{ 
                    backgroundColor: selectedOrders.includes(order.id) ? '#e3f2fd' : 'transparent'
                  }}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedOrders.includes(order.id)}
                        onChange={() => handleSelectOrder(order.id)}
                        style={{ cursor: 'pointer', width: '18px', height: '18px' }}
                      />
                    </td>
                    <td>{order.order_number}</td>
                    <td>
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        backgroundColor: 
                          order.temperature_zone === '냉동' ? '#e3f2fd' :
                          order.temperature_zone === '냉장' ? '#e8f5e9' : '#fff3e0',
                        color:
                          order.temperature_zone === '냉동' ? '#1976d2' :
                          order.temperature_zone === '냉장' ? '#388e3c' : '#f57c00'
                      }}>
                        {order.temperature_zone}
                      </span>
                    </td>
                    <td>{order.pallet_count}</td>
                    <td>{order.weight_kg.toFixed(1)}</td>
                    <td style={{ fontSize: '14px' }}>{order.pickup_client_name}</td>
                    <td style={{ fontSize: '14px' }}>{order.delivery_client_name}</td>
                    <td>
                      <button
                        onClick={() => handleDeleteOrder(order.id, order.order_number)}
                        style={{
                          padding: '4px 8px',
                          fontSize: '12px',
                          backgroundColor: '#dc3545',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer'
                        }}
                        title="주문 삭제"
                      >
                        🗑️ 삭제
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {result && result.dispatches && result.dispatches.length > 0 && (
        <div className="card" style={{ marginTop: '20px' }}>
          <h3>생성된 배차 목록</h3>
          <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
            {result.dispatches.map((dispatch: any, idx: number) => (
              <div key={idx} style={{ 
                padding: '16px', 
                border: '1px solid #e0e0e0', 
                borderRadius: '8px', 
                marginBottom: '16px',
                backgroundColor: '#f8f9fa'
              }}>
                {/* 배차 헤더 */}
                <div style={{ 
                  fontWeight: 600, 
                  fontSize: '16px',
                  marginBottom: '12px',
                  paddingBottom: '12px',
                  borderBottom: '2px solid #dee2e6'
                }}>
                  배차 #{idx + 1}: {dispatch.vehicle_code || `차량 ${dispatch.vehicle_id}`}
                </div>
                
                {/* 배차 요약 */}
                <div style={{ 
                  display: 'grid', 
                  gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                  gap: '12px',
                  marginBottom: '16px',
                  padding: '12px',
                  backgroundColor: 'white',
                  borderRadius: '6px'
                }}>
                  <div>
                    <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>주문 수</div>
                    <div style={{ fontSize: '18px', fontWeight: 600, color: '#2c3e50' }}>
                      {dispatch.total_orders}건
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>팔레트</div>
                    <div style={{ fontSize: '18px', fontWeight: 600, color: '#2c3e50' }}>
                      {dispatch.total_pallets}개
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>중량</div>
                    <div style={{ fontSize: '18px', fontWeight: 600, color: '#2c3e50' }}>
                      {dispatch.total_weight_kg?.toFixed(1) || 0}kg
                    </div>
                  </div>
                  {dispatch.distance_km && (
                    <div>
                      <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>거리</div>
                      <div style={{ fontSize: '18px', fontWeight: 600, color: '#2c3e50' }}>
                        {dispatch.distance_km.toFixed(2)}km
                      </div>
                    </div>
                  )}
                  {dispatch.duration_min && (
                    <div>
                      <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px' }}>소요시간</div>
                      <div style={{ fontSize: '18px', fontWeight: 600, color: '#2c3e50' }}>
                        {dispatch.duration_min}분
                      </div>
                    </div>
                  )}
                </div>

                {/* 주문 상세 목록 */}
                {dispatch.orders && dispatch.orders.length > 0 && (
                  <div style={{ marginTop: '12px' }}>
                    <div style={{ 
                      fontSize: '14px', 
                      fontWeight: 600, 
                      marginBottom: '8px',
                      color: '#495057'
                    }}>
                      📋 주문 상세 ({dispatch.orders.length}건)
                    </div>
                    <div style={{ 
                      backgroundColor: 'white',
                      borderRadius: '6px',
                      overflow: 'hidden'
                    }}>
                      <table style={{ 
                        width: '100%', 
                        fontSize: '13px',
                        borderCollapse: 'collapse'
                      }}>
                        <thead>
                          <tr style={{ backgroundColor: '#e9ecef' }}>
                            <th style={{ padding: '8px', textAlign: 'left', fontWeight: 600 }}>주문번호</th>
                            <th style={{ padding: '8px', textAlign: 'left', fontWeight: 600 }}>온도대</th>
                            <th style={{ padding: '8px', textAlign: 'center', fontWeight: 600 }}>팔레트</th>
                            <th style={{ padding: '8px', textAlign: 'center', fontWeight: 600 }}>중량(kg)</th>
                            <th style={{ padding: '8px', textAlign: 'left', fontWeight: 600 }}>상차지</th>
                            <th style={{ padding: '8px', textAlign: 'left', fontWeight: 600 }}>하차지</th>
                            <th style={{ padding: '8px', textAlign: 'center', fontWeight: 600 }}>시간</th>
                          </tr>
                        </thead>
                        <tbody>
                          {dispatch.orders.map((order: any, orderIdx: number) => (
                            <tr key={orderIdx} style={{ 
                              borderBottom: '1px solid #e9ecef',
                              backgroundColor: orderIdx % 2 === 0 ? 'white' : '#f8f9fa'
                            }}>
                              <td style={{ padding: '8px' }}>{order.order_number}</td>
                              <td style={{ padding: '8px' }}>
                                <span style={{
                                  padding: '2px 8px',
                                  borderRadius: '4px',
                                  fontSize: '11px',
                                  fontWeight: 500,
                                  backgroundColor: 
                                    order.temperature_zone === '냉동' ? '#e3f2fd' :
                                    order.temperature_zone === '냉장' ? '#e8f5e9' : '#fff3e0',
                                  color:
                                    order.temperature_zone === '냉동' ? '#1976d2' :
                                    order.temperature_zone === '냉장' ? '#388e3c' : '#f57c00'
                                }}>
                                  {order.temperature_zone}
                                </span>
                              </td>
                              <td style={{ padding: '8px', textAlign: 'center' }}>{order.pallet_count}</td>
                              <td style={{ padding: '8px', textAlign: 'center' }}>
                                {order.weight_kg?.toFixed(1) || '-'}
                              </td>
                              <td style={{ padding: '8px', fontSize: '12px' }}>
                                {order.pickup_client_name || order.pickup_address || '-'}
                              </td>
                              <td style={{ padding: '8px', fontSize: '12px' }}>
                                {order.delivery_client_name || order.delivery_address || '-'}
                              </td>
                              <td style={{ padding: '8px', textAlign: 'center', fontSize: '11px' }}>
                                {order.pickup_start_time && order.delivery_start_time ? (
                                  <div>
                                    <div>상: {order.pickup_start_time}</div>
                                    <div>하: {order.delivery_start_time}</div>
                                  </div>
                                ) : '-'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default DispatchOptimization
