import { useState } from 'react'
import { clientsAPI } from '../services/api'

function ClientUpload() {
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
      const response = await clientsAPI.upload(file, true)
      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || '업로드 중 오류가 발생했습니다')
    } finally {
      setUploading(false)
    }
  }

  const downloadTemplate = () => {
    window.open('/api/v1/clients/template', '_blank')
  }

  return (
    <div>
      <div className="card">
        <h2>거래처 마스터 업로드</h2>
        <p style={{ marginBottom: '20px', color: '#666' }}>
          엑셀 파일로 거래처 정보를 일괄 등록합니다. 자동으로 지오코딩을 수행합니다.
        </p>

        <div style={{ marginBottom: '20px' }}>
          <button className="button secondary" onClick={downloadTemplate}>
            📥 템플릿 다운로드
          </button>
        </div>

        {error && <div className="error-message">{error}</div>}
        {result && (
          <div className="success-message">
            <strong>업로드 완료!</strong>
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
        </ol>
      </div>
    </div>
  )
}

export default ClientUpload
