import { useState } from 'react'
import { ordersAPI } from '../services/api'

interface ParsedOrder {
  order_date: string
  pickup_client_id?: number
  delivery_client_id?: number
  pickup_client_name?: string
  delivery_client_name?: string
  pickup_address?: string
  delivery_address?: string
  temperature_zone?: string
  pallet_count?: number
  weight_kg?: number
  pickup_start_time?: string
  raw_text: string
  confidence: number
  needs_review: boolean
  is_valid: boolean
  validation_errors?: string[]
}

function OrderNLPInput({ onOrdersCreated }: { onOrdersCreated?: () => void }) {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [parsedOrders, setParsedOrders] = useState<ParsedOrder[]>([])
  const [error, setError] = useState<string>('')
  const [creating, setCreating] = useState<{ [key: number]: boolean }>({})

  const exampleText = `[02/03] 추가 배차요청
백암 _ 저온 → 경산 16판 1대

동이천센터 → 양산 16판 1대

**2/3(화)목우촌 오후배차**
15:30 / 육가공5톤
16:30 / 육가공11톤`

  const handleParse = async () => {
    if (!text.trim()) {
      setError('텍스트를 입력해주세요')
      return
    }

    setLoading(true)
    setError('')
    setParsedOrders([])

    try {
      const response = await ordersAPI.parseNLP(text)
      console.log('파싱 결과:', response.data)
      
      setParsedOrders(response.data.orders || [])
      
      if (response.data.orders.length === 0) {
        setError('파싱된 주문이 없습니다. 형식을 확인해주세요.')
      }
    } catch (err: any) {
      console.error('파싱 실패:', err)
      setError(err.response?.data?.detail || '파싱 중 오류가 발생했습니다')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateOrder = async (order: ParsedOrder, index: number) => {
    setCreating({ ...creating, [index]: true })
    setError('')

    try {
      // Generate order number
      const orderNumber = `ORD-${Date.now()}`
      
      const orderData = {
        order_number: orderNumber,
        order_date: order.order_date,
        temperature_zone: order.temperature_zone || 'REFRIGERATED',
        pallet_count: order.pallet_count || 1,
        weight_kg: order.weight_kg || 0,
        priority: 5,
        ...(order.pickup_client_id && { pickup_client_id: order.pickup_client_id }),
        ...(order.delivery_client_id && { delivery_client_id: order.delivery_client_id }),
        ...(order.pickup_address && { 
          pickup_address: order.pickup_address,
          pickup_address_detail: ''
        }),
        ...(order.delivery_address && { 
          delivery_address: order.delivery_address,
          delivery_address_detail: ''
        }),
        ...(order.pickup_start_time && { pickup_start_time: order.pickup_start_time }),
        notes: `[AI 파싱] ${order.raw_text}`
      }

      await ordersAPI.create(orderData)
      
      // Remove from list
      setParsedOrders(parsedOrders.filter((_, i) => i !== index))
      
      // Success message
      alert(`✅ 주문이 생성되었습니다: ${orderNumber}`)
      
      if (onOrdersCreated) {
        onOrdersCreated()
      }
    } catch (err: any) {
      console.error('주문 생성 실패:', err)
      setError(err.response?.data?.detail || '주문 생성 중 오류가 발생했습니다')
    } finally {
      setCreating({ ...creating, [index]: false })
    }
  }

  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 0.8) return { text: '높음', color: '#28a745' }
    if (confidence >= 0.5) return { text: '보통', color: '#ffc107' }
    return { text: '낮음', color: '#dc3545' }
  }

  const getTempZoneLabel = (zone?: string) => {
    const map: { [key: string]: string } = {
      'FROZEN': '냉동',
      'REFRIGERATED': '냉장',
      'AMBIENT': '상온'
    }
    return map[zone || ''] || zone || '-'
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0 }}>🤖 AI 자연어 주문 입력</h2>
        <button
          onClick={() => setText(exampleText)}
          className="button secondary"
          style={{ fontSize: '14px' }}
        >
          📝 예시 채우기
        </button>
      </div>

      <p style={{ marginBottom: '20px', color: '#666' }}>
        거래처의 자연어 요청을 입력하면 AI가 자동으로 주문으로 변환합니다.
      </p>

      <div style={{ marginBottom: '20px' }}>
        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
          거래처 요청 텍스트
        </label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="예:
[02/03] 추가 배차요청
백암 _ 저온 → 경산 16판 1대

동이천센터 → 양산 16판 1대"
          rows={10}
          style={{
            width: '100%',
            padding: '12px',
            fontSize: '14px',
            borderRadius: '4px',
            border: '1px solid #ddd',
            fontFamily: 'monospace'
          }}
        />
      </div>

      <button
        onClick={handleParse}
        disabled={loading || !text.trim()}
        className="button"
        style={{
          backgroundColor: '#007bff',
          cursor: loading || !text.trim() ? 'not-allowed' : 'pointer',
          opacity: loading || !text.trim() ? 0.6 : 1
        }}
      >
        {loading ? '🤖 AI 분석 중...' : '🤖 AI로 파싱하기'}
      </button>

      {error && (
        <div style={{
          padding: '12px',
          marginTop: '20px',
          backgroundColor: '#f8d7da',
          border: '1px solid #f5c6cb',
          borderRadius: '4px',
          color: '#721c24'
        }}>
          ⚠️ {error}
        </div>
      )}

      {parsedOrders.length > 0 && (
        <div style={{ marginTop: '30px' }}>
          <h3>📋 파싱 결과 ({parsedOrders.length}건)</h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {parsedOrders.map((order, index) => {
              const confidenceBadge = getConfidenceBadge(order.confidence)
              
              return (
                <div
                  key={index}
                  style={{
                    padding: '16px',
                    border: '2px solid',
                    borderColor: order.is_valid ? '#d4edda' : '#fff3cd',
                    borderRadius: '8px',
                    backgroundColor: order.is_valid ? '#f8fff9' : '#fffef5'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '12px' }}>
                    <div>
                      <strong style={{ fontSize: '16px' }}>주문 {index + 1}</strong>
                      <span
                        style={{
                          marginLeft: '12px',
                          padding: '4px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                          backgroundColor: confidenceBadge.color,
                          color: 'white'
                        }}
                      >
                        신뢰도: {confidenceBadge.text} ({(order.confidence * 100).toFixed(0)}%)
                      </span>
                    </div>
                    
                    {order.needs_review && (
                      <span style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        backgroundColor: '#ffc107',
                        color: '#856404'
                      }}>
                        ⚠️ 확인 필요
                      </span>
                    )}
                  </div>

                  <div style={{
                    padding: '12px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px',
                    marginBottom: '12px',
                    fontSize: '13px',
                    fontFamily: 'monospace',
                    color: '#666'
                  }}>
                    원문: {order.raw_text}
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '12px' }}>
                    <div>
                      <strong>주문일자:</strong> {order.order_date}
                    </div>
                    <div>
                      <strong>온도대:</strong> {getTempZoneLabel(order.temperature_zone)}
                    </div>
                    <div>
                      <strong>상차:</strong> {order.pickup_client_name || order.pickup_address || '-'}
                      {order.pickup_client_id && <span style={{ color: '#28a745', marginLeft: '4px' }}>✓</span>}
                    </div>
                    <div>
                      <strong>하차:</strong> {order.delivery_client_name || order.delivery_address || '-'}
                      {order.delivery_client_id && <span style={{ color: '#28a745', marginLeft: '4px' }}>✓</span>}
                    </div>
                    <div>
                      <strong>팔레트:</strong> {order.pallet_count ? `${order.pallet_count}개` : '-'}
                    </div>
                    <div>
                      <strong>중량:</strong> {order.weight_kg ? `${order.weight_kg.toLocaleString()}kg` : '-'}
                    </div>
                    {order.pickup_start_time && (
                      <div>
                        <strong>상차시간:</strong> {order.pickup_start_time}
                      </div>
                    )}
                  </div>

                  {order.validation_errors && order.validation_errors.length > 0 && (
                    <div style={{
                      padding: '8px 12px',
                      marginBottom: '12px',
                      backgroundColor: '#fff3cd',
                      borderRadius: '4px',
                      fontSize: '13px',
                      color: '#856404'
                    }}>
                      <strong>검증 오류:</strong>
                      <ul style={{ margin: '4px 0 0 20px', padding: 0 }}>
                        {order.validation_errors.map((err, i) => (
                          <li key={i}>{err}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <button
                    onClick={() => handleCreateOrder(order, index)}
                    disabled={creating[index]}
                    className="button"
                    style={{
                      backgroundColor: order.is_valid ? '#28a745' : '#ffc107',
                      cursor: creating[index] ? 'not-allowed' : 'pointer',
                      opacity: creating[index] ? 0.6 : 1
                    }}
                  >
                    {creating[index] ? '생성 중...' : order.is_valid ? '✓ 주문 생성' : '⚠️ 확인 후 생성'}
                  </button>
                </div>
              )
            })}
          </div>
        </div>
      )}

      <div className="card" style={{ marginTop: '20px', backgroundColor: '#f8f9fa' }}>
        <h3 style={{ marginTop: 0 }}>💡 사용 팁</h3>
        <ul style={{ marginLeft: '20px', color: '#666', lineHeight: '1.8' }}>
          <li><strong>날짜 형식:</strong> [02/03], 2/3, 02-03 등</li>
          <li><strong>온도대:</strong> 냉동/냉동칸, 냉장/냉장칸, 저온/저온칸, 상온/상온칸 등</li>
          <li><strong>경로:</strong> 백암 → 경산, 백암에서 경산으로</li>
          <li><strong>수량:</strong> 16판, 20팔레트, 5톤 등</li>
          <li><strong>시간:</strong> 15:30, 16:30 (HH:MM 형식)</li>
          <li><strong>신뢰도 낮음:</strong> 수동으로 확인 후 생성하세요</li>
        </ul>
      </div>
    </div>
  )
}

export default OrderNLPInput
