import React, { useState, useEffect, FormEvent, ChangeEvent } from 'react';

interface PurchaseOrder {
  id: number;
  title: string;
  content?: string;
  image_urls?: string[];
  author: string;
  created_at: string;
}

interface POForm {
  title: string;
  content: string;
  image_urls: string[];
  author: string;
}

const PurchaseOrders: React.FC = () => {
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<PurchaseOrder | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  
  const [formData, setFormData] = useState<POForm>({
    title: '',
    content: '',
    image_urls: [],
    author: '',
  });

  useEffect(() => {
    loadOrders();
    // 이미지 프록시 테스트
    console.log('🔍 이미지 프록시 테스트 시작');
    fetch('/uploads/purchase_orders/test_red.jpg')
      .then(res => {
        console.log('✅ 이미지 프록시 응답:', res.status, res.statusText);
      })
      .catch(err => {
        console.error('❌ 이미지 프록시 실패:', err);
      });
  }, []);

  const loadOrders = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/purchase-orders/');
      const data = await response.json();
      setOrders(data.items || []);
    } catch (error) {
      console.error('발주서 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleImageSelect = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImageFile(e.target.files[0]);
    }
  };

  const handleImageUpload = async () => {
    if (!imageFile) return;
    
    // 최대 5개 제한 확인
    if (formData.image_urls.length >= 5) {
      alert('이미지는 최대 5개까지만 업로드 가능합니다.');
      return;
    }

    setUploadingImage(true);
    try {
      const formData = new FormData();
      formData.append('file', imageFile);

      const response = await fetch('/api/v1/purchase-orders/upload-image/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`업로드 실패: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data.image_url) {
        throw new Error('이미지 URL을 받지 못했습니다');
      }
      
      console.log('업로드된 이미지 URL:', data.image_url);
      setFormData(prev => ({ ...prev, image_urls: [...prev.image_urls, data.image_url] }));
      alert('이미지가 업로드되었습니다!');
      setImageFile(null);
      // 파일 입력 초기화
      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (error) {
      console.error('이미지 업로드 실패:', error);
      alert(`이미지 업로드에 실패했습니다: ${error instanceof Error ? error.message : '알 수 없는 오류'}`);
    } finally {
      setUploadingImage(false);
    }
  };

  const handleFormSubmit = async (e: FormEvent) => {
    e.preventDefault();

    try {
      const url = editingId
        ? `/api/v1/purchase-orders/${editingId}`
        : '/api/v1/purchase-orders/';
      
      const method = editingId ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        alert(editingId ? '발주서가 수정되었습니다!' : '발주서가 등록되었습니다!');
        loadOrders();
        setShowForm(false);
        setEditingId(null);
        setFormData({
          title: '',
          content: '',
          image_urls: [],
          author: '',
        });
      } else {
        const error = await response.json();
        alert(`오류: ${error.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('발주서 저장 실패:', error);
      alert('발주서 저장에 실패했습니다.');
    }
  };

  const handleEdit = (order: PurchaseOrder) => {
    setEditingId(order.id);
    setFormData({
      title: order.title,
      content: order.content || '',
      image_urls: order.image_urls || [],
      author: order.author,
    });
    setShowForm(true);
  };
  
  const handleRemoveImage = (indexToRemove: number) => {
    setFormData(prev => ({
      ...prev,
      image_urls: prev.image_urls.filter((_, index) => index !== indexToRemove)
    }));
  };

  const handleDelete = async (id: number) => {
    if (!confirm('정말로 이 발주서를 삭제하시겠습니까?')) return;

    try {
      const response = await fetch(`/api/v1/purchase-orders/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        alert('발주서가 삭제되었습니다.');
        loadOrders();
      }
    } catch (error) {
      console.error('삭제 실패:', error);
      alert('삭제에 실패했습니다.');
    }
  };

  const handleViewDetail = (order: PurchaseOrder) => {
    setSelectedOrder(order);
  };



  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>📝 발주서 관리</h2>
        <div>
          <button
            onClick={() => {
              setShowForm(!showForm);
              setEditingId(null);
              setFormData({
                po_number: '',
                title: '',
                supplier: '',
                order_date: new Date().toISOString().split('T')[0],
                delivery_date: '',
                total_amount: 0,
                status: '작성중',
                content: '',
                image_url: '',
                author: '',
              });
            }}
            style={{
              padding: '10px 20px',
              backgroundColor: '#4CAF50',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            {showForm ? '폼 닫기' : '✏️ 발주서 작성'}
          </button>
          <button
            onClick={loadOrders}
            style={{
              padding: '10px 20px',
              marginLeft: '10px',
              backgroundColor: '#2196F3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            🔄 새로고침
          </button>
        </div>
      </div>

      {/* 발주서 작성/수정 폼 */}
      {showForm && (
        <div style={{
          backgroundColor: '#f9f9f9',
          padding: '20px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #ddd',
        }}>
          <h3>{editingId ? '발주서 수정' : '발주서 작성'}</h3>
          <form onSubmit={handleFormSubmit}>
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '15px', marginBottom: '15px' }}>
              <div>
                <label>제목 *</label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleFormChange}
                  required
                  placeholder="발주서 제목을 입력하세요"
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                />
              </div>
              <div>
                <label>작성자 *</label>
                <input
                  type="text"
                  name="author"
                  value={formData.author}
                  onChange={handleFormChange}
                  required
                  placeholder="작성자명"
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                />
              </div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label>내용</label>
              <textarea
                name="content"
                value={formData.content}
                onChange={handleFormChange}
                rows={8}
                placeholder="발주 내용을 입력하세요"
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label>이미지 첨부 (최대 5개)</label>
              <div style={{ display: 'flex', gap: '10px', marginTop: '5px' }}>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  disabled={formData.image_urls.length >= 5}
                  style={{ flex: 1 }}
                />
                <button
                  type="button"
                  onClick={handleImageUpload}
                  disabled={!imageFile || uploadingImage || formData.image_urls.length >= 5}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: (imageFile && formData.image_urls.length < 5) ? '#FF9800' : '#ccc',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: (imageFile && formData.image_urls.length < 5) ? 'pointer' : 'not-allowed',
                  }}
                >
                  {uploadingImage ? '업로드 중...' : '📤 업로드'}
                </button>
              </div>
              <div style={{ marginTop: '5px', fontSize: '12px', color: '#757575' }}>
                {formData.image_urls.length}/5개 업로드됨
              </div>
              {formData.image_urls.length > 0 && (
                <div style={{ marginTop: '10px', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '10px' }}>
                  {formData.image_urls.map((url, index) => (
                    <div key={index} style={{ position: 'relative' }}>
                      <img
                        src={url}
                        alt={`Preview ${index + 1}`}
                        style={{ width: '100%', height: '150px', objectFit: 'cover', borderRadius: '4px', border: '1px solid #ddd' }}
                        onLoad={(e) => {
                          console.log('✅ 이미지 로딩 성공:', url);
                          console.log('  - naturalWidth:', e.currentTarget.naturalWidth);
                          console.log('  - naturalHeight:', e.currentTarget.naturalHeight);
                        }}
                        onError={(e) => {
                          console.error('❌ 이미지 로딩 실패:', url);
                          console.error('  - 전체 URL:', window.location.origin + url);
                          console.error('  - currentSrc:', e.currentTarget.currentSrc);
                          
                          const imgElement = e.currentTarget;
                          imgElement.style.display = 'none';
                          
                          // 에러 메시지 표시
                          const errorDiv = document.createElement('div');
                          errorDiv.style.cssText = 'padding: 20px; background: #ffebee; border: 2px dashed #f44336; border-radius: 4px; color: #c62828; text-align: center; font-size: 12px;';
                          errorDiv.innerHTML = `<strong>⚠️ 이미지를 불러올 수 없습니다</strong><br/><small>${url}</small>`;
                          imgElement.parentElement?.appendChild(errorDiv);
                          
                          // 자동 재시도 (1회)
                          setTimeout(() => {
                            console.log('🔄 이미지 재시도:', url);
                            imgElement.src = url + '?retry=' + Date.now();
                            imgElement.style.display = 'block';
                          }, 2000);
                        }}
                      />
                      <button
                        type="button"
                        onClick={() => handleRemoveImage(index)}
                        style={{
                          position: 'absolute',
                          top: '5px',
                          right: '5px',
                          backgroundColor: '#f44336',
                          color: 'white',
                          border: 'none',
                          borderRadius: '50%',
                          width: '24px',
                          height: '24px',
                          cursor: 'pointer',
                          fontSize: '14px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                        title="이미지 삭제"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                type="submit"
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#4CAF50',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                {editingId ? '수정하기' : '등록하기'}
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false);
                  setEditingId(null);
                }}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#757575',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                }}
              >
                취소
              </button>
            </div>
          </form>
        </div>
      )}

      {/* 발주서 상세보기 모달 */}
      {selectedOrder && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000,
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '8px',
            maxWidth: '800px',
            maxHeight: '80vh',
            overflow: 'auto',
          }}>
            <h2>📝 {selectedOrder.title}</h2>
            <div style={{
              backgroundColor: '#f5f5f5',
              padding: '15px',
              borderRadius: '4px',
              marginBottom: '20px',
            }}>
              <div style={{ marginBottom: '10px' }}>
                <strong>작성자:</strong> {selectedOrder.author}
              </div>
              <div>
                <strong>작성일:</strong> {new Date(selectedOrder.created_at).toLocaleString('ko-KR')}
              </div>
            </div>
            {selectedOrder.image_urls && selectedOrder.image_urls.length > 0 && (
              <div style={{ marginBottom: '20px' }}>
                <strong>첨부 이미지 ({selectedOrder.image_urls.length}개):</strong>
                <div style={{ marginTop: '10px', display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '15px' }}>
                  {selectedOrder.image_urls.map((url, index) => (
                    <div key={index}>
                      <img
                        src={url}
                        alt={`발주서 이미지 ${index + 1}`}
                        style={{ width: '100%', height: '200px', objectFit: 'cover', borderRadius: '4px', cursor: 'pointer', border: '1px solid #ddd' }}
                        onClick={() => window.open(url, '_blank')}
                        onLoad={(e) => {
                          console.log('✅ 상세보기 이미지 로딩 성공:', url);
                          console.log('  - 크기:', e.currentTarget.naturalWidth, 'x', e.currentTarget.naturalHeight);
                        }}
                        onError={(e) => {
                          console.error('❌ 상세보기 이미지 로딩 실패:', url);
                          console.error('  - 전체 URL:', window.location.origin + url);
                          console.error('  - currentSrc:', e.currentTarget.currentSrc);
                          
                          const imgElement = e.currentTarget;
                          const alreadyRetried = imgElement.getAttribute('data-retried');
                          
                          if (!alreadyRetried) {
                            // 첫 번째 재시도
                            console.log('🔄 이미지 재시도 (1/2):', url);
                            imgElement.setAttribute('data-retried', '1');
                            setTimeout(() => {
                              imgElement.src = url + '?t=' + Date.now();
                            }, 1000);
                          } else if (alreadyRetried === '1') {
                            // 두 번째 재시도
                            console.log('🔄 이미지 재시도 (2/2):', url);
                            imgElement.setAttribute('data-retried', '2');
                            setTimeout(() => {
                              // API를 통한 직접 접근 시도
                              imgElement.src = window.location.origin + url;
                            }, 1000);
                          } else {
                            // 최종 실패
                            imgElement.style.display = 'none';
                            const errorDiv = document.createElement('div');
                            errorDiv.style.cssText = 'padding: 40px 20px; background: #ffebee; border: 2px dashed #f44336; border-radius: 4px; color: #c62828; text-align: center; font-weight: bold;';
                            errorDiv.innerHTML = `⚠️ 이미지를 불러올 수 없습니다<br/><small style="font-weight: normal; font-size: 12px;">${url}</small><br/><small style="font-weight: normal; font-size: 10px; color: #999;">2회 재시도 실패</small>`;
                            imgElement.parentElement?.appendChild(errorDiv);
                          }
                        }}
                        title="클릭하여 크게 보기"
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
            {selectedOrder.content && (
              <div style={{ marginBottom: '20px' }}>
                <strong>내용:</strong>
                <div style={{ whiteSpace: 'pre-wrap', marginTop: '10px', lineHeight: '1.6', backgroundColor: '#fafafa', padding: '15px', borderRadius: '4px' }}>
                  {selectedOrder.content}
                </div>
              </div>
            )}
            <button
              onClick={() => setSelectedOrder(null)}
              style={{
                padding: '10px 20px',
                backgroundColor: '#757575',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
              }}
            >
              닫기
            </button>
          </div>
        </div>
      )}

      {/* 발주서 목록 */}
      <div>
        <h3>등록된 발주서 ({orders.length}개)</h3>
        {loading ? (
          <p>로딩 중...</p>
        ) : orders.length === 0 ? (
          <p>등록된 발주서가 없습니다.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f5f5f5' }}>
                <th style={{ padding: '12px', border: '1px solid #ddd', width: '60px' }}>번호</th>
                <th style={{ padding: '12px', border: '1px solid #ddd' }}>제목</th>
                <th style={{ padding: '12px', border: '1px solid #ddd', width: '120px' }}>작성자</th>
                <th style={{ padding: '12px', border: '1px solid #ddd', width: '150px' }}>작성일</th>
                <th style={{ padding: '12px', border: '1px solid #ddd', width: '180px' }}>액션</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order, index) => (
                <tr key={order.id} style={{ borderBottom: '1px solid #ddd' }}>
                  <td style={{ padding: '12px', textAlign: 'center', border: '1px solid #ddd' }}>
                    {orders.length - index}
                  </td>
                  <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                    <span
                      onClick={() => handleViewDetail(order)}
                      style={{ cursor: 'pointer', color: '#2196F3', textDecoration: 'underline' }}
                    >
                      {order.title}
                    </span>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', border: '1px solid #ddd' }}>
                    {order.author}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', border: '1px solid #ddd' }}>
                    {new Date(order.created_at).toLocaleDateString('ko-KR')}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', border: '1px solid #ddd' }}>
                    <button
                      onClick={() => handleEdit(order)}
                      style={{
                        padding: '6px 12px',
                        marginRight: '5px',
                        backgroundColor: '#2196F3',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                      }}
                    >
                      수정
                    </button>
                    <button
                      onClick={() => handleDelete(order.id)}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: '#f44336',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                      }}
                    >
                      삭제
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default PurchaseOrders;
