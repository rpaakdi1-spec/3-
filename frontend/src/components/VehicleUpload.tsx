import { useState, useEffect } from 'react'
import { vehiclesAPI } from '../services/api'

interface VehicleForm {
  plate_number: string
  vehicle_type: string
  max_weight_kg: number
  max_pallets: number
  tonnage: number
  temperature_zones: string
  driver_name?: string
  driver_phone?: string
  fuel_efficiency_kmperliter?: number
  notes?: string
}

interface Vehicle {
  id: number
  code: string
  plate_number: string
  vehicle_type: string
  max_weight_kg: number
  max_volume_cbm: number
  max_pallets: number
  temperature_zones: string
  driver_name?: string
  driver_phone?: string
  status: string
}

function VehicleUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string>('')
  const [showForm, setShowForm] = useState(false)
  const [vehicles, setVehicles] = useState<Vehicle[]>([])
  const [loading, setLoading] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState<VehicleForm>({
    plate_number: '',
    vehicle_type: 'FREEZER',
    max_weight_kg: 5000,
    max_pallets: 20,
    tonnage: 5.0,
    temperature_zones: 'frozen',
    driver_name: '',
    driver_phone: '',
    fuel_efficiency_kmperliter: 8,
    notes: ''
  })

  // 컴포넌트 마운트 시 차량 목록 로드
  useEffect(() => {
    loadVehicles()
  }, [])

  // 업로드/등록 성공 시 차량 목록 새로고침
  useEffect(() => {
    if (result && (result.created > 0)) {
      loadVehicles()
    }
  }, [result])

  const loadVehicles = async () => {
    setLoading(true)
    try {
      const response = await vehiclesAPI.list()
      setVehicles(response.data.items || [])
    } catch (err) {
      console.error('Failed to load vehicles:', err)
    } finally {
      setLoading(false)
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
      const response = await vehiclesAPI.upload(file)
      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '업로드 중 오류가 발생했습니다')
    } finally {
      setUploading(false)
    }
  }

  const downloadTemplate = async () => {
    try {
      const response = await vehiclesAPI.downloadTemplate()
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'vehicles_template.xlsx')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      setError('템플릿 다운로드 중 오류가 발생했습니다')
    }
  }

  // 전화번호 포맷팅 함수 (000-0000-0000)
  const formatPhoneNumber = (value: string) => {
    // 숫자만 추출
    const numbers = value.replace(/[^\d]/g, '')
    
    // 포맷팅
    if (numbers.length <= 3) {
      return numbers
    } else if (numbers.length <= 7) {
      return `${numbers.slice(0, 3)}-${numbers.slice(3)}`
    } else if (numbers.length <= 11) {
      return `${numbers.slice(0, 3)}-${numbers.slice(3, 7)}-${numbers.slice(7)}`
    }
    // 11자리 초과는 자름
    return `${numbers.slice(0, 3)}-${numbers.slice(3, 7)}-${numbers.slice(7, 11)}`
  }

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    
    // 전화번호 필드인 경우 포맷팅 적용
    if (name === 'driver_phone') {
      setFormData(prev => ({
        ...prev,
        [name]: formatPhoneNumber(value)
      }))
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: value
      }))
    }
  }

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setUploading(true)
    setError('')
    setResult(null)

    try {
      // Convert English values to Korean for backend
      const vehicleTypeMap: { [key: string]: string } = {
        'FREEZER': '냉동',
        'REFRIGERATED': '냉장',
        'BOTH': '겸용',
        'AMBIENT': '상온'
      }
      
      // 차량 코드는 차량번호로 자동 생성
      const dataToSubmit = {
        ...formData,
        code: formData.plate_number.replace(/[^a-zA-Z0-9]/g, ''), // 특수문자 제거
        vehicle_type: vehicleTypeMap[formData.vehicle_type] || '냉동',
        max_volume_cbm: formData.max_pallets * 1.5 // 팔레트당 평균 1.5 CBM으로 자동 계산
      }
      
      if (editingId) {
        // 수정 모드
        await vehiclesAPI.update(editingId, dataToSubmit)
        setResult({ created: 0, updated: 1, failed: 0, total: 1 })
      } else {
        // 등록 모드
        await vehiclesAPI.create(dataToSubmit)
        setResult({ created: 1, failed: 0, total: 1 })
      }
      
      setShowForm(false)
      setEditingId(null)
      // Reset form
      setFormData({
        plate_number: '',
        vehicle_type: 'FREEZER',
        max_weight_kg: 5000,
        max_pallets: 20,
        tonnage: 5.0,
        temperature_zones: 'frozen',
        driver_name: '',
        driver_phone: '',
        fuel_efficiency_kmperliter: 8,
        notes: ''
      })
      loadVehicles()
    } catch (err: any) {
      setError(err.response?.data?.detail || `${editingId ? '수정' : '등록'} 중 오류가 발생했습니다`)
    } finally {
      setUploading(false)
    }
  }

  const handleEdit = (vehicle: Vehicle) => {
    // 영어 값으로 변환
    const vehicleTypeReverseMap: { [key: string]: string } = {
      '냉동': 'FREEZER',
      '냉장': 'REFRIGERATED',
      '겸용': 'BOTH',
      '상온': 'AMBIENT'
    }
    
    setFormData({
      plate_number: vehicle.plate_number,
      vehicle_type: vehicleTypeReverseMap[vehicle.vehicle_type] || 'FREEZER',
      max_weight_kg: vehicle.max_weight_kg,
      max_pallets: vehicle.max_pallets,
      tonnage: 5.0, // TODO: 백엔드에서 가져오기
      temperature_zones: vehicle.temperature_zones || 'frozen',
      driver_name: vehicle.driver_name || '',
      driver_phone: vehicle.driver_phone ? formatPhoneNumber(vehicle.driver_phone) : '',
      fuel_efficiency_kmperliter: 8,
      notes: ''
    })
    setEditingId(vehicle.id)
    setShowForm(true)
    setError('')
    setResult(null)
  }

  const handleDelete = async (id: number, plate_number: string) => {
    if (!confirm(`차량 "${plate_number}"을(를) 삭제하시겠습니까?`)) {
      return
    }

    try {
      await vehiclesAPI.delete(id)
      setResult({ deleted: 1 })
      loadVehicles()
    } catch (err: any) {
      setError(err.response?.data?.detail || '삭제 중 오류가 발생했습니다')
    }
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setShowForm(false)
    setFormData({
      plate_number: '',
      vehicle_type: 'FREEZER',
      max_weight_kg: 5000,
      max_pallets: 20,
      tonnage: 5.0,
      temperature_zones: 'frozen',
      driver_name: '',
      driver_phone: '',
      fuel_efficiency_kmperliter: 8,
      notes: ''
    })
  }

  const getVehicleTypeLabel = (type: string) => {
    const labels: { [key: string]: string } = {
      'FREEZER': '냉동차',
      'REFRIGERATED': '냉장차',
      'BOTH': '냉동/냉장'
    }
    return labels[type] || type
  }

  const getStatusBadge = (status: string) => {
    const badges: { [key: string]: string } = {
      'AVAILABLE': 'success',
      'IN_USE': 'info',
      'MAINTENANCE': 'warning',
      'UNAVAILABLE': 'error'
    }
    const labels: { [key: string]: string } = {
      'AVAILABLE': '사용가능',
      'IN_USE': '운행중',
      'MAINTENANCE': '정비중',
      'UNAVAILABLE': '사용불가'
    }
    return (
      <span className={`badge ${badges[status] || 'info'}`}>
        {labels[status] || status}
      </span>
    )
  }

  return (
    <div>
      <div className="card">
        <h2>차량 마스터 업로드</h2>
        <p style={{ marginBottom: '20px', color: '#666' }}>
          엑셀 파일로 차량 정보를 일괄 등록하거나 직접 등록할 수 있습니다.
        </p>

        <div style={{ marginBottom: '20px', display: 'flex', gap: '10px' }}>
          <button className="button secondary" onClick={downloadTemplate}>
            📥 템플릿 다운로드
          </button>
          <button 
            className="button" 
            onClick={() => {
              handleCancelEdit()
              setShowForm(!showForm)
            }}
            style={{ backgroundColor: showForm ? '#6c757d' : '#28a745' }}
          >
            {showForm ? '❌ 폼 닫기' : '➕ 직접 등록'}
          </button>
          <button 
            className="button secondary" 
            onClick={loadVehicles}
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
            <h3 style={{ marginBottom: '15px' }}>
              {editingId ? '차량 정보 수정' : '차량 직접 등록'}
            </h3>
            <form onSubmit={handleFormSubmit}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    차량번호 *
                  </label>
                  <input
                    type="text"
                    name="plate_number"
                    value={formData.plate_number}
                    onChange={handleFormChange}
                    required
                    placeholder="예: 서울12가3456"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    차량 유형 *
                  </label>
                  <select
                    name="vehicle_type"
                    value={formData.vehicle_type}
                    onChange={handleFormChange}
                    required
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  >
                    <option value="FREEZER">냉동차</option>
                    <option value="REFRIGERATED">냉장차</option>
                    <option value="BOTH">냉동/냉장</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    온도존 *
                  </label>
                  <select
                    name="temperature_zones"
                    value={formData.temperature_zones}
                    onChange={handleFormChange}
                    required
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  >
                    <option value="frozen">냉동</option>
                    <option value="chilled">냉장</option>
                    <option value="frozen,chilled">냉동/냉장</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    최대 적재량 (kg) *
                  </label>
                  <input
                    type="number"
                    name="max_weight_kg"
                    value={formData.max_weight_kg}
                    onChange={handleFormChange}
                    required
                    min="0"
                    placeholder="예: 5000"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    최대 팔레트 수 *
                  </label>
                  <input
                    type="number"
                    name="max_pallets"
                    value={formData.max_pallets}
                    onChange={handleFormChange}
                    required
                    min="0"
                    placeholder="예: 20"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                  <small style={{ color: '#666', fontSize: '12px' }}>※ 용적은 자동 계산됩니다 (팔레트당 1.5 CBM)</small>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    톤수 *
                  </label>
                  <input
                    type="number"
                    name="tonnage"
                    value={formData.tonnage}
                    onChange={handleFormChange}
                    required
                    min="0"
                    step="0.5"
                    placeholder="예: 5.0"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                  <small style={{ color: '#666', fontSize: '12px' }}>※ 차량 톤수를 입력하세요</small>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    연비 (km/L)
                  </label>
                  <input
                    type="number"
                    name="fuel_efficiency_kmperliter"
                    value={formData.fuel_efficiency_kmperliter}
                    onChange={handleFormChange}
                    min="0"
                    step="0.1"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    운전자명
                  </label>
                  <input
                    type="text"
                    name="driver_name"
                    value={formData.driver_name}
                    onChange={handleFormChange}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    운전자 전화번호
                  </label>
                  <input
                    type="tel"
                    name="driver_phone"
                    value={formData.driver_phone}
                    onChange={handleFormChange}
                    placeholder="000-0000-0000"
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
                  onClick={handleCancelEdit}
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
          <h2 style={{ margin: 0 }}>등록된 차량 목록 ({vehicles.length}대)</h2>
        </div>

        {loading ? (
          <div className="loading">차량 목록을 불러오는 중...</div>
        ) : vehicles.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
            등록된 차량이 없습니다. 차량을 등록해주세요.
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="table">
              <thead>
                <tr>
                  <th>차량번호</th>
                  <th>차량 유형</th>
                  <th>온도존</th>
                  <th>최대 적재량</th>
                  <th>최대 용적</th>
                  <th>최대 팔레트</th>
                  <th>운전자</th>
                  <th>연락처</th>
                  <th>상태</th>
                  <th>관리</th>
                </tr>
              </thead>
              <tbody>
                {vehicles.map((vehicle) => (
                  <tr key={vehicle.id}>
                    <td><strong>{vehicle.plate_number}</strong></td>
                    <td>{getVehicleTypeLabel(vehicle.vehicle_type)}</td>
                    <td>{vehicle.temperature_zones}</td>
                    <td>{vehicle.max_weight_kg.toLocaleString()} kg</td>
                    <td>{vehicle.max_volume_cbm} CBM</td>
                    <td>{vehicle.max_pallets} 개</td>
                    <td>{vehicle.driver_name || '-'}</td>
                    <td>{vehicle.driver_phone ? formatPhoneNumber(vehicle.driver_phone) : '-'}</td>
                    <td>{getStatusBadge(vehicle.status)}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '4px', justifyContent: 'center' }}>
                        <button
                          onClick={() => handleEdit(vehicle)}
                          style={{
                            padding: '4px 8px',
                            fontSize: '12px',
                            backgroundColor: '#007bff',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                          }}
                        >
                          ✏️ 수정
                        </button>
                        <button
                          onClick={() => handleDelete(vehicle.id, vehicle.plate_number)}
                          style={{
                            padding: '4px 8px',
                            fontSize: '12px',
                            backgroundColor: '#dc3545',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer'
                          }}
                        >
                          🗑️ 삭제
                        </button>
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
          <li style={{ marginBottom: '8px' }}>템플릿에 차량 정보를 입력합니다.</li>
          <li style={{ marginBottom: '8px' }}>작성한 파일을 업로드합니다.</li>
          <li style={{ marginBottom: '8px' }}><strong>또는</strong> "직접 등록" 버튼으로 한 건씩 등록할 수 있습니다.</li>
          <li style={{ marginBottom: '8px' }}>등록된 차량은 하단의 차량 목록에서 확인할 수 있습니다.</li>
        </ol>
      </div>
    </div>
  )
}

export default VehicleUpload
