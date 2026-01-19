import { useState } from 'react'
import { clientsAPI } from '../services/api'

interface ClientForm {
  code: string
  name: string
  client_type: string
  address: string
  address_detail?: string
  contact_person?: string
  phone?: string
  has_forklift: boolean
  loading_time_minutes?: number
  pickup_start_time?: string
  pickup_end_time?: string
  delivery_start_time?: string
  delivery_end_time?: string
  notes?: string
}

function ClientUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string>('')
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState<ClientForm>({
    code: '',
    name: '',
    client_type: 'DELIVERY',
    address: '',
    address_detail: '',
    contact_person: '',
    phone: '',
    has_forklift: false,
    loading_time_minutes: 30,
    pickup_start_time: '08:00',
    pickup_end_time: '18:00',
    delivery_start_time: '08:00',
    delivery_end_time: '18:00',
    notes: ''
  })

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
      const response = await clientsAPI.upload(file, true)
      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '업로드 중 오류가 발생했습니다')
    } finally {
      setUploading(false)
    }
  }

  const downloadTemplate = async () => {
    try {
      const response = await clientsAPI.downloadTemplate()
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'clients_template.xlsx')
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (err) {
      setError('템플릿 다운로드 중 오류가 발생했습니다')
    }
  }

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
    }))
  }

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setUploading(true)
    setError('')
    setResult(null)

    try {
      const response = await clientsAPI.create(formData)
      setResult({ created: 1, failed: 0, total: 1 })
      setShowForm(false)
      // Reset form
      setFormData({
        code: '',
        name: '',
        client_type: 'DELIVERY',
        address: '',
        address_detail: '',
        contact_person: '',
        phone: '',
        has_forklift: false,
        loading_time_minutes: 30,
        pickup_start_time: '08:00',
        pickup_end_time: '18:00',
        delivery_start_time: '08:00',
        delivery_end_time: '18:00',
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
        <h2>거래처 마스터 업로드</h2>
        <p style={{ marginBottom: '20px', color: '#666' }}>
          엑셀 파일로 거래처 정보를 일괄 등록하거나 직접 등록할 수 있습니다.
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
            {result.errors && result.errors.length > 0 && (
              <details style={{ marginTop: '12px' }}>
                <summary>오류 상세보기</summary>
                <ul style={{ marginTop: '8px', marginLeft: '20px' }}>
                  {result.errors.map((err: any, idx: number) => (
                    <li key={idx}>
                      행 {err.row}: {err.error}
                    </li>
                  ))}
                </ul>
              </details>
            )}
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
            <h3 style={{ marginBottom: '15px' }}>거래처 직접 등록</h3>
            <form onSubmit={handleFormSubmit}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    거래처 코드 *
                  </label>
                  <input
                    type="text"
                    name="code"
                    value={formData.code}
                    onChange={handleFormChange}
                    required
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    거래처명 *
                  </label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleFormChange}
                    required
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    구분 *
                  </label>
                  <select
                    name="client_type"
                    value={formData.client_type}
                    onChange={handleFormChange}
                    required
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  >
                    <option value="PICKUP">상차</option>
                    <option value="DELIVERY">하차</option>
                    <option value="BOTH">양쪽</option>
                  </select>
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    담당자명
                  </label>
                  <input
                    type="text"
                    name="contact_person"
                    value={formData.contact_person}
                    onChange={handleFormChange}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    주소 *
                  </label>
                  <input
                    type="text"
                    name="address"
                    value={formData.address}
                    onChange={handleFormChange}
                    required
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    상세주소
                  </label>
                  <input
                    type="text"
                    name="address_detail"
                    value={formData.address_detail}
                    onChange={handleFormChange}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    전화번호
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={handleFormChange}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    상하차 소요시간 (분)
                  </label>
                  <input
                    type="number"
                    name="loading_time_minutes"
                    value={formData.loading_time_minutes}
                    onChange={handleFormChange}
                    min="0"
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
                </div>
                <div>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <input
                      type="checkbox"
                      name="has_forklift"
                      checked={formData.has_forklift}
                      onChange={handleFormChange}
                    />
                    <span style={{ fontWeight: 'bold' }}>지게차 유무</span>
                  </label>
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
          <button
            className="button"
            onClick={handleUpload}
            disabled={!file || uploading}
          >
            {uploading ? '업로드 중...' : '업로드 시작'}
          </button>
        </div>
      </div>

      <div className="card">
        <h2>업로드 가이드</h2>
        <ol style={{ marginLeft: '20px', color: '#666' }}>
          <li style={{ marginBottom: '8px' }}>위의 "템플릿 다운로드" 버튼을 클릭하여 엑셀 템플릿을 다운로드합니다.</li>
          <li style={{ marginBottom: '8px' }}>템플릿에 거래처 정보를 입력합니다.</li>
          <li style={{ marginBottom: '8px' }}>작성한 파일을 업로드합니다.</li>
          <li style={{ marginBottom: '8px' }}>시스템이 자동으로 주소를 지오코딩합니다.</li>
          <li style={{ marginBottom: '8px' }}><strong>또는</strong> "직접 등록" 버튼으로 한 건씩 등록할 수 있습니다.</li>
        </ol>
      </div>
    </div>
  )
}

export default ClientUpload
