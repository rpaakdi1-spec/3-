import { useEffect, useState } from 'react'
import { dispatchesAPI } from '../services/api'

interface Dispatch {
  id: number
  dispatch_number: string
  dispatch_date: string
  vehicle_code?: string
  vehicle_plate?: string
  driver_name?: string
  total_orders: number
  total_pallets: number
  total_weight_kg: number
  total_distance_km?: number
  estimated_duration_minutes?: number
  status: string
  created_at: string
}

function DispatchList() {
  const [dispatches, setDispatches] = useState<Dispatch[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string>('')
  const [downloading, setDownloading] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [selectedDispatches, setSelectedDispatches] = useState<number[]>([])
  
  // Filters
  const [startDate, setStartDate] = useState<string>('')
  const [endDate, setEndDate] = useState<string>('')
  const [statusFilter, setStatusFilter] = useState<string>('')

  useEffect(() => {
    loadDispatches()
  }, [])

  const loadDispatches = async () => {
    console.log('배차 내역 로드 중...')
    setLoading(true)
    setError('')
    
    try {
      const response = await dispatchesAPI.list()
      console.log('배차 내역 응답:', response.data)
      setDispatches(response.data.items || [])
    } catch (err: any) {
      console.error('Failed to load dispatches:', err)
      setError('배차 내역을 불러오는데 실패했습니다')
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteDispatch = async (dispatchId: number, dispatchNumber: string) => {
    if (!window.confirm(`배차 "${dispatchNumber}"을(를) 삭제하시겠습니까?\n\n확정되었거나 진행 중인 배차는 삭제할 수 없습니다.`)) {
      return
    }

    try {
      await dispatchesAPI.delete(dispatchId)
      setError('')
      // Reload dispatches
      await loadDispatches()
    } catch (err: any) {
      console.error('Dispatch deletion error:', err)
      let errorMessage = '배차 삭제 중 오류가 발생했습니다'
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      }
      setError(errorMessage)
    }
  }

  const handleSelectAll = () => {
    const draftDispatches = dispatches.filter(d => d.status === '임시저장')
    if (selectedDispatches.length === draftDispatches.length && draftDispatches.length > 0) {
      setSelectedDispatches([])
    } else {
      setSelectedDispatches(draftDispatches.map(d => d.id))
    }
  }

  const handleSelectDispatch = (dispatchId: number, status: string) => {
    // Only allow selection of DRAFT dispatches
    if (status !== '임시저장') {
      return
    }

    if (selectedDispatches.includes(dispatchId)) {
      setSelectedDispatches(selectedDispatches.filter(id => id !== dispatchId))
    } else {
      setSelectedDispatches([...selectedDispatches, dispatchId])
    }
  }

  const handleConfirmDispatches = async () => {
    if (selectedDispatches.length === 0) {
      setError('확정할 배차를 선택해주세요')
      return
    }

    if (!window.confirm(`선택한 ${selectedDispatches.length}건의 배차를 확정하시겠습니까?\n\n확정 후에는 수정/삭제가 불가능합니다.`)) {
      return
    }

    setConfirming(true)
    setError('')

    try {
      const response = await dispatchesAPI.confirm(selectedDispatches)
      console.log('배차 확정 응답:', response.data)
      
      // Clear selection and reload
      setSelectedDispatches([])
      await loadDispatches()
      
      // Show success message
      alert(`✅ ${response.data.confirmed}건의 배차가 확정되었습니다.`)
    } catch (err: any) {
      console.error('Dispatch confirmation error:', err)
      let errorMessage = '배차 확정 중 오류가 발생했습니다'
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      }
      setError(errorMessage)
    } finally {
      setConfirming(false)
    }
  }

  const handleDownloadExcel = async () => {
    console.log('엑셀 다운로드 시작...')
    setDownloading(true)
    setError('')

    try {
      const params: any = {}
      if (startDate) params.start_date = startDate
      if (endDate) params.end_date = endDate
      if (statusFilter) params.status = statusFilter

      const response = await dispatchesAPI.downloadExcel(params)
      
      // Create blob and download
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      })
      
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      const today = new Date().toISOString().split('T')[0]
      link.download = `배차내역_${today}.xlsx`
      
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      console.log('엑셀 다운로드 완료')
    } catch (err: any) {
      console.error('Excel download error:', err)
      if (err.response?.status === 404) {
        setError('다운로드할 배차 내역이 없습니다')
      } else {
        setError('엑셀 다운로드 중 오류가 발생했습니다')
      }
    } finally {
      setDownloading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const statusMap: { [key: string]: { label: string; color: string } } = {
      '임시저장': { label: '임시저장', color: '#6c757d' },
      '확정': { label: '확정', color: '#28a745' },
      '진행중': { label: '진행중', color: '#007bff' },
      '완료': { label: '완료', color: '#17a2b8' },
      '취소': { label: '취소', color: '#dc3545' }
    }
    
    const statusInfo = statusMap[status] || { label: status, color: '#6c757d' }
    
    return (
      <span style={{
        padding: '4px 12px',
        borderRadius: '12px',
        fontSize: '12px',
        fontWeight: 500,
        backgroundColor: statusInfo.color,
        color: 'white'
      }}>
        {statusInfo.label}
      </span>
    )
  }

  return (
    <div>
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ margin: 0 }}>📋 AI 배차 내역</h2>
          <div style={{ display: 'flex', gap: '10px' }}>
            {selectedDispatches.length > 0 && (
              <button
                className="button"
                onClick={handleConfirmDispatches}
                disabled={confirming}
                style={{
                  backgroundColor: '#28a745',
                  cursor: confirming ? 'not-allowed' : 'pointer',
                  opacity: confirming ? 0.6 : 1
                }}
              >
                {confirming ? '확정 중...' : `✓ 선택 배차 확정 (${selectedDispatches.length}건)`}
              </button>
            )}
            <button
              className="button"
              onClick={handleDownloadExcel}
              disabled={downloading || dispatches.length === 0}
              style={{
                backgroundColor: '#007bff',
                cursor: downloading || dispatches.length === 0 ? 'not-allowed' : 'pointer',
                opacity: downloading || dispatches.length === 0 ? 0.6 : 1
              }}
            >
              {downloading ? '📥 다운로드 중...' : '📥 엑셀 다운로드'}
            </button>
          </div>
        </div>

        <p style={{ marginBottom: '20px', color: '#666' }}>
          AI가 생성한 배차 내역을 확인하고 엑셀로 다운로드할 수 있습니다.
        </p>

        {/* Filters */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '12px',
          marginBottom: '20px',
          padding: '16px',
          backgroundColor: '#f8f9fa',
          borderRadius: '8px'
        }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 500, fontSize: '14px' }}>
              시작일
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 500, fontSize: '14px' }}>
              종료일
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 500, fontSize: '14px' }}>
              상태
            </label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
            >
              <option value="">전체</option>
              <option value="임시저장">임시저장</option>
              <option value="확정">확정</option>
              <option value="진행중">진행중</option>
              <option value="완료">완료</option>
              <option value="취소">취소</option>
            </select>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button
              className="button secondary"
              onClick={loadDispatches}
              style={{ width: '100%' }}
            >
              🔍 조회
            </button>
          </div>
        </div>

        {error && (
          <div style={{
            padding: '12px',
            marginBottom: '20px',
            backgroundColor: '#f8d7da',
            border: '1px solid #f5c6cb',
            borderRadius: '4px',
            color: '#721c24'
          }}>
            ⚠️ {error}
          </div>
        )}

        <div style={{ marginBottom: '10px', color: '#666' }}>
          총 <strong>{dispatches.length}건</strong>의 배차 내역
          {selectedDispatches.length > 0 && (
            <span style={{ marginLeft: '12px', color: '#28a745', fontWeight: 'bold' }}>
              ✓ {selectedDispatches.length}건 선택됨
            </span>
          )}
        </div>

        {loading ? (
          <div className="loading">배차 내역을 불러오는 중...</div>
        ) : dispatches.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
            배차 내역이 없습니다
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: '50px' }}>
                    <input
                      type="checkbox"
                      checked={selectedDispatches.length > 0 && selectedDispatches.length === dispatches.filter(d => d.status === '임시저장').length}
                      onChange={handleSelectAll}
                      disabled={dispatches.filter(d => d.status === '임시저장').length === 0}
                      style={{ cursor: 'pointer' }}
                      title="임시저장 배차 전체 선택"
                    />
                  </th>
                  <th>배차번호</th>
                  <th>배차일자</th>
                  <th>차량번호</th>
                  <th>기사명</th>
                  <th>주문수</th>
                  <th>팔레트</th>
                  <th>중량(kg)</th>
                  <th>거리(km)</th>
                  <th>예상시간(분)</th>
                  <th>상태</th>
                  <th>생성일시</th>
                  <th style={{ width: '80px' }}>관리</th>
                </tr>
              </thead>
              <tbody>
                {dispatches.map((dispatch) => {
                  const isDraft = dispatch.status === '임시저장'
                  const isSelected = selectedDispatches.includes(dispatch.id)
                  
                  return (
                  <tr 
                    key={dispatch.id}
                    style={{ 
                      backgroundColor: isSelected ? '#e3f2fd' : 'transparent',
                      cursor: isDraft ? 'pointer' : 'default'
                    }}
                    onClick={() => isDraft && handleSelectDispatch(dispatch.id, dispatch.status)}
                  >
                    <td onClick={(e) => e.stopPropagation()}>
                      {isDraft ? (
                        <input
                          type="checkbox"
                          checked={isSelected}
                          onChange={() => handleSelectDispatch(dispatch.id, dispatch.status)}
                          style={{ cursor: 'pointer', width: '18px', height: '18px' }}
                        />
                      ) : (
                        <span style={{ color: '#ccc' }}>-</span>
                      )}
                    </td>
                    <td><strong>{dispatch.dispatch_number}</strong></td>
                    <td>{dispatch.dispatch_date}</td>
                    <td>{dispatch.vehicle_plate || '-'}</td>
                    <td>{dispatch.driver_name || '-'}</td>
                    <td>{dispatch.total_orders}건</td>
                    <td>{dispatch.total_pallets}개</td>
                    <td>{dispatch.total_weight_kg?.toLocaleString() || 0}</td>
                    <td>{dispatch.total_distance_km ? dispatch.total_distance_km.toFixed(2) : '-'}</td>
                    <td>{dispatch.estimated_duration_minutes || '-'}</td>
                    <td>{getStatusBadge(dispatch.status)}</td>
                    <td style={{ fontSize: '12px' }}>
                      {new Date(dispatch.created_at).toLocaleString('ko-KR')}
                    </td>
                    <td>
                      <button
                        onClick={() => handleDeleteDispatch(dispatch.id, dispatch.dispatch_number)}
                        disabled={dispatch.status === '확정' || dispatch.status === '진행중'}
                        style={{
                          padding: '4px 8px',
                          fontSize: '12px',
                          backgroundColor: dispatch.status === '확정' || dispatch.status === '진행중' ? '#ccc' : '#dc3545',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: dispatch.status === '확정' || dispatch.status === '진행중' ? 'not-allowed' : 'pointer',
                          opacity: dispatch.status === '확정' || dispatch.status === '진행중' ? 0.5 : 1
                        }}
                        title={dispatch.status === '확정' || dispatch.status === '진행중' ? '확정/진행중 배차는 삭제 불가' : '배차 삭제'}
                      >
                        🗑️ 삭제
                      </button>
                    </td>
                  </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="card" style={{ marginTop: '20px' }}>
        <h3>💡 사용 가이드</h3>
        <ul style={{ marginLeft: '20px', color: '#666', lineHeight: '1.8' }}>
          <li>AI 배차 최적화로 생성된 모든 배차 내역을 확인할 수 있습니다</li>
          <li><strong>임시저장</strong> 상태의 배차를 선택하여 일괄 확정할 수 있습니다</li>
          <li><strong>확정</strong> 버튼 클릭 시 선택한 배차들이 확정되며, 이후 수정/삭제가 불가능합니다</li>
          <li><strong>엑셀 다운로드</strong> 버튼을 클릭하면 상세 정보가 포함된 엑셀 파일을 받을 수 있습니다</li>
          <li>다운로드된 엑셀에는 <strong>배차일자, 차량번호, 기사명, 상차지주소, 하차지주소</strong> 등이 포함됩니다</li>
          <li>날짜 범위와 상태로 필터링하여 원하는 내역만 조회/다운로드할 수 있습니다</li>
        </ul>
      </div>
    </div>
  )
}

export default DispatchList
