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

function DispatchOptimization() {
  const [orders, setOrders] = useState<Order[]>([])
  const [selectedOrders, setSelectedOrders] = useState<number[]>([])
  const [optimizing, setOptimizing] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    loadPendingOrders()
  }, [])

  const loadPendingOrders = async () => {
    try {
      const response = await ordersAPI.list('배차대기')
      setOrders(response.data.items || [])
    } catch (err) {
      console.error('Failed to load orders:', err)
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

  const handleOptimize = async () => {
    if (selectedOrders.length === 0) {
      setError('최소 1개 이상의 주문을 선택해주세요')
      return
    }

    setOptimizing(true)
    setError('')
    setResult(null)

    try {
      const today = new Date().toISOString().split('T')[0]
      const response = await dispatchesAPI.optimize(selectedOrders, undefined, today)
      setResult(response.data)
      
      if (response.data.success) {
        // Reload orders
        await loadPendingOrders()
        setSelectedOrders([])
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '최적화 중 오류가 발생했습니다')
    } finally {
      setOptimizing(false)
    }
  }

  return (
    <div>
      <div className="card">
        <h2>AI 배차 최적화</h2>
        <p style={{ marginBottom: '20px', color: '#666' }}>
          배차 대기 중인 주문을 선택하고 AI 최적화를 실행하세요.
        </p>

        {error && <div className="error-message">{error}</div>}
        {result && result.success && (
          <div className="success-message">
            <strong>최적화 완료!</strong>
            <ul style={{ marginTop: '8px', marginLeft: '20px' }}>
              <li>처리한 주문: {result.total_orders}건</li>
              <li>생성된 배차: {result.total_dispatches}개</li>
            </ul>
          </div>
        )}

        <div style={{ marginBottom: '20px' }}>
          <button
            className="button"
            onClick={handleOptimize}
            disabled={selectedOrders.length === 0 || optimizing}
          >
            {optimizing ? '최적화 중...' : `🤖 AI 배차 실행 (${selectedOrders.length}건 선택)`}
          </button>
        </div>

        {orders.length === 0 ? (
          <p style={{ padding: '40px', textAlign: 'center', color: '#666' }}>
            배차 대기 중인 주문이 없습니다.
          </p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th style={{ width: '40px' }}>
                    <input
                      type="checkbox"
                      checked={selectedOrders.length === orders.length}
                      onChange={handleSelectAll}
                    />
                  </th>
                  <th>주문번호</th>
                  <th>온도대</th>
                  <th>팔레트</th>
                  <th>중량(kg)</th>
                  <th>상차지</th>
                  <th>하차지</th>
                </tr>
              </thead>
              <tbody>
                {orders.map(order => (
                  <tr key={order.id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedOrders.includes(order.id)}
                        onChange={() => handleSelectOrder(order.id)}
                      />
                    </td>
                    <td>{order.order_number}</td>
                    <td>
                      <span className={`badge ${
                        order.temperature_zone === '냉동' ? 'info' :
                        order.temperature_zone === '냉장' ? 'success' : 'warning'
                      }`}>
                        {order.temperature_zone}
                      </span>
                    </td>
                    <td>{order.pallet_count}</td>
                    <td>{order.weight_kg.toLocaleString()}</td>
                    <td>{order.pickup_client_name}</td>
                    <td>{order.delivery_client_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {result && result.dispatches && result.dispatches.length > 0 && (
        <div className="card">
          <h2>생성된 배차 계획</h2>
          {result.dispatches.map((dispatch: any, idx: number) => (
            <div key={idx} style={{ marginBottom: '20px', padding: '16px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
              <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>
                {dispatch.dispatch_number} - {dispatch.vehicle_code}
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px', marginBottom: '12px' }}>
                <div>
                  <strong>주문 수:</strong> {dispatch.total_orders}건
                </div>
                <div>
                  <strong>총 팔레트:</strong> {dispatch.total_pallets}개
                </div>
                <div>
                  <strong>총 중량:</strong> {dispatch.total_weight_kg.toLocaleString()}kg
                </div>
              </div>
              <details>
                <summary style={{ cursor: 'pointer', color: '#1976d2' }}>경로 상세보기</summary>
                <ol style={{ marginTop: '12px', marginLeft: '20px' }}>
                  {dispatch.routes.map((route: any, rIdx: number) => (
                    <li key={rIdx} style={{ marginBottom: '8px' }}>
                      <strong>{route.route_type}:</strong> {route.location_name}
                      {route.current_pallets > 0 && (
                        <span style={{ marginLeft: '10px', color: '#666' }}>
                          (적재: {route.current_pallets}팔레트)
                        </span>
                      )}
                    </li>
                  ))}
                </ol>
              </details>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default DispatchOptimization
