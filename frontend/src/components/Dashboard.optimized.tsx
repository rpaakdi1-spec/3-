import { useEffect, useState, useCallback, useMemo, memo } from 'react'
import { clientsAPI, vehiclesAPI, ordersAPI, dispatchesAPI } from '../services/api'

interface Stats {
  clients: number
  vehicles: number
  pendingOrders: number
  dispatches: number
}

// StatCard 컴포넌트를 memo로 래핑하여 불필요한 리렌더링 방지
const StatCard = memo(({ title, value, unit, color }: {
  title: string
  value: number
  unit: string
  color?: string
}) => (
  <div className="stat-card">
    <h3>{title}</h3>
    <div className="value" style={{ color }}>{value}</div>
    <p style={{ marginTop: '8px', fontSize: '14px', color: '#666' }}>{unit}</p>
  </div>
))

StatCard.displayName = 'StatCard'

// QuickStartCard 컴포넌트도 memo로 래핑
const QuickStartCard = memo(({ step, title, description }: {
  step: string
  title: string
  description: string
}) => (
  <div style={{ flex: 1, padding: '20px', backgroundColor: '#f5f5f5', borderRadius: '4px' }}>
    <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>{step}. {title}</h3>
    <p style={{ fontSize: '14px', color: '#666' }}>{description}</p>
  </div>
))

QuickStartCard.displayName = 'QuickStartCard'

function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    clients: 0,
    vehicles: 0,
    pendingOrders: 0,
    dispatches: 0,
  })
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<string>('')

  // loadStats를 useCallback으로 메모이제이션
  const loadStats = useCallback(async () => {
    try {
      const [clientsRes, vehiclesRes, ordersRes, dispatchesRes] = await Promise.all([
        clientsAPI.list(),
        vehiclesAPI.list(),
        ordersAPI.pendingCount(),
        dispatchesAPI.list(),
      ])

      const newStats = {
        clients: clientsRes.data.total || 0,
        vehicles: vehiclesRes.data.total || 0,
        pendingOrders: ordersRes.data.pending_count || 0,
        dispatches: dispatchesRes.data.total || 0,
      }

      setStats(newStats)
      
      // 마지막 업데이트 시간 설정
      const now = new Date()
      setLastUpdated(now.toLocaleTimeString('ko-KR'))
    } catch (error) {
      console.error('Dashboard: Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }, []) // 의존성 없음 - 한 번만 생성

  useEffect(() => {
    loadStats()
    
    // 자동 새로고침: 30초마다 통계 업데이트
    const interval = setInterval(loadStats, 30000) // 30초

    return () => clearInterval(interval)
  }, [loadStats])

  // Quick start 데이터를 useMemo로 메모이제이션
  const quickStartSteps = useMemo(() => [
    {
      step: '1',
      title: '데이터 준비',
      description: '거래처, 차량, 주문 정보를 엑셀 파일로 업로드하세요.'
    },
    {
      step: '2',
      title: 'AI 배차 실행',
      description: '대기 중인 주문을 선택하고 AI 최적화를 실행하세요.'
    },
    {
      step: '3',
      title: '배차 확정',
      description: '최적화된 배차 계획을 검토하고 확정하세요.'
    }
  ], [])

  // Stats 카드 데이터를 useMemo로 메모이제이션
  const statCards = useMemo(() => [
    { title: '등록된 거래처', value: stats.clients, unit: '개' },
    { title: '보유 차량', value: stats.vehicles, unit: '대' },
    { title: '배차 대기 주문', value: stats.pendingOrders, unit: '건', color: '#ff9800' },
    { title: '총 배차 계획', value: stats.dispatches, unit: '개', color: '#4caf50' },
  ], [stats])

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
        {statCards.map((card, index) => (
          <StatCard 
            key={index}
            title={card.title}
            value={card.value}
            unit={card.unit}
            color={card.color}
          />
        ))}
      </div>

      <div className="card">
        <h2>빠른 시작</h2>
        <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
          {quickStartSteps.map((step) => (
            <QuickStartCard
              key={step.step}
              step={step.step}
              title={step.title}
              description={step.description}
            />
          ))}
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
              <td><strong>상태</strong></td>
              <td>
                <span style={{ color: '#4caf50' }}>● 정상</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Dashboard
