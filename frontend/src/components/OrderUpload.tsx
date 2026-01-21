import { useState, useEffect } from 'react'
import { ordersAPI, clientsAPI } from '../services/api'

interface OrderForm {
  order_number: string
  order_date: string
  pickup_client_id: number | ''
  delivery_client_id: number | ''
  pickup_address?: string
  pickup_address_detail?: string
  delivery_address?: string
  delivery_address_detail?: string
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
  pallet_count: number
  weight_kg: number
  temperature_zone: string
  status: string
  pickup_client_name?: string
  delivery_client_name?: string
  pickup_client_id?: number
  delivery_client_id?: number
  pickup_address?: string
  pickup_address_detail?: string
  delivery_address?: string
  delivery_address_detail?: string
  volume_cbm?: number
  pickup_time_start?: string
  pickup_time_end?: string
  delivery_time_start?: string
  delivery_time_end?: string
  notes?: string
}

function OrderUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string>('')
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [clients, setClients] = useState<any[]>([])
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(false)
  const [usePickupAddress, setUsePickupAddress] = useState(false)
  const [useDeliveryAddress, setUseDeliveryAddress] = useState(false)
  const [formData, setFormData] = useState<OrderForm>({
    order_number: '',
    order_date: new Date().toISOString().split('T')[0],
    pickup_client_id: '',
    delivery_client_id: '',
    pickup_address: '',
    delivery_address: '',
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

  // 주문번호 자동 생성
  const generateOrderNumber = () => {
    const now = new Date()
    const year = now.getFullYear()
    const month = String(now.getMonth() + 1).padStart(2, '0')
    const day = String(now.getDate()).padStart(2, '0')
    const hours = String(now.getHours()).padStart(2, '0')
    const minutes = String(now.getMinutes()).padStart(2, '0')
    const seconds = String(now.getSeconds()).padStart(2, '0')
    return `ORD-${year}${month}${day}-${hours}${minutes}${seconds}`
  }

  // 폼 열기 시 주문번호 자동 생성
  useEffect(() => {
    if (showForm && !formData.order_number) {
      setFormData(prev => ({
        ...prev,
        order_number: generateOrderNumber()
      }))
    }
  }, [showForm])

  // 거래처 선택 시 주소 자동 입력
  const handleClientSelect = (field: 'pickup' | 'delivery', clientId: string) => {
    const selectedClient = clients.find(c => c.id === parseInt(clientId))
    
    if (field === 'pickup') {
      setFormData(prev => ({
        ...prev,
        pickup_client_id: clientId ? parseInt(clientId) : '',
        pickup_address: selectedClient?.address || '',
        pickup_address_detail: selectedClient?.address_detail || ''
      }))
    } else {
      setFormData(prev => ({
        ...prev,
        delivery_client_id: clientId ? parseInt(clientId) : '',
        delivery_address: selectedClient?.address || '',
        delivery_address_detail: selectedClient?.address_detail || ''
      }))
    }
  }

  // 팔레트 수 변경 시 용적 자동 계산 (1팔레트 = 1.5 CBM)
  const handlePalletChange = (pallets: number) => {
    setFormData(prev => ({
      ...prev,
      quantity_pallets: pallets,
      volume_cbm: pallets * 1.5
    }))
  }

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    
    // 팔레트 수 변경 시 용적 자동 계산
    if (name === 'quantity_pallets') {
      handlePalletChange(parseInt(value) || 0)
      return
    }
    
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
      // Convert English values to Korean for backend
      const tempZoneMap: { [key: string]: string } = {
        'frozen': '냉동',
        'chilled': '냉장',
        'ambient': '상온'
      }
      
      const apiData: any = {
        order_number: formData.order_number,
        order_date: formData.order_date,
        product_name: formData.product_name,
        pallet_count: formData.quantity_pallets,  // Map to backend field name
        weight_kg: formData.weight_kg,
        volume_cbm: formData.volume_cbm,
        temperature_zone: tempZoneMap[formData.temperature_zone] || '냉동',
        pickup_start_time: formData.pickup_time_start,
        pickup_end_time: formData.pickup_time_end,
        delivery_start_time: formData.delivery_time_start,
        delivery_end_time: formData.delivery_time_end,
        notes: formData.notes
      }
      
      // 상차지: 거래처 ID 또는 주소
      if (usePickupAddress && formData.pickup_address) {
        apiData.pickup_address = formData.pickup_address
        apiData.pickup_address_detail = formData.pickup_address_detail || ''
      } else if (formData.pickup_client_id) {
        apiData.pickup_client_id = formData.pickup_client_id
      }
      
      // 하차지: 거래처 ID 또는 주소
      if (useDeliveryAddress && formData.delivery_address) {
        apiData.delivery_address = formData.delivery_address
        apiData.delivery_address_detail = formData.delivery_address_detail || ''
      } else if (formData.delivery_client_id) {
        apiData.delivery_client_id = formData.delivery_client_id
      }
      
      // Create or Update
      if (editingId) {
        await ordersAPI.update(editingId, apiData)
        setResult({ created: 0, failed: 0, total: 1, message: '주문이 수정되었습니다.' })
      } else {
        await ordersAPI.create(apiData)
        setResult({ created: 1, failed: 0, total: 1 })
      }
      
      setShowForm(false)
      setEditingId(null)
      // Reset form
      setFormData({
        order_number: '',
        order_date: new Date().toISOString().split('T')[0],
        pickup_client_id: '',
        delivery_client_id: '',
        pickup_address: '',
        delivery_address: '',
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
      setUsePickupAddress(false)
      setUseDeliveryAddress(false)
    } catch (err: any) {
      console.error('Order creation error:', err)
      let errorMessage = '등록 중 오류가 발생했습니다'
      
      if (err.response) {
        // 서버에서 응답을 받은 경우
        if (err.response.data?.detail) {
          errorMessage = err.response.data.detail
          // 중복 주문번호 오류인 경우 새 번호 제안
          if (errorMessage.includes('이미 존재하는 주문번호')) {
            const newOrderNumber = generateOrderNumber()
            errorMessage += `\n\n새로운 주문번호로 시도해주세요: ${newOrderNumber}`
            setFormData(prev => ({ ...prev, order_number: newOrderNumber }))
          }
        } else if (err.response.status === 400) {
          errorMessage = '잘못된 요청입니다. 모든 필수 항목을 확인해주세요.'
        } else if (err.response.status === 404) {
          errorMessage = '선택한 거래처를 찾을 수 없습니다. 거래처를 다시 선택해주세요.'
        } else if (err.response.status >= 500) {
          errorMessage = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
        }
      } else if (err.request) {
        // 요청을 보냈지만 응답을 받지 못한 경우
        errorMessage = '서버에 연결할 수 없습니다. 인터넷 연결을 확인해주세요.'
      } else {
        // 요청 설정 중 오류가 발생한 경우
        errorMessage = `오류: ${err.message}`
      }
      
      setError(errorMessage)
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteOrder = async (orderId: number, orderNumber: string) => {
    if (!window.confirm(`주문번호 "${orderNumber}"을(를) 삭제하시겠습니까?\n\n배차대기 상태의 주문만 삭제 가능합니다.`)) {
      return
    }

    try {
      await ordersAPI.delete(orderId)
      setResult({ created: 0, failed: 0, total: 0, message: '주문이 삭제되었습니다.' })
      loadOrders()
    } catch (err: any) {
      console.error('Order deletion error:', err)
      let errorMessage = '삭제 중 오류가 발생했습니다'
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      }
      setError(errorMessage)
    }
  }

  const handleEditOrder = (order: Order) => {
    // Set editing mode
    setEditingId(order.id)
    
    // Populate form with order data for editing
    const tempZoneMap: { [key: string]: string } = {
      '냉동': 'frozen',
      '냉장': 'chilled',
      '상온': 'ambient'
    }

    setFormData({
      order_number: order.order_number,
      order_date: order.order_date,
      pickup_client_id: order.pickup_client_id || '',
      delivery_client_id: order.delivery_client_id || '',
      pickup_address: order.pickup_address || '',
      pickup_address_detail: order.pickup_address_detail || '',
      delivery_address: order.delivery_address || '',
      delivery_address_detail: order.delivery_address_detail || '',
      product_name: order.product_name,
      quantity_pallets: order.pallet_count,
      weight_kg: order.weight_kg,
      volume_cbm: order.volume_cbm || 0,
      temperature_zone: tempZoneMap[order.temperature_zone] || 'frozen',
      pickup_time_start: order.pickup_time_start || '08:00',
      pickup_time_end: order.pickup_time_end || '18:00',
      delivery_time_start: order.delivery_time_start || '08:00',
      delivery_time_end: order.delivery_time_end || '18:00',
      notes: order.notes || ''
    })

    // Set address mode based on whether addresses are present
    setUsePickupAddress(!!order.pickup_address)
    setUseDeliveryAddress(!!order.delivery_address)

    // Show the form
    setShowForm(true)

    // Scroll to form
    window.scrollTo({ top: 0, behavior: 'smooth' })
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

        {error && (
          <div className="error-message" style={{ 
            whiteSpace: 'pre-line',
            padding: '15px',
            marginBottom: '20px',
            backgroundColor: '#f8d7da',
            border: '1px solid #f5c6cb',
            borderRadius: '4px',
            color: '#721c24'
          }}>
            <strong>⚠️ 오류가 발생했습니다</strong>
            <div style={{ marginTop: '8px' }}>{error}</div>
          </div>
        )}
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
            <h3 style={{ marginBottom: '15px' }}>
              {editingId ? '주문 수정' : '주문 직접 등록'}
            </h3>
            <form onSubmit={handleFormSubmit}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    주문번호 *
                  </label>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <input
                      type="text"
                      name="order_number"
                      value={formData.order_number}
                      onChange={handleFormChange}
                      required
                      style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                    />
                    <button
                      type="button"
                      onClick={() => setFormData(prev => ({ ...prev, order_number: generateOrderNumber() }))}
                      style={{ 
                        padding: '8px 12px', 
                        borderRadius: '4px', 
                        border: '1px solid #ddd', 
                        backgroundColor: '#f8f9fa',
                        cursor: 'pointer',
                        fontSize: '14px'
                      }}
                      title="새로운 주문번호 생성"
                    >
                      🔄
                    </button>
                  </div>
                  <small style={{ color: '#666', fontSize: '12px' }}>자동생성됨. 필요시 수정 가능</small>
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
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '8px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <input
                        type="checkbox"
                        checked={usePickupAddress}
                        onChange={(e) => {
                          setUsePickupAddress(e.target.checked)
                          if (e.target.checked) {
                            setFormData(prev => ({ ...prev, pickup_client_id: '', pickup_address: '', pickup_address_detail: '' }))
                          }
                        }}
                      />
                      주소로 직접 입력
                    </label>
                  </div>
                  {usePickupAddress ? (
                    <>
                      <input
                        type="text"
                        name="pickup_address"
                        value={formData.pickup_address}
                        onChange={handleFormChange}
                        placeholder="상차 주소 (예: 서울특별시 강남구 테헤란로 123)"
                        required
                        style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                      />
                      <input
                        type="text"
                        name="pickup_address_detail"
                        value={formData.pickup_address_detail || ''}
                        onChange={handleFormChange}
                        placeholder="상세주소 (예: 3층)"
                        style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd', marginTop: '5px' }}
                      />
                    </>
                  ) : (
                    <>
                      <select
                        name="pickup_client_id"
                        value={formData.pickup_client_id}
                        onChange={(e) => handleClientSelect('pickup', e.target.value)}
                        required
                        style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                      >
                        <option value="">선택하세요</option>
                        {clients.filter(c => c.client_type === '상차' || c.client_type === '양쪽').map(client => (
                          <option key={client.id} value={client.id}>
                            {client.name} ({client.code})
                          </option>
                        ))}
                      </select>
                      {formData.pickup_client_id && formData.pickup_address && (
                        <div style={{ marginTop: '8px', padding: '8px', backgroundColor: '#e9ecef', borderRadius: '4px', fontSize: '13px' }}>
                          <div><strong>주소:</strong> {formData.pickup_address}</div>
                          {formData.pickup_address_detail && <div><strong>상세:</strong> {formData.pickup_address_detail}</div>}
                        </div>
                      )}
                    </>
                  )}
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    하차 거래처 *
                  </label>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '8px' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <input
                        type="checkbox"
                        checked={useDeliveryAddress}
                        onChange={(e) => {
                          setUseDeliveryAddress(e.target.checked)
                          if (e.target.checked) {
                            setFormData(prev => ({ ...prev, delivery_client_id: '', delivery_address: '', delivery_address_detail: '' }))
                          }
                        }}
                      />
                      주소로 직접 입력
                    </label>
                  </div>
                  {useDeliveryAddress ? (
                    <>
                      <input
                        type="text"
                        name="delivery_address"
                        value={formData.delivery_address}
                        onChange={handleFormChange}
                        placeholder="하차 주소 (예: 경기도 성남시 분당구 판교로 456)"
                        required
                        style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                      />
                      <input
                        type="text"
                        name="delivery_address_detail"
                        value={formData.delivery_address_detail || ''}
                        onChange={handleFormChange}
                        placeholder="상세주소 (예: B동 1층)"
                        style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd', marginTop: '5px' }}
                      />
                    </>
                  ) : (
                    <>
                      <select
                        name="delivery_client_id"
                        value={formData.delivery_client_id}
                        onChange={(e) => handleClientSelect('delivery', e.target.value)}
                        required
                        style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                      >
                        <option value="">선택하세요</option>
                        {clients.filter(c => c.client_type === '하차' || c.client_type === '양쪽').map(client => (
                          <option key={client.id} value={client.id}>
                            {client.name} ({client.code})
                          </option>
                        ))}
                      </select>
                      {formData.delivery_client_id && formData.delivery_address && (
                        <div style={{ marginTop: '8px', padding: '8px', backgroundColor: '#e9ecef', borderRadius: '4px', fontSize: '13px' }}>
                          <div><strong>주소:</strong> {formData.delivery_address}</div>
                          {formData.delivery_address_detail && <div><strong>상세:</strong> {formData.delivery_address_detail}</div>}
                        </div>
                      )}
                    </>
                  )}
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
                    readOnly
                    min="0"
                    step="0.1"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd', backgroundColor: '#e9ecef' }}
                    title="팔레트 수에 따라 자동 계산됩니다 (1팔레트 = 1.5 CBM)"
                  />
                  <small style={{ color: '#666', fontSize: '12px' }}>자동계산: {formData.quantity_pallets} 팔레트 × 1.5 = {formData.volume_cbm} CBM</small>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    상차 시작시간
                  </label>
                  <input
                    type="text"
                    name="pickup_time_start"
                    value={formData.pickup_time_start}
                    onChange={handleFormChange}
                    placeholder="HH:MM (예: 08:00)"
                    pattern="[0-2][0-9]:[0-5][0-9]"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    상차 종료시간
                  </label>
                  <input
                    type="text"
                    name="pickup_time_end"
                    value={formData.pickup_time_end}
                    onChange={handleFormChange}
                    placeholder="HH:MM (예: 18:00)"
                    pattern="[0-2][0-9]:[0-5][0-9]"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    하차 시작시간
                  </label>
                  <input
                    type="text"
                    name="delivery_time_start"
                    value={formData.delivery_time_start}
                    onChange={handleFormChange}
                    placeholder="HH:MM (예: 08:00)"
                    pattern="[0-2][0-9]:[0-5][0-9]"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    하차 종료시간
                  </label>
                  <input
                    type="text"
                    name="delivery_time_end"
                    value={formData.delivery_time_end}
                    onChange={handleFormChange}
                    placeholder="HH:MM (예: 18:00)"
                    pattern="[0-2][0-9]:[0-5][0-9]"
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
                  onClick={() => {
                    setShowForm(false)
                    setEditingId(null)
                  }}
                >
                  취소
                </button>
                <button 
                  type="submit" 
                  className="button"
                  disabled={uploading}
                >
                  {uploading ? (editingId ? '수정 중...' : '등록 중...') : (editingId ? '수정하기' : '등록하기')}
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
                  <th>작업</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id}>
                    <td><strong>{order.order_number}</strong></td>
                    <td>{order.order_date}</td>
                    <td>{order.product_name}</td>
                    <td><strong>{order.pallet_count}</strong>팔레트</td>
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
                    <td>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                        <button
                          className="button secondary"
                          onClick={() => handleEditOrder(order)}
                          style={{ 
                            padding: '4px 12px',
                            fontSize: '12px',
                            backgroundColor: '#17a2b8',
                            color: 'white'
                          }}
                          title="수정"
                        >
                          ✏️ 수정
                        </button>
                        {order.status === 'PENDING' && (
                          <button
                            className="button"
                            onClick={() => handleDeleteOrder(order.id, order.order_number)}
                            style={{ 
                              padding: '4px 12px',
                              fontSize: '12px',
                              backgroundColor: '#dc3545',
                              color: 'white'
                            }}
                            title="삭제"
                          >
                            🗑️ 삭제
                          </button>
                        )}
                      </div>
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
