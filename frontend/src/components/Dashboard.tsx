import { useEffect, useState } from 'react'
import { clientsAPI, vehiclesAPI, ordersAPI, dispatchesAPI } from '../services/api'

interface Stats {
  clients: number
  vehicles: number
  pendingOrders: number
  dispatches: number
}

function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    clients: 0,
    vehicles: 0,
    pendingOrders: 0,
    dispatches: 0,
  })
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<string>('')

  useEffect(() => {
    loadStats()
    
    // 자동 새로고침: 30초마다 통계 업데이트
    const interval = setInterval(() => {
      loadStats()
    }, 30000) // 30초

    return () => clearInterval(interval)
  }, [])

  const loadStats = async () => {
    try {
      console.log('Dashboard: Loading stats...')
      const [clientsRes, vehiclesRes, ordersRes, dispatchesRes] = await Promise.all([
        clientsAPI.list(),
        vehiclesAPI.list(),
        ordersAPI.pendingCount(),
        dispatchesAPI.list(),
      ])

      console.log('Dashboard: API responses:', {
        clients: clientsRes.data,
        vehicles: vehiclesRes.data,
        orders: ordersRes.data,
        dispatches: dispatchesRes.data
      })

      const newStats = {
        clients: clientsRes.data.total || 0,
        vehicles: vehiclesRes.data.total || 0,
        pendingOrders: ordersRes.data.pending_count || 0,
        dispatches: dispatchesRes.data.total || 0,
      }

      console.log('Dashboard: Updated stats:', newStats)
      setStats(newStats)
      
      // 마지막 업데이트 시간 설정
      const now = new Date()
      setLastUpdated(now.toLocaleTimeString('ko-KR'))
    } catch (error) {
      console.error('Dashboard: Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="loading">데이터를 불러오는 중...</div>
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h1 style={{ margin: 0 }}>대시보드</h1>
          {lastUpdated && (
            <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#666' }}>
              마지막 업데이트: {lastUpdated}
            </p>
          )}
        </div>
        <button 
          className="button secondary" 
          onClick={loadStats}
          disabled={loading}
        >
          🔄 새로고침
        </button>
      </div>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>등록된 거래처</h3>
          <div className="value">{stats.clients}</div>
          <p style={{ marginTop: '8px', fontSize: '14px', color: '#666' }}>개</p>
        </div>
        
        <div className="stat-card">
          <h3>보유 차량</h3>
          <div className="value">{stats.vehicles}</div>
          <p style={{ marginTop: '8px', fontSize: '14px', color: '#666' }}>대</p>
        </div>
        
        <div className="stat-card">
          <h3>배차 대기 주문</h3>
          <div className="value" style={{ color: '#ff9800' }}>{stats.pendingOrders}</div>
          <p style={{ marginTop: '8px', fontSize: '14px', color: '#666' }}>건</p>
        </div>
        
        <div className="stat-card">
          <h3>총 배차 계획</h3>
          <div className="value" style={{ color: '#4caf50' }}>{stats.dispatches}</div>
          <p style={{ marginTop: '8px', fontSize: '14px', color: '#666' }}>개</p>
        </div>
      </div>

      <div className="card">
        <h2>빠른 시작</h2>
        <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
          <div style={{ flex: 1, padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>1. 데이터 준비</h3>
            <p style={{ fontSize: '14px', color: '#666' }}>
              거래처, 차량, 주문 정보를 엑셀 파일로 업로드하세요.
            </p>
          </div>
          <div style={{ flex: 1, padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>2. AI 배차 실행</h3>
            <p style={{ fontSize: '14px', color: '#666' }}>
              대기 중인 주문을 선택하고 AI 최적화를 실행하세요.
            </p>
          </div>
          <div style={{ flex: 1, padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>3. 배차 확정</h3>
            <p style={{ fontSize: '14px', color: '#666' }}>
              최적화된 배차 계획을 검토하고 확정하세요.
            </p>
          </div>
        </div>
      </div>

      <div className="card">
        <h2>시스템 정보</h2>
        <table className="table">
          <tbody>
            <tr>
              <td><strong>버전</strong></td>
              <td>1.0.0 (Phase 1 PoC)</td>
            </tr>
            <tr>
              <td><strong>최적화 알고리즘</strong></td>
              <td>Google OR-Tools VRP (Greedy)</td>
            </tr>
            <tr>
              <td><strong>지오코딩</strong></td>
              <td>Naver Map API</td>
            </tr>
            <tr>
              <td><strong>상태</strong></td>
              <td><span className="badge success">정상</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Dashboard
