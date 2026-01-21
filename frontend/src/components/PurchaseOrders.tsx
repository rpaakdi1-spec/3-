import React, { useState, useEffect, FormEvent, ChangeEvent } from 'react';

interface PurchaseOrder {
  id: number;
  po_number: string;
  title: string;
  supplier: string;
  order_date: string;
  delivery_date?: string;
  total_amount: number;
  status: string;
  content?: string;
  image_url?: string;
  author: string;
  created_at: string;
}

interface POForm {
  po_number: string;
  title: string;
  supplier: string;
  order_date: string;
  delivery_date: string;
  total_amount: number;
  status: string;
  content: string;
  image_url: string;
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

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/purchase-orders/');
      const data = await response.json();
      setOrders(data.items || []);
    } catch (error) {
      console.error('발주서 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'total_amount' ? parseFloat(value) || 0 : value
    }));
  };

  const handleImageSelect = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImageFile(e.target.files[0]);
    }
  };

  const handleImageUpload = async () => {
    if (!imageFile) return;

    setUploadingImage(true);
    try {
      const formData = new FormData();
      formData.append('file', imageFile);

      const response = await fetch('http://localhost:8000/api/v1/purchase-orders/upload-image/', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setFormData(prev => ({ ...prev, image_url: data.image_url }));
      alert('이미지가 업로드되었습니다!');
      setImageFile(null);
    } catch (error) {
      console.error('이미지 업로드 실패:', error);
      alert('이미지 업로드에 실패했습니다.');
    } finally {
      setUploadingImage(false);
    }
  };

  const handleFormSubmit = async (e: FormEvent) => {
    e.preventDefault();

    try {
      const url = editingId
        ? `http://localhost:8000/api/v1/purchase-orders/${editingId}`
        : 'http://localhost:8000/api/v1/purchase-orders/';
      
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
      po_number: order.po_number,
      title: order.title,
      supplier: order.supplier,
      order_date: order.order_date,
      delivery_date: order.delivery_date || '',
      total_amount: order.total_amount,
      status: order.status,
      content: order.content || '',
      image_url: order.image_url || '',
      author: order.author,
    });
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('정말로 이 발주서를 삭제하시겠습니까?')) return;

    try {
      const response = await fetch(`http://localhost:8000/api/v1/purchase-orders/${id}`, {
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case '작성중': return '#FF9800';
      case '발송완료': return '#2196F3';
      case '승인': return '#4CAF50';
      case '취소': return '#f44336';
      default: return '#757575';
    }
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
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '15px' }}>
              <div>
                <label>발주서 번호 *</label>
                <input
                  type="text"
                  name="po_number"
                  value={formData.po_number}
                  onChange={handleFormChange}
                  required
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
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                />
              </div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label>제목 *</label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleFormChange}
                required
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '15px' }}>
              <div>
                <label>공급업체 *</label>
                <input
                  type="text"
                  name="supplier"
                  value={formData.supplier}
                  onChange={handleFormChange}
                  required
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                />
              </div>
              <div>
                <label>총 금액</label>
                <input
                  type="number"
                  name="total_amount"
                  value={formData.total_amount}
                  onChange={handleFormChange}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                />
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px', marginBottom: '15px' }}>
              <div>
                <label>발주일 *</label>
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
                <label>희망 납기일</label>
                <input
                  type="date"
                  name="delivery_date"
                  value={formData.delivery_date}
                  onChange={handleFormChange}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                />
              </div>
              <div>
                <label>상태</label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleFormChange}
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                >
                  <option value="작성중">작성중</option>
                  <option value="발송완료">발송완료</option>
                  <option value="승인">승인</option>
                  <option value="취소">취소</option>
                </select>
              </div>
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label>발주 내용 및 특이사항</label>
              <textarea
                name="content"
                value={formData.content}
                onChange={handleFormChange}
                rows={6}
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
              />
            </div>

            <div style={{ marginBottom: '15px' }}>
              <label>이미지 첨부</label>
              <div style={{ display: 'flex', gap: '10px', marginTop: '5px' }}>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  style={{ flex: 1 }}
                />
                <button
                  type="button"
                  onClick={handleImageUpload}
                  disabled={!imageFile || uploadingImage}
                  style={{
                    padding: '8px 16px',
                    backgroundColor: imageFile ? '#FF9800' : '#ccc',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: imageFile ? 'pointer' : 'not-allowed',
                  }}
                >
                  {uploadingImage ? '업로드 중...' : '📤 업로드'}
                </button>
              </div>
              {formData.image_url && (
                <div style={{ marginTop: '10px' }}>
                  <img
                    src={`http://localhost:8000${formData.image_url}`}
                    alt="Preview"
                    style={{ maxWidth: '200px', borderRadius: '4px', border: '1px solid #ddd' }}
                  />
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
                <strong>발주서 번호:</strong> {selectedOrder.po_number}
              </div>
              <div style={{ marginBottom: '10px' }}>
                <strong>공급업체:</strong> {selectedOrder.supplier}
              </div>
              <div style={{ marginBottom: '10px' }}>
                <strong>발주일:</strong> {selectedOrder.order_date}
              </div>
              {selectedOrder.delivery_date && (
                <div style={{ marginBottom: '10px' }}>
                  <strong>희망 납기일:</strong> {selectedOrder.delivery_date}
                </div>
              )}
              <div style={{ marginBottom: '10px' }}>
                <strong>총 금액:</strong> {selectedOrder.total_amount.toLocaleString()}원
              </div>
              <div style={{ marginBottom: '10px' }}>
                <strong>상태:</strong>{' '}
                <span style={{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  backgroundColor: getStatusColor(selectedOrder.status),
                  color: 'white',
                }}>
                  {selectedOrder.status}
                </span>
              </div>
              <div>
                <strong>작성자:</strong> {selectedOrder.author}
              </div>
            </div>
            {selectedOrder.image_url && (
              <img
                src={`http://localhost:8000${selectedOrder.image_url}`}
                alt="발주서 이미지"
                style={{ maxWidth: '100%', marginBottom: '20px', borderRadius: '4px' }}
              />
            )}
            {selectedOrder.content && (
              <div style={{ marginBottom: '20px' }}>
                <strong>발주 내용:</strong>
                <div style={{ whiteSpace: 'pre-wrap', marginTop: '10px', lineHeight: '1.6' }}>
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
                <th style={{ padding: '12px', border: '1px solid #ddd' }}>발주서 번호</th>
                <th style={{ padding: '12px', border: '1px solid #ddd' }}>제목</th>
                <th style={{ padding: '12px', border: '1px solid #ddd' }}>공급업체</th>
                <th style={{ padding: '12px', border: '1px solid #ddd' }}>발주일</th>
                <th style={{ padding: '12px', border: '1px solid #ddd' }}>총 금액</th>
                <th style={{ padding: '12px', border: '1px solid #ddd' }}>상태</th>
                <th style={{ padding: '12px', border: '1px solid #ddd' }}>액션</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.id} style={{ borderBottom: '1px solid #ddd' }}>
                  <td style={{ padding: '12px', textAlign: 'center', border: '1px solid #ddd' }}>
                    <span
                      onClick={() => handleViewDetail(order)}
                      style={{ cursor: 'pointer', color: '#2196F3', textDecoration: 'underline' }}
                    >
                      {order.po_number}
                    </span>
                  </td>
                  <td style={{ padding: '12px', border: '1px solid #ddd' }}>{order.title}</td>
                  <td style={{ padding: '12px', border: '1px solid #ddd' }}>{order.supplier}</td>
                  <td style={{ padding: '12px', textAlign: 'center', border: '1px solid #ddd' }}>
                    {order.order_date}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'right', border: '1px solid #ddd' }}>
                    {order.total_amount.toLocaleString()}원
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', border: '1px solid #ddd' }}>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      backgroundColor: getStatusColor(order.status),
                      color: 'white',
                      fontSize: '12px',
                    }}>
                      {order.status}
                    </span>
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
