/**
 * 관리자용 위치공유 방 관리 페이지
 * - 방 생성 (배차와 독립)
 * - 방 목록 보기 / 상태별 필터링
 * - 기사용/고객사용 링크 복사
 * - 방 상세 (위치 이력, 문서 확인)
 * - 방 완료/취소 처리
 */

import React, { useState, useEffect, useCallback } from 'react';
import apiClient from '../api/client';
import {
  Plus, MapPin, Link2, Copy, Check, CheckCircle,
  Clock, Truck, Building2, FileText, Eye, X,
  RefreshCw, Loader2, AlertCircle, Navigation,
  QrCode, Phone, Car, Trash2, Filter,
  ChevronDown, Upload, Thermometer, Share2
} from 'lucide-react';


interface Room {
  id: number;
  room_code: string;
  title: string;
  status: string;
  driver_name?: string;
  driver_phone?: string;
  vehicle_plate?: string;
  client_name?: string;
  last_latitude?: number;
  last_longitude?: number;
  last_location_at?: string;
  driver_joined_at?: string;
  document_count: number;
  client_view_count: number;
  expires_at?: string;
  created_at: string;
  driver_url: string;
  client_url: string;
}

interface RoomDetail {
  id: number;
  room_code: string;
  title: string;
  description?: string;
  status: string;
  driver_name?: string;
  driver_phone?: string;
  vehicle_plate?: string;
  client_name?: string;
  last_latitude?: number;
  last_longitude?: number;
  last_location_at?: string;
  driver_joined_at?: string;
  driver_last_seen?: string;
  completed_at?: string;
  client_view_count: number;
  expires_at?: string;
  created_at: string;
  notes?: string;
  documents: any[];
  location_history: any[];
  driver_url: string;
  client_url: string;
}

interface CreateForm {
  title: string;
  description: string;
  driver_name: string;
  driver_phone: string;
  vehicle_plate: string;
  client_name: string;
  hours_valid: number;
  notes: string;
}

const STATUS_CONFIG: { [key: string]: { label: string; dot: string; badge: string } } = {
  '대기중': { label: '대기중', dot: 'bg-yellow-400', badge: 'bg-yellow-50 text-yellow-700 border-yellow-200' },
  '진행중': { label: '진행중', dot: 'bg-blue-400 animate-pulse', badge: 'bg-blue-50 text-blue-700 border-blue-200' },
  '완료': { label: '완료', dot: 'bg-green-400', badge: 'bg-green-50 text-green-700 border-green-200' },
  '취소': { label: '취소', dot: 'bg-red-400', badge: 'bg-red-50 text-red-700 border-red-200' },
};

const LocationRoomsPage: React.FC = () => {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [page, setPage] = useState(1);

  // 방 생성 모달
  const [showCreate, setShowCreate] = useState(false);
  const [creating, setCreating] = useState(false);
  const [createForm, setCreateForm] = useState<CreateForm>({
    title: '',
    description: '',
    driver_name: '',
    driver_phone: '',
    vehicle_plate: '',
    client_name: '',
    hours_valid: 48,
    notes: '',
  });

  // 방 상세 모달
  const [selectedRoom, setSelectedRoom] = useState<RoomDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // 링크 복사 상태
  const [copied, setCopied] = useState<string | null>(null);

  // 생성 성공 결과
  const [createdRoom, setCreatedRoom] = useState<any | null>(null);

  const fetchRooms = useCallback(async () => {
    try {
      setLoading(true);
      const params: any = { page, limit: 20 };
      if (statusFilter) params.status = statusFilter;
      const res = await apiClient.get('/rooms', { params });
      setRooms(res.data.items);
      setTotal(res.data.total);
    } catch (err) {
      console.error('방 목록 조회 실패:', err);
    } finally {
      setLoading(false);
    }
  }, [page, statusFilter]);

  useEffect(() => {
    fetchRooms();
  }, [fetchRooms]);

  const copyToClipboard = async (text: string, key: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(key);
      setTimeout(() => setCopied(null), 2000);
    } catch {
      // 폴백
      const el = document.createElement('textarea');
      el.value = text;
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
      setCopied(key);
      setTimeout(() => setCopied(null), 2000);
    }
  };

  const handleCreate = async () => {
    if (!createForm.title.trim()) {
      alert('방 제목을 입력해주세요.');
      return;
    }
    setCreating(true);
    try {
      const res = await apiClient.post('/rooms', {
        title: createForm.title,
        description: createForm.description || undefined,
        driver_name: createForm.driver_name || undefined,
        driver_phone: createForm.driver_phone || undefined,
        vehicle_plate: createForm.vehicle_plate || undefined,
        client_name: createForm.client_name || undefined,
        hours_valid: createForm.hours_valid,
        notes: createForm.notes || undefined,
      });
      setCreatedRoom(res.data);
      fetchRooms();
    } catch (err: any) {
      alert(err.response?.data?.detail || '방 생성에 실패했습니다.');
    } finally {
      setCreating(false);
    }
  };

  const handleViewDetail = async (roomId: number) => {
    setDetailLoading(true);
    setSelectedRoom(null);
    try {
      const res = await apiClient.get(`/rooms/${roomId}`);
      setSelectedRoom(res.data);
    } catch (err) {
      alert('상세 정보를 불러올 수 없습니다.');
    } finally {
      setDetailLoading(false);
    }
  };

  const handleStatusChange = async (roomId: number, newStatus: string) => {
    if (!window.confirm(`상태를 '${newStatus}'(으)로 변경하시겠습니까?`)) return;
    try {
      await apiClient.patch(`/rooms/${roomId}/status?new_status=${encodeURIComponent(newStatus)}`);
      fetchRooms();
      if (selectedRoom?.id === roomId) {
        setSelectedRoom(prev => prev ? { ...prev, status: newStatus } : null);
      }
    } catch (err: any) {
      alert(err.response?.data?.detail || '상태 변경에 실패했습니다.');
    }
  };

  const handleDelete = async (roomId: number) => {
    if (!window.confirm('방을 삭제하시겠습니까? 모든 위치 기록과 서류가 삭제됩니다.')) return;
    try {
      await apiClient.delete(`/rooms/${roomId}`);

      fetchRooms();
      if (selectedRoom?.id === roomId) setSelectedRoom(null);
    } catch (err: any) {
      alert(err.response?.data?.detail || '삭제에 실패했습니다.');
    }
  };

  const resetCreateForm = () => {
    setCreateForm({
      title: '', description: '', driver_name: '', driver_phone: '',
      vehicle_plate: '', client_name: '', hours_valid: 48, notes: ''
    });
    setCreatedRoom(null);
    setShowCreate(false);
  };

  const getFullUrl = (path: string) => {
    // path가 http로 시작하면 그대로, 아니면 현재 origin + path
    if (path.startsWith('http')) return path;
    return `${window.location.origin}${path.startsWith('/') ? path : '/' + path}`;
  };

  // ====== 렌더링 ======

  return (
    <div className="p-4 md:p-6 max-w-6xl mx-auto">
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <MapPin className="text-blue-600" size={26} />
            위치공유 방 관리
          </h1>
          <p className="text-gray-500 text-sm mt-1">배차와 독립적으로 방을 만들어 기사 위치를 고객사에 공유합니다</p>
        </div>
        <button
          onClick={() => { setShowCreate(true); setCreatedRoom(null); }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors shadow-sm"
        >
          <Plus size={18} />
          방 만들기
        </button>
      </div>

      {/* 상태 필터 + 새로고침 */}
      <div className="flex flex-wrap items-center gap-2 mb-4">
        <div className="flex gap-1.5 flex-wrap">
          {['', '대기중', '진행중', '완료', '취소'].map(s => (
            <button
              key={s}
              onClick={() => { setStatusFilter(s); setPage(1); }}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium border transition-colors ${
                statusFilter === s
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-600 border-gray-200 hover:bg-gray-50'
              }`}
            >
              {s === '' ? '전체' : s}
            </button>
          ))}
        </div>
        <button
          onClick={fetchRooms}
          className="ml-auto p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
          title="새로고침"
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
        </button>
        <span className="text-sm text-gray-500">총 {total}개</span>
      </div>

      {/* 방 목록 */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="animate-spin text-blue-500" size={32} />
        </div>
      ) : rooms.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <MapPin size={48} className="mx-auto mb-3 opacity-20" />
          <p className="text-lg">방이 없습니다</p>
          <p className="text-sm">위에서 '방 만들기' 버튼을 눌러 시작하세요</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {rooms.map(room => {
            const sc = STATUS_CONFIG[room.status] || STATUS_CONFIG['대기중'];
            return (
              <div
                key={room.id}
                className="bg-white rounded-2xl shadow-sm border hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleViewDetail(room.id)}
              >
                <div className="p-4">
                  {/* 상태 + 코드 */}
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${sc.dot}`} />
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${sc.badge}`}>
                        {sc.label}
                      </span>
                    </div>
                    <span className="font-mono text-xs text-gray-400 bg-gray-50 px-2 py-1 rounded-lg">
                      {room.room_code}
                    </span>
                  </div>

                  {/* 제목 */}
                  <h3 className="font-semibold text-gray-900 text-sm mb-2 line-clamp-2 leading-tight">
                    {room.title}
                  </h3>

                  {/* 정보 */}
                  <div className="space-y-1 text-xs text-gray-500">
                    {room.driver_name && (
                      <div className="flex items-center gap-1.5">
                        <Truck size={11} className="text-gray-400" />
                        <span>{room.driver_name}</span>
                        {room.vehicle_plate && <span className="text-gray-400">· {room.vehicle_plate}</span>}
                      </div>
                    )}
                    {room.client_name && (
                      <div className="flex items-center gap-1.5">
                        <Building2 size={11} className="text-gray-400" />
                        <span>{room.client_name}</span>
                      </div>
                    )}
                    {room.last_location_at && (
                      <div className="flex items-center gap-1.5 text-blue-500">
                        <Navigation size={11} />
                        <span>위치 수신 {new Date(room.last_location_at).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}</span>
                      </div>
                    )}
                  </div>

                  {/* 하단 통계 */}
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-gray-100 text-xs text-gray-400">
                    <div className="flex gap-3">
                      <span className="flex items-center gap-1">
                        <FileText size={11} /> {room.document_count}
                      </span>
                      <span className="flex items-center gap-1">
                        <Eye size={11} /> {room.client_view_count}
                      </span>
                    </div>
                    <span>{new Date(room.created_at).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}</span>
                  </div>
                </div>

                {/* 링크 버튼 */}
                <div className="px-4 pb-4 grid grid-cols-2 gap-2" onClick={e => e.stopPropagation()}>
                  <LinkCopyButton
                    label="기사 링크"
                    color="blue"
                    url={getFullUrl(room.driver_url)}
                    copyKey={`driver_${room.id}`}
                    copied={copied}
                    onCopy={copyToClipboard}
                  />
                  <LinkCopyButton
                    label="고객 링크"
                    color="purple"
                    url={getFullUrl(room.client_url)}
                    copyKey={`client_${room.id}`}
                    copied={copied}
                    onCopy={copyToClipboard}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ====== 방 생성 모달 ====== */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 z-40 flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl w-full max-w-lg my-4 overflow-hidden shadow-xl">
            {/* 모달 헤더 */}
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <h2 className="text-lg font-bold text-gray-900">
                {createdRoom ? '방이 생성되었습니다 🎉' : '새 위치공유 방 만들기'}
              </h2>
              <button onClick={resetCreateForm} className="p-1 text-gray-400 hover:text-gray-600 rounded-lg">
                <X size={20} />
              </button>
            </div>

            {createdRoom ? (
              // 생성 완료 화면
              <div className="p-6 space-y-4">
                <div className="bg-gray-50 rounded-xl p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="font-mono text-2xl font-bold text-blue-600">{createdRoom.room_code}</span>
                    <span className="text-sm text-gray-500">방 코드</span>
                  </div>
                  <p className="text-sm text-gray-600 font-medium">{createdRoom.title}</p>
                </div>

                <div className="space-y-3">
                  <LinkShareCard
                    title="🚛 기사용 링크"
                    subtitle="기사에게 이 링크를 공유하세요"
                    url={getFullUrl(createdRoom.driver_url)}
                    color="blue"
                    copyKey="new_driver"
                    copied={copied}
                    onCopy={copyToClipboard}
                  />
                  <LinkShareCard
                    title="🏢 고객사용 링크"
                    subtitle="고객사에게 이 링크를 공유하세요"
                    url={getFullUrl(createdRoom.client_url)}
                    color="purple"
                    copyKey="new_client"
                    copied={copied}
                    onCopy={copyToClipboard}
                  />
                </div>

                <button
                  onClick={resetCreateForm}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors"
                >
                  확인
                </button>
              </div>
            ) : (
              // 방 생성 폼
              <div className="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    방 제목 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={createForm.title}
                    onChange={e => setCreateForm(p => ({ ...p, title: e.target.value }))}
                    placeholder="예: 2026-03-13 서울→부산 냉동운송"
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">기사 이름</label>
                    <input
                      type="text"
                      value={createForm.driver_name}
                      onChange={e => setCreateForm(p => ({ ...p, driver_name: e.target.value }))}
                      placeholder="홍길동"
                      className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">기사 연락처</label>
                    <input
                      type="tel"
                      value={createForm.driver_phone}
                      onChange={e => setCreateForm(p => ({ ...p, driver_phone: e.target.value }))}
                      placeholder="010-0000-0000"
                      className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">차량 번호</label>
                    <input
                      type="text"
                      value={createForm.vehicle_plate}
                      onChange={e => setCreateForm(p => ({ ...p, vehicle_plate: e.target.value }))}
                      placeholder="12가 3456"
                      className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">고객사명</label>
                    <input
                      type="text"
                      value={createForm.client_name}
                      onChange={e => setCreateForm(p => ({ ...p, client_name: e.target.value }))}
                      placeholder="(주)냉동유통"
                      className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">유효 시간</label>
                  <select
                    value={createForm.hours_valid}
                    onChange={e => setCreateForm(p => ({ ...p, hours_valid: Number(e.target.value) }))}
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value={12}>12시간</option>
                    <option value={24}>24시간</option>
                    <option value={48}>48시간</option>
                    <option value={72}>72시간</option>
                    <option value={168}>7일</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">메모 (내부용)</label>
                  <textarea
                    value={createForm.notes}
                    onChange={e => setCreateForm(p => ({ ...p, notes: e.target.value }))}
                    placeholder="내부 메모를 입력하세요..."
                    rows={2}
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  />
                </div>

                <button
                  onClick={handleCreate}
                  disabled={creating}
                  className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-xl font-bold transition-colors flex items-center justify-center gap-2"
                >
                  {creating ? (
                    <><Loader2 size={18} className="animate-spin" /> 생성 중...</>
                  ) : (
                    <><Plus size={18} /> 방 생성하기</>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ====== 방 상세 모달 ====== */}
      {(selectedRoom || detailLoading) && (
        <div className="fixed inset-0 bg-black/50 z-40 flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl w-full max-w-2xl my-4 overflow-hidden shadow-xl">
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <h2 className="font-bold text-gray-900 flex items-center gap-2">
                <MapPin size={18} className="text-blue-600" />
                {selectedRoom?.title || '로딩 중...'}
              </h2>
              <button
                onClick={() => setSelectedRoom(null)}
                className="p-1 text-gray-400 hover:text-gray-600 rounded-lg"
              >
                <X size={20} />
              </button>
            </div>

            {detailLoading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="animate-spin text-blue-500" size={32} />
              </div>
            ) : selectedRoom ? (
              <div className="p-6 space-y-4 max-h-[75vh] overflow-y-auto">
                {/* 방 코드 + 상태 */}
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xl font-bold text-blue-600">{selectedRoom.room_code}</span>
                  <span className={`text-sm px-2 py-1 rounded-full border ${STATUS_CONFIG[selectedRoom.status]?.badge || ''}`}>
                    {selectedRoom.status}
                  </span>
                </div>

                {/* 기본 정보 */}
                <div className="bg-gray-50 rounded-xl p-4 grid grid-cols-2 gap-3 text-sm">
                  {selectedRoom.driver_name && (
                    <div><span className="text-gray-500">기사</span><br /><strong>{selectedRoom.driver_name}</strong></div>
                  )}
                  {selectedRoom.driver_phone && (
                    <div><span className="text-gray-500">연락처</span><br /><strong>{selectedRoom.driver_phone}</strong></div>
                  )}
                  {selectedRoom.vehicle_plate && (
                    <div><span className="text-gray-500">차량번호</span><br /><strong>{selectedRoom.vehicle_plate}</strong></div>
                  )}
                  {selectedRoom.client_name && (
                    <div><span className="text-gray-500">고객사</span><br /><strong>{selectedRoom.client_name}</strong></div>
                  )}
                  {selectedRoom.driver_joined_at && (
                    <div><span className="text-gray-500">기사 입장</span><br /><strong>{new Date(selectedRoom.driver_joined_at).toLocaleString('ko-KR')}</strong></div>
                  )}
                  {selectedRoom.driver_last_seen && (
                    <div><span className="text-gray-500">마지막 활동</span><br /><strong>{new Date(selectedRoom.driver_last_seen).toLocaleString('ko-KR')}</strong></div>
                  )}
                  <div><span className="text-gray-500">고객 조회</span><br /><strong>{selectedRoom.client_view_count}회</strong></div>
                  <div><span className="text-gray-500">위치 기록</span><br /><strong>{selectedRoom.location_history.length}건</strong></div>
                </div>

                {/* 현재 위치 */}
                {selectedRoom.last_latitude && (
                  <div className="bg-blue-50 border border-blue-200 rounded-xl p-3 text-sm">
                    <div className="flex items-center gap-2 text-blue-700 font-medium mb-1">
                      <Navigation size={14} />
                      현재 위치
                    </div>
                    <p className="text-blue-600 text-xs">
                      {selectedRoom.last_latitude.toFixed(6)}, {selectedRoom.last_longitude?.toFixed(6)}
                    </p>
                    {selectedRoom.last_location_at && (
                      <p className="text-blue-500 text-xs">{new Date(selectedRoom.last_location_at).toLocaleString('ko-KR')}</p>
                    )}
                  </div>
                )}

                {/* 링크 */}
                <div className="space-y-2">
                  <LinkShareCard
                    title="🚛 기사용 링크"
                    subtitle="기사에게 공유"
                    url={getFullUrl(selectedRoom.driver_url)}
                    color="blue"
                    copyKey={`detail_driver_${selectedRoom.id}`}
                    copied={copied}
                    onCopy={copyToClipboard}
                  />
                  <LinkShareCard
                    title="🏢 고객사용 링크"
                    subtitle="고객사에게 공유"
                    url={getFullUrl(selectedRoom.client_url)}
                    color="purple"
                    copyKey={`detail_client_${selectedRoom.id}`}
                    copied={copied}
                    onCopy={copyToClipboard}
                  />
                </div>

                {/* 업로드된 서류 */}
                {selectedRoom.documents.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
                      <FileText size={15} /> 업로드된 서류 ({selectedRoom.documents.length}건)
                    </h4>
                    <div className="space-y-2">
                      {selectedRoom.documents.map((doc: any) => (
                        <div key={doc.id} className="flex items-center gap-3 bg-gray-50 rounded-xl p-3">
                          {doc.document_type === '온도기록지' ? (
                            <Thermometer size={16} className="text-red-400" />
                          ) : (
                            <FileText size={16} className="text-blue-400" />
                          )}
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-800">{doc.document_type}</p>
                            <p className="text-xs text-gray-500">
                              <span className={`mr-2 px-1.5 py-0.5 rounded text-xs ${
                                doc.stage === '출발' ? 'bg-blue-100 text-blue-600' : 'bg-orange-100 text-orange-600'
                              }`}>{doc.stage}</span>
                              {new Date(doc.created_at).toLocaleString('ko-KR')}
                            </p>
                          </div>
                          <a
                            href={doc.file_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1.5 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                          >
                            <Eye size={15} />
                          </a>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 상태 변경 버튼 */}
                <div className="flex flex-wrap gap-2 pt-2 border-t">
                  {selectedRoom.status !== '완료' && (
                    <button
                      onClick={() => handleStatusChange(selectedRoom.id, '완료')}
                      className="px-3 py-2 bg-green-50 hover:bg-green-100 text-green-700 border border-green-200 rounded-xl text-sm font-medium transition-colors flex items-center gap-1.5"
                    >
                      <CheckCircle size={14} /> 완료 처리
                    </button>
                  )}
                  {selectedRoom.status !== '취소' && selectedRoom.status !== '완료' && (
                    <button
                      onClick={() => handleStatusChange(selectedRoom.id, '취소')}
                      className="px-3 py-2 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded-xl text-sm font-medium transition-colors flex items-center gap-1.5"
                    >
                      <X size={14} /> 취소
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(selectedRoom.id)}
                    className="px-3 py-2 bg-gray-50 hover:bg-gray-100 text-gray-600 border border-gray-200 rounded-xl text-sm font-medium transition-colors flex items-center gap-1.5 ml-auto"
                  >
                    <Trash2 size={14} /> 삭제
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  );
};

// ====== 서브 컴포넌트 ======

interface LinkCopyButtonProps {
  label: string;
  color: 'blue' | 'purple';
  url: string;
  copyKey: string;
  copied: string | null;
  onCopy: (url: string, key: string) => void;
}

const LinkCopyButton: React.FC<LinkCopyButtonProps> = ({ label, color, url, copyKey, copied, onCopy }) => {
  const isCopied = copied === copyKey;
  const colorClass = color === 'blue'
    ? 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100'
    : 'bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100';

  return (
    <button
      onClick={() => onCopy(url, copyKey)}
      className={`flex items-center justify-center gap-1.5 py-2 rounded-xl border text-xs font-medium transition-colors ${colorClass}`}
    >
      {isCopied ? <Check size={12} /> : <Copy size={12} />}
      {isCopied ? '복사됨!' : label}
    </button>
  );
};

interface LinkShareCardProps {
  title: string;
  subtitle: string;
  url: string;
  color: 'blue' | 'purple';
  copyKey: string;
  copied: string | null;
  onCopy: (url: string, key: string) => void;
}

const LinkShareCard: React.FC<LinkShareCardProps> = ({ title, subtitle, url, color, copyKey, copied, onCopy }) => {
  const isCopied = copied === copyKey;
  const borderColor = color === 'blue' ? 'border-blue-200' : 'border-purple-200';
  const btnColor = color === 'blue'
    ? 'bg-blue-600 hover:bg-blue-700 text-white'
    : 'bg-purple-600 hover:bg-purple-700 text-white';

  return (
    <div className={`border ${borderColor} rounded-xl p-3`}>
      <div className="flex items-center justify-between mb-1.5">
        <div>
          <p className="font-semibold text-gray-800 text-sm">{title}</p>
          <p className="text-xs text-gray-500">{subtitle}</p>
        </div>
        <button
          onClick={() => onCopy(url, copyKey)}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${btnColor}`}
        >
          {isCopied ? '✓ 복사됨!' : '링크 복사'}
        </button>
      </div>
      <p className="text-xs text-gray-400 font-mono truncate bg-gray-50 px-2 py-1 rounded-lg">{url}</p>
    </div>
  );
};

export default LocationRoomsPage;
