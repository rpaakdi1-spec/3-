import { useState, useEffect } from 'react'
import { ordersAPI, clientsAPI } from '../services/api'

interface OrderForm {
  order_number: string
  order_date: string
  pickup_client_id: number | ''
  delivery_client_id: number | ''
  product_name: string
  quantity_pallets: number
  weight_kg: number
  volume_cbm: number
  temperature_zone: string
  pickup_time_start?: string
  pickup_time_end?: string
  delivery_time_start?: string
  delivery_time_end?: string
  notes?: string
}

interface Order {
  id: number
  order_number: string
  order_date: string
  product_name: string
  quantity_pallets: number
  weight_kg: number
  temperature_zone: string
  status: string
  pickup_client_name?: string
  delivery_client_name?: string
}

function OrderUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string>('')
  const [showForm, setShowForm] = useState(false)
  const [clients, setClients] = useState<any[]>([])
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState<OrderForm>({
    order_number: '',
    order_date: new Date().toISOString().split('T')[0],
    pickup_client_id: '',
    delivery_client_id: '',
    product_name: '',
    quantity_pallets: 1,
    weight_kg: 500,
    volume_cbm: 1.5,
    temperature_zone: 'frozen',
    pickup_time_start: '08:00',
    pickup_time_end: '18:00',
    delivery_time_start: '08:00',
    delivery_time_end: '18:00',
    notes: ''
  })

  // 컴포넌트 마운트 시 주문 목록 로드
  useEffect(() => {
    loadOrders()
  }, [])

  useEffect(() => {
    if (showForm) {
      loadClients()
    }
  }, [showForm])

  // 업로드/등록 성공 시 주문 목록 새로고침
  useEffect(() => {
    if (result && (result.created > 0)) {
      loadOrders()
    }
  }, [result])

  const loadOrders = async () => {
    setLoading(true)
    try {
      const response = await ordersAPI.list()
      setOrders(response.data.items || [])
    } catch (err) {
      console.error('Failed to load orders:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadClients = async () => {
    try {
      const response = await clientsAPI.list()
      setClients(response.data.items || [])
    } catch (err) {
      console.error('Failed to load clients:', err)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setResult(null)
      setError('')
    }
  }

  const handleUpload = async () => {
    if (!file) return
    setUploading(true)
    setError('')
    setResult(null)

    try {
      const response = await ordersAPI.upload(file)
      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '업로드 중 오류가 발생했습니다')
    } finally {
      setUploading(false)
    }
  }

  const downloadTemplate = async () => {
    try {
      const response = await ordersAPI.downloadTemplate()
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'orders_template.xlsx')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      setError('템플릿 다운로드 중 오류가 발생했습니다')
    }
  }

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setUploading(true)
    setError('')
    setResult(null)

    try {
      await ordersAPI.create(formData)
      setResult({ created: 1, failed: 0, total: 1 })
      setShowForm(false)
      // Reset form
      setFormData({
        order_number: '',
        order_date: new Date().toISOString().split('T')[0],
        pickup_client_id: '',
        delivery_client_id: '',
        product_name: '',
        quantity_pallets: 1,
        weight_kg: 500,
        volume_cbm: 1.5,
        temperature_zone: 'frozen',
        pickup_time_start: '08:00',
        pickup_time_end: '18:00',
        delivery_time_start: '08:00',
        delivery_time_end: '18:00',
        notes: ''
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || '등록 중 오류가 발생했습니다')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div>
      <div className="card">
        <h2>주문 일괄 업로드</h2>
        <p style={{ marginBottom: '20px', color: '#666' }}>
          엑셀 파일로 주문 정보를 일괄 등록하거나 직접 등록할 수 있습니다.
        </p>

        <div style={{ marginBottom: '20px', display: 'flex', gap: '10px' }}>
          <button className="button secondary" onClick={downloadTemplate}>
            📥 템플릿 다운로드
          </button>
          <button 
            className="button" 
            onClick={() => setShowForm(!showForm)}
            style={{ backgroundColor: showForm ? '#6c757d' : '#28a745' }}
          >
            {showForm ? '❌ 폼 닫기' : '➕ 직접 등록'}
          </button>
          <button 
            className="button secondary" 
            onClick={loadOrders}
            disabled={loading}
          >
            🔄 새로고침
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}
        {result && (
          <div className="success-message">
            <strong>등록 완료!</strong>
            <ul style={{ marginTop: '8px', marginLeft: '20px' }}>
              <li>총 {result.total}건</li>
              <li>성공: {result.created}건</li>
              <li>실패: {result.failed}건</li>
            </ul>
          </div>
        )}

        {showForm && (
          <div style={{ 
            marginBottom: '30px', 
            padding: '20px', 
            border: '2px solid #28a745', 
            borderRadius: '8px',
            backgroundColor: '#f8f9fa'
          }}>
            <h3 style={{ marginBottom: '15px' }}>주문 직접 등록</h3>
            <form onSubmit={handleFormSubmit}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    주문번호 *
                  </label>
                  <input
                    type="text"
                    name="order_number"
                    value={formData.order_number}
                    onChange={handleFormChange}
                    required
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    주문일자 *
                  </label>
                  <input
                    type="date"
                    name="order_date"
                    value={formData.order_date}
                    onChange={handleFormChange}
                    required
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    상차 거래처 *
                  </label>
                  <select
                    name="pickup_client_id"
                    value={formData.pickup_client_id}
                    onChange={handleFormChange}
                    required
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  >
                    <option value="">선택하세요</option>
                    {clients.filter(c => c.client_type === 'PICKUP' || c.client_type === 'BOTH').map(client => (
                      <option key={client.id} value={client.id}>
                        {client.name} ({client.code})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    하차 거래처 *
                  </label>
                  <select
                    name="delivery_client_id"
                    value={formData.delivery_client_id}
                    onChange={handleFormChange}
                    required
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  >
                    <option value="">선택하세요</option>
                    {clients.filter(c => c.client_type === 'DELIVERY' || c.client_type === 'BOTH').map(client => (
                      <option key={client.id} value={client.id}>
                        {client.name} ({client.code})
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    제품명 *
                  </label>
                  <input
                    type="text"
                    name="product_name"
                    value={formData.product_name}
                    onChange={handleFormChange}
                    required
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    온도존 *
                  </label>
                  <select
                    name="temperature_zone"
                    value={formData.temperature_zone}
                    onChange={handleFormChange}
                    required
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  >
                    <option value="frozen">냉동 (-18°C)</option>
                    <option value="chilled">냉장 (0~5°C)</option>
                    <option value="ambient">상온</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    팔레트 수 *
                  </label>
                  <input
                    type="number"
                    name="quantity_pallets"
                    value={formData.quantity_pallets}
                    onChange={handleFormChange}
                    required
                    min="0"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    중량 (kg) *
                  </label>
                  <input
                    type="number"
                    name="weight_kg"
                    value={formData.weight_kg}
                    onChange={handleFormChange}
                    required
                    min="0"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    용적 (CBM) *
                  </label>
                  <input
                    type="number"
                    name="volume_cbm"
                    value={formData.volume_cbm}
                    onChange={handleFormChange}
                    required
                    min="0"
                    step="0.1"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    상차 시작시간
                  </label>
                  <input
                    type="time"
                    name="pickup_time_start"
                    value={formData.pickup_time_start}
                    onChange={handleFormChange}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    상차 종료시간
                  </label>
                  <input
                    type="time"
                    name="pickup_time_end"
                    value={formData.pickup_time_end}
                    onChange={handleFormChange}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    하차 시작시간
                  </label>
                  <input
                    type="time"
                    name="delivery_time_start"
                    value={formData.delivery_time_start}
                    onChange={handleFormChange}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    하차 종료시간
                  </label>
                  <input
                    type="time"
                    name="delivery_time_end"
                    value={formData.delivery_time_end}
                    onChange={handleFormChange}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div style={{ gridColumn: '1 / -1' }}>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    비고
                  </label>
                  <textarea
                    name="notes"
                    value={formData.notes}
                    onChange={handleFormChange}
                    rows={3}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
              </div>
              <div style={{ marginTop: '20px', display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button 
                  type="button" 
                  className="button secondary"
                  onClick={() => setShowForm(false)}
                >
                  취소
                </button>
                <button 
                  type="submit" 
                  className="button"
                  disabled={uploading}
                >
                  {uploading ? '등록 중...' : '등록하기'}
                </button>
              </div>
            </form>
          </div>
        )}

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <div className="file-input-wrapper">
            <button className="button">파일 선택</button>
            <input type="file" accept=".xlsx,.xls" onChange={handleFileChange} />
          </div>
          {file && <span>{file.name}</span>}
        </div>

        <div style={{ marginTop: '20px' }}>
          <button className="button" onClick={handleUpload} disabled={!file || uploading}>
            {uploading ? '업로드 중...' : '업로드 시작'}
          </button>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h2 style={{ margin: 0 }}>등록된 주문 목록 ({orders.length}건)</h2>
        </div>

        {loading ? (
          <div className="loading">주문 목록을 불러오는 중...</div>
        ) : orders.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            등록된 주문이 없습니다. 주문을 등록해주세요.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>주문번호</th>
                  <th>주문일자</th>
                  <th>제품명</th>
                  <th>팔레트</th>
                  <th>중량(kg)</th>
                  <th>온도존</th>
                  <th>상차지</th>
                  <th>하차지</th>
                  <th>상태</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id}>
                    <td><strong>{order.order_number}</strong></td>
                    <td>{order.order_date}</td>
                    <td>{order.product_name}</td>
                    <td>{order.quantity_pallets}</td>
                    <td>{order.weight_kg.toLocaleString()}</td>
                    <td>
                      <span className={`badge ${
                        order.temperature_zone === 'frozen' ? 'info' : 
                        order.temperature_zone === 'chilled' ? 'success' : 'warning'
                      }`}>
                        {order.temperature_zone === 'frozen' ? '냉동' : 
                         order.temperature_zone === 'chilled' ? '냉장' : '상온'}
                      </span>
                    </td>
                    <td style={{ maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {order.pickup_client_name || '-'}
                    </td>
                    <td style={{ maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {order.delivery_client_name || '-'}
                    </td>
                    <td>
                      <span className={`badge ${
                        order.status === 'PENDING' ? 'warning' : 
                        order.status === 'ASSIGNED' ? 'info' : 
                        order.status === 'COMPLETED' ? 'success' : 'error'
                      }`}>
                        {order.status === 'PENDING' ? '대기' : 
                         order.status === 'ASSIGNED' ? '배차완료' : 
                         order.status === 'COMPLETED' ? '완료' : order.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card">
        <h2>업로드 가이드</h2>
        <ol style={{ marginLeft: '20px', color: '#666' }}>
          <li style={{ marginBottom: '8px' }}>위의 "템플릿 다운로드" 버튼을 클릭하여 엑셀 템플릿을 다운로드합니다.</li>
          <li style={{ marginBottom: '8px' }}>템플릿에 주문 정보를 입력합니다.</li>
          <li style={{ marginBottom: '8px' }}>작성한 파일을 업로드합니다.</li>
          <li style={{ marginBottom: '8px' }}><strong>또는</strong> "직접 등록" 버튼으로 한 건씩 등록할 수 있습니다.</li>
          <li style={{ marginBottom: '8px' }}>등록된 주문은 하단의 주문 목록에서 확인할 수 있습니다.</li>
        </ol>
      </div>
    </div>
  )
}

export default OrderUpload
