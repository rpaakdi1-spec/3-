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
  // 상차지
  loading_name?: string;
  loading_address?: string;
  loading_lat?: number;
  loading_lng?: number;
  // 하차지
  unloading_name?: string;
  unloading_address?: string;
  unloading_lat?: number;
  unloading_lng?: number;
  // 운행 타임라인
  arrived_at_loading?: string;
  departed_loading?: string;
  arrived_at_unloading?: string;
  departed_unloading?: string;
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
  // 상차지
  loading_name: string;
  loading_address: string;
  loading_lat: string;
  loading_lng: string;
  // 하차지
  unloading_name: string;
  unloading_address: string;
  unloading_lat: string;
  unloading_lng: string;
}

interface MonitoringVehicle {
  id: number;
  plate_number: string;
  vehicle_type: string;
  driver_name?: string;
  last_gps_time?: string;
  last_lat?: number;
  last_lng?: number;
  last_speed?: number;
  is_engine_on?: boolean;
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
    loading_name: '',
    loading_address: '',
    loading_lat: '',
    loading_lng: '',
    unloading_name: '',
    unloading_address: '',
    unloading_lat: '',
    unloading_lng: '',
  });
  const [monitoringVehicles, setMonitoringVehicles] = useState<MonitoringVehicle[]>([]);
  const [vehiclesLoading, setVehiclesLoading] = useState(false);
  const [showVehiclePicker, setShowVehiclePicker] = useState(false);

  // 방 상세 모달
  const [selectedRoom, setSelectedRoom] = useState<RoomDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  // GPS 이력 탭
  const [gpsTab, setGpsTab] = useState(false);
  const [gpsDate, setGpsDate] = useState('');
  const [gpsAvailDates, setGpsAvailDates] = useState<string[]>([]);
  const [gpsHistory, setGpsHistory] = useState<any[]>([]);
  const [gpsLoading, setGpsLoading] = useState(false);
  const [gpsMessage, setGpsMessage] = useState<string | null>(null);

  // 링크 복사 상태
  const [copied, setCopied] = useState<string | null>(null);

  // 생성 성공 결과
  const [createdRoom, setCreatedRoom] = useState<any | null>(null);

  // 실시간모니터링 차량 목록 불러오기
  const loadMonitoringVehicles = async () => {
    setVehiclesLoading(true);
    try {
      const res = await apiClient.get('/rooms/vehicles/monitoring-list');
      setMonitoringVehicles(res.data?.items ?? []);
    } catch {
      setMonitoringVehicles([]);
    } finally {
      setVehiclesLoading(false);
    }
  };

  const handleSelectVehicle = (v: MonitoringVehicle) => {
    setCreateForm(p => ({ ...p, vehicle_plate: v.plate_number, driver_name: p.driver_name || v.driver_name || '' }));
    setShowVehiclePicker(false);
  };

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
      const body: any = {
        title: createForm.title,
        description: createForm.description || undefined,
        driver_name: createForm.driver_name || undefined,
        driver_phone: createForm.driver_phone || undefined,
        vehicle_plate: createForm.vehicle_plate || undefined,
        client_name: createForm.client_name || undefined,
        hours_valid: createForm.hours_valid,
        notes: createForm.notes || undefined,
      };
      // 상차지
      if (createForm.loading_name) body.loading_name = createForm.loading_name;
      if (createForm.loading_address) body.loading_address = createForm.loading_address;
      if (createForm.loading_lat) body.loading_lat = parseFloat(createForm.loading_lat);
      if (createForm.loading_lng) body.loading_lng = parseFloat(createForm.loading_lng);
      // 하차지
      if (createForm.unloading_name) body.unloading_name = createForm.unloading_name;
      if (createForm.unloading_address) body.unloading_address = createForm.unloading_address;
      if (createForm.unloading_lat) body.unloading_lat = parseFloat(createForm.unloading_lat);
      if (createForm.unloading_lng) body.unloading_lng = parseFloat(createForm.unloading_lng);

      const res = await apiClient.post('/rooms', body);
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
    // GPS 탭 초기화
    setGpsTab(false);
    setGpsHistory([]);
    setGpsAvailDates([]);
    setGpsMessage(null);
    try {
      const res = await apiClient.get(`/rooms/${roomId}`);
      setSelectedRoom(res.data);
    } catch (err) {
      alert('상세 정보를 불러올 수 없습니다.');
    } finally {
      setDetailLoading(false);
    }
  };

  // GPS 이력 - 가용 날짜 로드
  const loadGpsAvailDates = async (roomId: number) => {
    try {
      const res = await apiClient.get(`/location-rooms/${roomId}/gps-available-dates`);
      const dates: string[] = res.data?.dates ?? [];
      setGpsAvailDates(dates);
      if (dates.length > 0) {
        setGpsDate(dates[0]);
        loadGpsHistory(roomId, dates[0]);
      } else {
        setGpsDate('');
        setGpsHistory([]);
        setGpsMessage('최근 3일 이내 GPS 이력이 없습니다.');
      }
    } catch {
      setGpsAvailDates([]);
      setGpsMessage('GPS 데이터를 불러올 수 없습니다.');
    }
  };

  // GPS 이력 - 날짜별 경로 로드
  const loadGpsHistory = async (roomId: number, date: string) => {
    if (!date) return;
    setGpsLoading(true);
    setGpsMessage(null);
    try {
      const res = await apiClient.get(`/location-rooms/${roomId}/gps-history?date=${date}`);
      setGpsHistory(res.data?.items ?? []);
      setGpsMessage(res.data?.message ?? null);
    } catch {
      setGpsHistory([]);
      setGpsMessage('GPS 데이터를 불러올 수 없습니다.');
    } finally {
      setGpsLoading(false);
    }
  };

  const handleSwitchToGpsTab = (roomId: number) => {
    setGpsTab(true);
    loadGpsAvailDates(roomId);
  };

  const handleStatusChange = async (roomId: number, newStatus: string) => {
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
      vehicle_plate: '', client_name: '', hours_valid: 48, notes: '',
      loading_name: '', loading_address: '', loading_lat: '', loading_lng: '',
      unloading_name: '', unloading_address: '', unloading_lat: '', unloading_lng: '',
    });
    setCreatedRoom(null);
    setShowCreate(false);
    setShowVehiclePicker(false);
    setMonitoringVehicles([]);
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
          onClick={() => { setShowCreate(true); setCreatedRoom(null); loadMonitoringVehicles(); }}
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
              <div className="p-6 space-y-4 max-h-[80vh] overflow-y-auto">
                {/* 방 제목 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    방 제목 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={createForm.title}
                    onChange={e => setCreateForm(p => ({ ...p, title: e.target.value }))}
                    placeholder="예: 2026-06-29 김해→광주 냉동운송"
                    className="w-full px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* 차량 선택 (실시간모니터링 연동) */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    차량 선택 <span className="text-xs text-gray-400">(실시간모니터링에서 불러오기)</span>
                  </label>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={createForm.vehicle_plate}
                      onChange={e => setCreateForm(p => ({ ...p, vehicle_plate: e.target.value }))}
                      placeholder="차량번호 직접 입력 또는 아래서 선택"
                      className="flex-1 px-3 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <button
                      type="button"
                      onClick={() => setShowVehiclePicker(p => !p)}
                      className="px-3 py-2.5 bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-xl text-sm font-medium transition-colors flex items-center gap-1"
                    >
                      <Truck size={14} />
                      {vehiclesLoading ? '로딩...' : '선택'}
                    </button>
                  </div>
                  {/* 차량 목록 드롭다운 */}
                  {showVehiclePicker && (
                    <div className="mt-1 border border-gray-200 rounded-xl overflow-hidden bg-white shadow-lg max-h-48 overflow-y-auto">
                      {vehiclesLoading ? (
                        <div className="flex items-center justify-center py-6">
                          <Loader2 size={18} className="animate-spin text-blue-500 mr-2" />
                          <span className="text-sm text-gray-500">차량 목록 로딩 중...</span>
                        </div>
                      ) : monitoringVehicles.length === 0 ? (
                        <div className="py-4 text-center text-sm text-gray-400">등록된 활성 차량이 없습니다</div>
                      ) : (
                        monitoringVehicles.map(v => (
                          <button
                            key={v.id}
                            type="button"
                            onClick={() => handleSelectVehicle(v)}
                            className="w-full flex items-center gap-3 px-4 py-2.5 hover:bg-blue-50 transition-colors text-left border-b border-gray-50 last:border-0"
                          >
                            <div className={`w-2 h-2 rounded-full flex-shrink-0 ${v.is_engine_on ? 'bg-green-400' : 'bg-gray-300'}`} />
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-800">{v.plate_number}</p>
                              <p className="text-xs text-gray-500">{v.vehicle_type} {v.driver_name ? `· ${v.driver_name}` : ''}</p>
                            </div>
                            {v.last_gps_time && (
                              <span className="text-xs text-gray-400 flex-shrink-0">
                                {v.last_gps_time.slice(0,2)}:{v.last_gps_time.slice(2,4)} · {v.last_speed ?? 0}km/h
                              </span>
                            )}
                          </button>
                        ))
                      )}
                    </div>
                  )}
                </div>

                {/* 기사 정보 */}
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
                </div>

                {/* 고객사명 */}
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

                {/* 상차지 */}
                <div className="bg-blue-50 rounded-xl p-3 space-y-2">
                  <p className="text-sm font-semibold text-blue-700 flex items-center gap-1.5">
                    <MapPin size={14} /> 상차지 정보
                    <span className="text-xs font-normal text-blue-500">(입력 시 도착/출차 시각 자동기록)</span>
                  </p>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">명칭</label>
                      <input
                        type="text"
                        value={createForm.loading_name}
                        onChange={e => setCreateForm(p => ({ ...p, loading_name: e.target.value }))}
                        placeholder="예: 김해센터"
                        className="w-full px-2.5 py-2 border border-blue-200 bg-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">주소</label>
                      <input
                        type="text"
                        value={createForm.loading_address}
                        onChange={e => setCreateForm(p => ({ ...p, loading_address: e.target.value }))}
                        placeholder="경남 김해시 주촌면..."
                        className="w-full px-2.5 py-2 border border-blue-200 bg-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">위도 (Lat)</label>
                      <input
                        type="number"
                        step="0.000001"
                        value={createForm.loading_lat}
                        onChange={e => setCreateForm(p => ({ ...p, loading_lat: e.target.value }))}
                        placeholder="35.123456"
                        className="w-full px-2.5 py-2 border border-blue-200 bg-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">경도 (Lng)</label>
                      <input
                        type="number"
                        step="0.000001"
                        value={createForm.loading_lng}
                        onChange={e => setCreateForm(p => ({ ...p, loading_lng: e.target.value }))}
                        placeholder="128.654321"
                        className="w-full px-2.5 py-2 border border-blue-200 bg-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                      />
                    </div>
                  </div>
                </div>

                {/* 하차지 */}
                <div className="bg-orange-50 rounded-xl p-3 space-y-2">
                  <p className="text-sm font-semibold text-orange-700 flex items-center gap-1.5">
                    <MapPin size={14} /> 하차지 정보
                    <span className="text-xs font-normal text-orange-500">(입력 시 도착/출차 시각 자동기록)</span>
                  </p>
                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">명칭</label>
                      <input
                        type="text"
                        value={createForm.unloading_name}
                        onChange={e => setCreateForm(p => ({ ...p, unloading_name: e.target.value }))}
                        placeholder="예: 광주저온"
                        className="w-full px-2.5 py-2 border border-orange-200 bg-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">주소</label>
                      <input
                        type="text"
                        value={createForm.unloading_address}
                        onChange={e => setCreateForm(p => ({ ...p, unloading_address: e.target.value }))}
                        placeholder="광주 북구 삼소로..."
                        className="w-full px-2.5 py-2 border border-orange-200 bg-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">위도 (Lat)</label>
                      <input
                        type="number"
                        step="0.000001"
                        value={createForm.unloading_lat}
                        onChange={e => setCreateForm(p => ({ ...p, unloading_lat: e.target.value }))}
                        placeholder="35.123456"
                        className="w-full px-2.5 py-2 border border-orange-200 bg-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
                      />
                    </div>
                    <div>
                      <label className="block text-xs text-gray-600 mb-1">경도 (Lng)</label>
                      <input
                        type="number"
                        step="0.000001"
                        value={createForm.unloading_lng}
                        onChange={e => setCreateForm(p => ({ ...p, unloading_lng: e.target.value }))}
                        placeholder="126.654321"
                        className="w-full px-2.5 py-2 border border-orange-200 bg-white rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-400"
                      />
                    </div>
                  </div>
                </div>

                {/* 유효 시간 */}
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

                {/* 메모 */}
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

                {/* 탭 전환 버튼 */}
                <div className="flex gap-2 border-b pb-1">
                  <button
                    onClick={() => setGpsTab(false)}
                    className={`px-4 py-1.5 rounded-t-lg text-sm font-medium transition-colors ${!gpsTab ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-blue-600'}`}
                  >
                    <MapPin size={14} className="inline mr-1" />방 정보
                  </button>
                  <button
                    onClick={() => handleSwitchToGpsTab(selectedRoom.id)}
                    className={`px-4 py-1.5 rounded-t-lg text-sm font-medium transition-colors ${gpsTab ? 'bg-blue-600 text-white' : 'text-gray-500 hover:text-blue-600'}`}
                  >
                    <Navigation size={14} className="inline mr-1" />GPS 이력
                    {gpsAvailDates.length > 0 && (
                      <span className="ml-1 bg-white text-blue-600 rounded-full px-1.5 text-xs font-bold">{gpsAvailDates.length}</span>
                    )}
                  </button>
                </div>

                {/* GPS 이력 탭 */}
                {gpsTab ? (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-sm text-gray-500">날짜 선택 (최근 3일):</span>
                      {gpsAvailDates.length > 0 ? (
                        gpsAvailDates.map(d => (
                          <button
                            key={d}
                            onClick={() => { setGpsDate(d); loadGpsHistory(selectedRoom.id, d); }}
                            className={`px-3 py-1 rounded-lg text-sm font-medium border transition-colors ${
                              gpsDate === d
                                ? 'bg-blue-600 text-white border-blue-600'
                                : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400'
                            }`}
                          >
                            {`${d.slice(0,4)}-${d.slice(4,6)}-${d.slice(6,8)}`}
                          </button>
                        ))
                      ) : (
                        <span className="text-sm text-gray-400">조회 가능한 날짜 없음</span>
                      )}
                    </div>

                    {gpsLoading ? (
                      <div className="flex items-center justify-center py-10">
                        <Loader2 className="animate-spin text-blue-500" size={24} />
                        <span className="ml-2 text-sm text-gray-500">GPS 이력 불러오는 중...</span>
                      </div>
                    ) : gpsHistory.length > 0 ? (
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">
                            📍 {gpsDate.slice(0,4)}-{gpsDate.slice(4,6)}-{gpsDate.slice(6,8)} 이동 기록
                            <span className="ml-2 text-blue-600 font-bold">{gpsHistory.length}건</span>
                          </span>
                          <span className="text-xs text-gray-400">5분 간격 수집 · 3일치 보관</span>
                        </div>

                        {/* 이동 경로 요약 */}
                        <div className="grid grid-cols-3 gap-2 mb-3">
                          <div className="bg-blue-50 rounded-lg p-2 text-center">
                            <p className="text-xs text-gray-500">첫 수신</p>
                            <p className="text-sm font-bold text-blue-700">
                              {`${gpsHistory[0].time.slice(0,2)}:${gpsHistory[0].time.slice(2,4)}`}
                            </p>
                          </div>
                          <div className="bg-green-50 rounded-lg p-2 text-center">
                            <p className="text-xs text-gray-500">최고속도</p>
                            <p className="text-sm font-bold text-green-700">
                              {Math.max(...gpsHistory.map((g:any) => g.speed_kmh || 0))} km/h
                            </p>
                          </div>
                          <div className="bg-orange-50 rounded-lg p-2 text-center">
                            <p className="text-xs text-gray-500">마지막 수신</p>
                            <p className="text-sm font-bold text-orange-700">
                              {`${gpsHistory[gpsHistory.length-1].time.slice(0,2)}:${gpsHistory[gpsHistory.length-1].time.slice(2,4)}`}
                            </p>
                          </div>
                        </div>

                        {/* 지도 링크 버튼 */}
                        {gpsHistory.length > 0 && (
                          <a
                            href={`https://map.naver.com/v5/search/${gpsHistory[Math.floor(gpsHistory.length/2)].latitude},${gpsHistory[Math.floor(gpsHistory.length/2)].longitude}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-2 w-full justify-center py-2 mb-3 bg-green-50 hover:bg-green-100 text-green-700 border border-green-200 rounded-xl text-sm font-medium transition-colors"
                          >
                            <MapPin size={14} /> 네이버 지도에서 위치 보기
                          </a>
                        )}

                        {/* GPS 포인트 목록 */}
                        <div className="max-h-60 overflow-y-auto space-y-1 border rounded-xl p-2 bg-gray-50">
                          {gpsHistory.map((g: any, i: number) => (
                            <div key={i} className="flex items-center gap-2 text-xs py-1 border-b border-gray-100 last:border-0">
                              <span className="text-gray-400 w-12 shrink-0">
                                {`${g.time.slice(0,2)}:${g.time.slice(2,4)}`}
                              </span>
                              <span className={`w-2 h-2 rounded-full shrink-0 ${g.is_engine_on ? 'bg-green-400' : 'bg-gray-300'}`} />
                              <span className="text-gray-600 flex-1">
                                {g.latitude.toFixed(5)}, {g.longitude.toFixed(5)}
                              </span>
                              <span className="text-blue-600 shrink-0">{g.speed_kmh} km/h</span>
                            </div>
                          ))}
                        </div>
                        <p className="text-xs text-gray-400 mt-1">● 초록: 시동ON / ● 회색: 시동OFF</p>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center justify-center py-10 text-gray-400">
                        <Navigation size={32} className="mb-2 opacity-30" />
                        <p className="text-sm">{gpsMessage || '해당 날짜의 GPS 데이터가 없습니다.'}</p>
                        <p className="text-xs mt-1">GPS 데이터는 5분마다 수집되며 3일치만 보관됩니다.</p>
                      </div>
                    )}
                  </div>
                ) : (
                  <>
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

                {/* ── 운행 타임라인 ── */}
                {(selectedRoom.loading_name || selectedRoom.unloading_name) && (
                  <div className="rounded-xl border border-gray-200 overflow-hidden">
                    <div className="bg-gray-50 px-4 py-2 flex items-center gap-2">
                      <Clock size={14} className="text-gray-500" />
                      <span className="text-sm font-semibold text-gray-700">운행 타임라인</span>
                      <span className="text-xs text-gray-400 ml-auto">반경 300m 자동기록</span>
                    </div>
                    <div className="p-3 space-y-2">
                      {/* 상차지 */}
                      {selectedRoom.loading_name && (
                        <div className="flex items-start gap-3">
                          <div className="flex flex-col items-center mt-1">
                            <div className={`w-3 h-3 rounded-full border-2 ${selectedRoom.arrived_at_loading ? 'bg-blue-500 border-blue-500' : 'bg-white border-gray-300'}`} />
                            <div className="w-0.5 h-6 bg-gray-200" />
                            <div className={`w-3 h-3 rounded-full border-2 ${selectedRoom.departed_loading ? 'bg-blue-500 border-blue-500' : 'bg-white border-gray-300'}`} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-semibold text-blue-700 mb-0.5">📦 상차지: {selectedRoom.loading_name}</p>
                            {selectedRoom.loading_address && <p className="text-xs text-gray-400 mb-1">{selectedRoom.loading_address}</p>}
                            <div className="flex gap-4 text-xs">
                              <TimelineCell
                                label="도착"
                                time={selectedRoom.arrived_at_loading}
                                roomId={selectedRoom.id}
                                field="arrived_at_loading"
                                onPatch={(updated) => setSelectedRoom(p => p ? { ...p, ...updated } : p)}
                              />
                              <TimelineCell
                                label="출차"
                                time={selectedRoom.departed_loading}
                                roomId={selectedRoom.id}
                                field="departed_loading"
                                onPatch={(updated) => setSelectedRoom(p => p ? { ...p, ...updated } : p)}
                              />
                            </div>
                          </div>
                        </div>
                      )}

                      {/* 이동 구간 표시 */}
                      {selectedRoom.loading_name && selectedRoom.unloading_name && (
                        <div className="flex items-center gap-2 pl-5 text-xs text-gray-400">
                          <div className="flex-1 border-t border-dashed border-gray-200" />
                          <Truck size={12} />
                          <span>이동 중</span>
                          <div className="flex-1 border-t border-dashed border-gray-200" />
                        </div>
                      )}

                      {/* 하차지 */}
                      {selectedRoom.unloading_name && (
                        <div className="flex items-start gap-3">
                          <div className="flex flex-col items-center mt-1">
                            <div className={`w-3 h-3 rounded-full border-2 ${selectedRoom.arrived_at_unloading ? 'bg-orange-500 border-orange-500' : 'bg-white border-gray-300'}`} />
                            <div className="w-0.5 h-6 bg-gray-200" />
                            <div className={`w-3 h-3 rounded-full border-2 ${selectedRoom.departed_unloading ? 'bg-green-500 border-green-500' : 'bg-white border-gray-300'}`} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs font-semibold text-orange-700 mb-0.5">🏭 하차지: {selectedRoom.unloading_name}</p>
                            {selectedRoom.unloading_address && <p className="text-xs text-gray-400 mb-1">{selectedRoom.unloading_address}</p>}
                            <div className="flex gap-4 text-xs">
                              <TimelineCell
                                label="도착"
                                time={selectedRoom.arrived_at_unloading}
                                roomId={selectedRoom.id}
                                field="arrived_at_unloading"
                                onPatch={(updated) => setSelectedRoom(p => p ? { ...p, ...updated } : p)}
                              />
                              <TimelineCell
                                label="하차완료"
                                time={selectedRoom.departed_unloading}
                                roomId={selectedRoom.id}
                                field="departed_unloading"
                                onPatch={(updated) => setSelectedRoom(p => p ? { ...p, ...updated } : p)}
                              />
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}

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
                  </>
                )}
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

// ====== TimelineCell 서브컴포넌트 ======
// 타임라인 셀: 시각 표시 + 미기록 시 "지금 기록" 버튼

interface TimelineCellProps {
  label: string;
  time?: string;
  roomId: number;
  field: string;
  onPatch: (updated: Record<string, string>) => void;
}

const TimelineCell: React.FC<TimelineCellProps> = ({ label, time, roomId, field, onPatch }) => {
  const [patching, setPatching] = useState(false);

  const handlePatch = async () => {
    if (patching) return;
    if (!window.confirm(`"${label}" 시각을 지금으로 기록하시겠습니까?`)) return;
    setPatching(true);
    try {
      const res = await apiClient.patch(`/rooms/${roomId}/timeline`, { field });
      onPatch({ [field]: res.data.value });
    } catch {
      alert('기록에 실패했습니다.');
    } finally {
      setPatching(false);
    }
  };

  if (time) {
    return (
      <div className="flex flex-col">
        <span className="text-gray-400">{label}</span>
        <span className="font-semibold text-gray-800">
          {new Date(time).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
        </span>
        <span className="text-gray-400 text-xs">
          {new Date(time).toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' })}
        </span>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      <span className="text-gray-400">{label}</span>
      <button
        onClick={handlePatch}
        disabled={patching}
        className="mt-0.5 px-2 py-0.5 bg-gray-100 hover:bg-blue-100 text-gray-500 hover:text-blue-600 rounded text-xs transition-colors flex items-center gap-1 w-fit"
      >
        {patching ? <Loader2 size={10} className="animate-spin" /> : <Clock size={10} />}
        {patching ? '기록 중...' : '지금 기록'}
      </button>
    </div>
  );
};
