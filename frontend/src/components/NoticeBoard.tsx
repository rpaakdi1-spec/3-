import React, { useState, useEffect, FormEvent, ChangeEvent } from 'react';

interface Notice {
  id: number;
  title: string;
  content: string;
  author: string;
  image_url?: string;
  is_important: boolean;
  views: number;
  created_at: string;
}

interface NoticeForm {
  title: string;
  content: string;
  author: string;
  image_url: string;
  is_important: boolean;
}

const NoticeBoard: React.FC = () => {
  const [notices, setNotices] = useState<Notice[]>([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [selectedNotice, setSelectedNotice] = useState<Notice | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [uploadingImage, setUploadingImage] = useState(false);
  
  const [formData, setFormData] = useState<NoticeForm>({
    title: '',
    content: '',
    author: '',
    image_url: '',
    is_important: false,
  });

  useEffect(() => {
    loadNotices();
  }, []);

  const loadNotices = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/notices/');
      const data = await response.json();
      setNotices(data.items || []);
    } catch (error) {
      console.error('공지사항 로드 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFormChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (e.target as HTMLInputElement).checked : value
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

      const response = await fetch('/api/v1/notices/upload-image/', {
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
        ? `/api/v1/notices/${editingId}`
        : '/api/v1/notices/';
      
      const method = editingId ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        alert(editingId ? '공지사항이 수정되었습니다!' : '공지사항이 등록되었습니다!');
        loadNotices();
        setShowForm(false);
        setEditingId(null);
        setFormData({
          title: '',
          content: '',
          author: '',
          image_url: '',
          is_important: false,
        });
      } else {
        const error = await response.json();
        alert(`오류: ${error.detail || '알 수 없는 오류'}`);
      }
    } catch (error) {
      console.error('공지사항 저장 실패:', error);
      alert('공지사항 저장에 실패했습니다.');
    }
  };

  const handleEdit = (notice: Notice) => {
    setEditingId(notice.id);
    setFormData({
      title: notice.title,
      content: notice.content,
      author: notice.author,
      image_url: notice.image_url || '',
      is_important: notice.is_important,
    });
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm('정말로 이 공지사항을 삭제하시겠습니까?')) return;

    try {
      const response = await fetch(`/api/v1/notices/${id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        alert('공지사항이 삭제되었습니다.');
        loadNotices();
      }
    } catch (error) {
      console.error('삭제 실패:', error);
      alert('삭제에 실패했습니다.');
    }
  };

  const handleViewDetail = async (notice: Notice) => {
    try {
      const response = await fetch(`/api/v1/notices/${notice.id}`);
      const data = await response.json();
      setSelectedNotice(data);
    } catch (error) {
      console.error('공지사항 조회 실패:', error);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>📢 공지사항</h2>
        <div>
          <button
            onClick={() => {
              setShowForm(!showForm);
              setEditingId(null);
              setFormData({
                title: '',
                content: '',
                author: '',
                image_url: '',
                is_important: false,
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
            {showForm ? '폼 닫기' : '✏️ 공지 작성'}
          </button>
          <button
            onClick={loadNotices}
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

      {/* 공지사항 작성/수정 폼 */}
      {showForm && (
        <div style={{
          backgroundColor: '#f9f9f9',
          padding: '20px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #ddd',
        }}>
          <h3>{editingId ? '공지사항 수정' : '공지사항 작성'}</h3>
          <form onSubmit={handleFormSubmit}>
            <div style={{ marginBottom: '15px' }}>
              <label style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
                <input
                  type="checkbox"
                  name="is_important"
                  checked={formData.is_important}
                  onChange={handleFormChange}
                  style={{ marginRight: '8px' }}
                />
                <strong style={{ color: '#f44336' }}>⚠️ 중요 공지</strong>
              </label>
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

            <div style={{ marginBottom: '15px' }}>
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

            <div style={{ marginBottom: '15px' }}>
              <label>내용 *</label>
              <textarea
                name="content"
                value={formData.content}
                onChange={handleFormChange}
                required
                rows={8}
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
                    src={`/${formData.image_url}`}
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

      {/* 공지사항 상세보기 모달 */}
      {selectedNotice && (
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
            position: 'relative',
          }}>
            {selectedNotice.is_important && (
              <div style={{
                backgroundColor: '#ffebee',
                padding: '10px',
                borderRadius: '4px',
                marginBottom: '15px',
                color: '#c62828',
                fontWeight: 'bold',
              }}>
                ⚠️ 중요 공지
              </div>
            )}
            <h2>{selectedNotice.title}</h2>
            <div style={{ color: '#757575', marginBottom: '20px' }}>
              작성자: {selectedNotice.author} | 조회수: {selectedNotice.views} | 
              작성일: {new Date(selectedNotice.created_at).toLocaleString('ko-KR')}
            </div>
            {selectedNotice.image_url && (
              <img
                src={`/${selectedNotice.image_url}`}
                alt="공지사항 이미지"
                style={{ maxWidth: '100%', marginBottom: '20px', borderRadius: '4px' }}
              />
            )}
            <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
              {selectedNotice.content}
            </div>
            <button
              onClick={() => setSelectedNotice(null)}
              style={{
                marginTop: '20px',
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

      {/* 공지사항 목록 */}
      <div>
        <h3>등록된 공지사항 ({notices.length}개)</h3>
        {loading ? (
          <p>로딩 중...</p>
        ) : notices.length === 0 ? (
          <p>등록된 공지사항이 없습니다.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f5f5f5' }}>
                <th style={{ padding: '12px', border: '1px solid #ddd', width: '60px' }}>번호</th>
                <th style={{ padding: '12px', border: '1px solid #ddd' }}>제목</th>
                <th style={{ padding: '12px', border: '1px solid #ddd', width: '120px' }}>작성자</th>
                <th style={{ padding: '12px', border: '1px solid #ddd', width: '80px' }}>조회수</th>
                <th style={{ padding: '12px', border: '1px solid #ddd', width: '150px' }}>작성일</th>
                <th style={{ padding: '12px', border: '1px solid #ddd', width: '180px' }}>액션</th>
              </tr>
            </thead>
            <tbody>
              {notices.map((notice, index) => (
                <tr key={notice.id} style={{ borderBottom: '1px solid #ddd' }}>
                  <td style={{ padding: '12px', textAlign: 'center', border: '1px solid #ddd' }}>
                    {notices.length - index}
                  </td>
                  <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {notice.is_important && (
                        <span style={{ color: '#f44336', fontWeight: 'bold' }}>⚠️</span>
                      )}
                      <span
                        onClick={() => handleViewDetail(notice)}
                        style={{
                          cursor: 'pointer',
                          fontWeight: notice.is_important ? 'bold' : 'normal',
                          color: notice.is_important ? '#f44336' : 'inherit',
                        }}
                      >
                        {notice.title}
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', border: '1px solid #ddd' }}>
                    {notice.author}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', border: '1px solid #ddd' }}>
                    {notice.views}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', border: '1px solid #ddd' }}>
                    {new Date(notice.created_at).toLocaleDateString('ko-KR')}
                  </td>
                  <td style={{ padding: '12px', textAlign: 'center', border: '1px solid #ddd' }}>
                    <button
                      onClick={() => handleEdit(notice)}
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
                      onClick={() => handleDelete(notice.id)}
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

export default NoticeBoard;
