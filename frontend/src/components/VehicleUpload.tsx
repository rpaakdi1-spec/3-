import { useState } from 'react'
import { vehiclesAPI } from '../services/api'

function VehicleUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string>('')

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

  return (
    <div>
      <div className="card">
        <h2>차량 마스터 업로드</h2>
        <p style={{ marginBottom: '20px', color: '#666' }}>
          엑셀 파일로 차량 정보를 일괄 등록합니다.
        </p>

        {error && <div className="error-message">{error}</div>}
        {result && (
          <div className="success-message">
            <strong>업로드 완료!</strong>
            <ul style={{ marginTop: '8px', marginLeft: '20px' }}>
              <li>총 {result.total}건</li>
              <li>성공: {result.created}건</li>
              <li>실패: {result.failed}건</li>
            </ul>
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
    </div>
  )
}

export default VehicleUpload
