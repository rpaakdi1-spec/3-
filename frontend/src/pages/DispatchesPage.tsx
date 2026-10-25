import React, { useEffect, useState, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import Card from '../components/common/Card';
import Loading from '../components/common/Loading';
import apiClient from '../api/client';
import { Dispatch } from '../types';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Truck, Navigation, Clock, CheckCircle, Trash2, Edit2, X, Package, MapPin, AlertCircle, Filter, Search, Calendar, Link2, Copy, QrCode, UserPlus, Radio } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import toast from 'react-hot-toast';
import { useResponsive } from '../hooks/useResponsive';
import { MobileDispatchCard } from '../components/mobile/MobileDispatchCard';
import GuestTrackingModal from '../components/dispatch/GuestTrackingModal';

const DispatchesPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [dispatches, setDispatches] = useState<Dispatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDispatch, setSelectedDispatch] = useState<Dispatch | null>(null);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [trackingNumber, setTrackingNumber] = useState<string | null>(null);
  const [generatingTracking, setGeneratingTracking] = useState(false);
  const [guestToken, setGuestToken] = useState<string | null>(null);
  const [generatingGuest, setGeneratingGuest] = useState(false);
  const [showTrackingModal, setShowTrackingModal] = useState(false);
  const [trackingModalToken, setTrackingModalToken] = useState<string | null>(null);
  const { isMobile } = useResponsive();

  // 차량 추적 모달 열기
  const openTrackingModal = (token: string) => {
    setTrackingModalToken(token);
    setShowTrackingModal(true);
  };

  // Filter states
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterVehicle, setFilterVehicle] = useState<string>('');
  const [filterDate, setFilterDate] = useState<string>('');
  const [searchText, setSearchText] = useState<string>('');

  useEffect(() => {
    fetchDispatches();
    const interval = setInterval(fetchDispatches, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  // URL에 refresh 파라미터가 있으면 즉시 새로고침
  useEffect(() => {
    const refreshParam = searchParams.get('refresh');
    if (refreshParam) {
      console.log('🔄 배차 확정 후 리다이렉트 감지 - 즉시 새로고침');
      toast.success('배차 목록을 업데이트합니다...');
      fetchDispatches();
      
      // URL에서 refresh 파라미터 제거 (깨끗한 URL 유지)
      window.history.replaceState({}, '', '/dispatches');
    }
  }, [searchParams]);

  const fetchDispatches = async () => {
    try {
      // Fetch all dispatches (no status filter to show drafts too)
      console.log('📊 배차 목록 조회 시작...');
      const response = await apiClient.getDispatches({});
      console.log('📊 배차 목록 응답:', response);
      console.log('📊 배차 개수:', response.items?.length || response.length || 0);
      
      const items = response.items || response;
      setDispatches(items);
      setSelectedIds([]);
      
      // 상태별 통계 로깅
      const stats = items.reduce((acc: any, d: any) => {
        acc[d.status] = (acc[d.status] || 0) + 1;
        return acc;
      }, {});
      console.log('📊 상태별 배차:', stats);
      
      if (loading) setLoading(false);
    } catch (error) {
      console.error('❌ 배차 목록 조회 실패:', error);
      toast.error('배차 목록을 불러오는데 실패했습니다');
      if (loading) setLoading(false);
    }
  };

  const handleSelectAll = () => {
    if (selectedIds.length === filteredDispatches.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredDispatches.map(d => d.id));
    }
  };

  const handleSelectOne = (id: number) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(selectedId => selectedId !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('이 배차를 삭제하시겠습니까?')) return;
    
    try {
      await apiClient.deleteDispatch(id);
      toast.success('배차가 삭제되었습니다');
      fetchDispatches();
    } catch (error) {
      toast.error('배차 삭제에 실패했습니다');
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) {
      toast.error('삭제할 배차를 선택해주세요');
      return;
    }
    
    if (!window.confirm(`선택한 ${selectedIds.length}개의 배차를 삭제하시겠습니까?`)) return;
    
    try {
      await Promise.all(selectedIds.map(id => apiClient.deleteDispatch(id)));
      toast.success(`${selectedIds.length}개의 배차가 삭제되었습니다`);
      fetchDispatches();
    } catch (error) {
      toast.error('일괄 삭제에 실패했습니다');
    }
  };

  const generateTrackingNumber = async (dispatchId: number) => {
    setGeneratingTracking(true);
    try {
      const response = await apiClient.post('/dispatch/tracking/generate', {
        dispatch_id: dispatchId
      });
      
      const newTrackingNumber = response.data.tracking_number;
      setTrackingNumber(newTrackingNumber);
      
      // 추적 URL 생성
      const trackingUrl = `${window.location.origin}/track/${newTrackingNumber}`;
      
      // 클립보드에 복사
      try {
        await navigator.clipboard.writeText(trackingUrl);
        toast.success(
          `🔗 추적 번호가 생성되었습니다!\n${newTrackingNumber}\n\nURL이 클립보드에 복사되었습니다.`,
          { duration: 5000 }
        );
      } catch (clipboardError) {
        toast.success(
          `🔗 추적 번호: ${newTrackingNumber}`,
          { duration: 5000 }
        );
      }
    } catch (error: any) {
      console.error('추적 번호 생성 실패:', error);
      toast.error(error.response?.data?.detail || '추적 번호 생성에 실패했습니다');
    } finally {
      setGeneratingTracking(false);
    }
  };

  const copyTrackingUrl = async () => {
    if (!trackingNumber) return;
    
    const trackingUrl = `${window.location.origin}/track/${trackingNumber}`;
    try {
      await navigator.clipboard.writeText(trackingUrl);
      toast.success('추적 URL이 클립보드에 복사되었습니다!');
    } catch (error) {
      toast.error('클립보드 복사에 실패했습니다');
    }
  };

  // 게스트 토큰 생성 (1회용 링크)
  const generateGuestToken = async (dispatchId: number) => {
    if (generatingGuest) return;
    
    setGeneratingGuest(true);
    try {
      const response = await apiClient.post('/guest/delivery/create-token', {
        dispatch_id: dispatchId,
        hours_valid: 24
      });
      
      const token = response.data.token;
      setGuestToken(token);
      
      // 게스트 URL 생성
      const guestUrl = `${window.location.origin}/guest/delivery/${token}`;
      
      // 클립보드에 복사
      try {
        await navigator.clipboard.writeText(guestUrl);
        toast.success(
          `🚚 기사 전용 링크가 생성되었습니다!\n\n링크가 클립보드에 복사되었습니다.\n유효기간: 24시간`,
          { duration: 6000 }
        );
      } catch (clipboardError) {
        toast.success(
          `🚚 기사 전용 링크가 생성되었습니다!\n유효기간: 24시간`,
          { duration: 6000 }
        );
      }
    } catch (error: any) {
      console.error('게스트 토큰 생성 실패:', error);
      toast.error(error.response?.data?.detail || '기사 링크 생성에 실패했습니다');
    } finally {
      setGeneratingGuest(false);
    }
  };

  const copyGuestUrl = async () => {
    if (!guestToken) return;
    
    const guestUrl = `${window.location.origin}/guest/delivery/${guestToken}`;
    try {
      await navigator.clipboard.writeText(guestUrl);
      toast.success('기사 전용 링크가 클립보드에 복사되었습니다!');
    } catch (error) {
      toast.error('클립보드 복사에 실패했습니다');
    }
  };

  const handleConfirmSelected = async () => {
    if (selectedIds.length === 0) {
      toast.error('확정할 배차를 선택해주세요');
      return;
    }

    // Filter only DRAFT dispatches
    const draftDispatches = dispatches.filter(d => 
      selectedIds.includes(d.id) && d.status === '임시저장'
    );

    if (draftDispatches.length === 0) {
      toast.error('임시저장 상태의 배차만 확정할 수 있습니다');
      return;
    }

    if (!window.confirm(`선택한 ${draftDispatches.length}개의 배차를 확정하시겠습니까?\n\n확정 후에는 수정/삭제가 불가능합니다.`)) {
      return;
    }

    try {
      const response = await apiClient.confirmDispatches(draftDispatches.map(d => d.id));
      
      if (response.confirmed > 0) {
        toast.success(
          `✅ ${response.confirmed}건의 배차가 확정되었습니다!\n` +
          `주문 상태가 '배차완료'로 변경되었습니다.`
        );
        
        if (response.failed > 0) {
          toast.error(`${response.failed}건 확정 실패`);
        }
        
        // DB 커밋 대기 후 새로고침
        setTimeout(() => {
          fetchDispatches();
          setSelectedIds([]);
        }, 500);
      } else {
        toast.error('배차 확정에 실패했습니다');
      }
    } catch (error: any) {
      console.error('배차 확정 실패:', error);
      toast.error(error.response?.data?.detail || '배차 확정에 실패했습니다');
    }
  };

  // Filtered dispatches
  const filteredDispatches = useMemo(() => {
    let filtered = [...dispatches];

    // Status filter
    if (filterStatus && filterStatus !== 'all') {
      filtered = filtered.filter(d => d.status === filterStatus);
    }

    // Vehicle filter
    if (filterVehicle) {
      filtered = filtered.filter(d => 
        d.vehicle_plate?.toLowerCase().includes(filterVehicle.toLowerCase()) ||
        d.driver_name?.toLowerCase().includes(filterVehicle.toLowerCase())
      );
    }

    // Date filter
    if (filterDate) {
      filtered = filtered.filter(d => {
        const dispatchDate = new Date(d.dispatch_date).toISOString().split('T')[0];
        return dispatchDate === filterDate;
      });
    }

    // Search text filter
    if (searchText) {
      const search = searchText.toLowerCase();
      filtered = filtered.filter(d =>
        d.dispatch_number?.toLowerCase().includes(search) ||
        d.vehicle_plate?.toLowerCase().includes(search) ||
        d.driver_name?.toLowerCase().includes(search)
      );
    }

    return filtered;
  }, [dispatches, filterStatus, filterVehicle, filterDate, searchText]);

  // Get unique vehicles for filter dropdown
  const uniqueVehicles = useMemo(() => {
    const vehicles = new Set(dispatches.map(d => d.vehicle_plate).filter(Boolean));
    return Array.from(vehicles).sort();
  }, [dispatches]);

  const clearFilters = () => {
    setFilterStatus('all');
    setFilterVehicle('');
    setFilterDate('');
    setSearchText('');
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      임시저장: 'bg-gray-100 text-gray-800',
      확정: 'bg-yellow-100 text-yellow-800',
      진행중: 'bg-green-100 text-green-800',
      완료: 'bg-blue-100 text-blue-800',
      취소: 'bg-red-100 text-red-800',
    };
    const labels = {
      임시저장: '임시저장',
      확정: '확정',
      진행중: '진행중',
      완료: '완료',
      취소: '취소',
    };
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${styles[status as keyof typeof styles]}`}>
        {labels[status as keyof typeof labels] || status}
      </span>
    );
  };

  if (loading) {
    return (<Loading />
  );
  }

  return (<><div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">배차 관리</h1>
            <p className="text-gray-600 mt-2">실시간 배송 현황을 모니터링하세요</p>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Filter className="text-gray-400" size={20} />
              <h3 className="font-semibold text-gray-700">필터</h3>
              {(filterStatus !== 'all' || filterVehicle || filterDate || searchText) && (
                <button
                  onClick={clearFilters}
                  className="ml-auto text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  <X size={14} />
                  필터 초기화
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="text"
                  placeholder="배차번호, 차량, 기사 검색..."
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Status Filter */}
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">전체 상태</option>
                <option value="임시저장">임시저장</option>
                <option value="확정">확정</option>
                <option value="진행중">진행중</option>
                <option value="완료">완료</option>
                <option value="취소">취소</option>
              </select>

              {/* Vehicle Filter */}
              <select
                value={filterVehicle}
                onChange={(e) => setFilterVehicle(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">전체 차량</option>
                {uniqueVehicles.map(vehicle => (
                  <option key={vehicle} value={vehicle}>{vehicle}</option>
                ))}
              </select>

              {/* Date Filter */}
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="date"
                  value={filterDate}
                  onChange={(e) => setFilterDate(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="날짜 선택"
                />
              </div>
            </div>

            {/* Filter Results */}
            <div className="text-sm text-gray-600">
              <span className="font-semibold">{filteredDispatches.length}</span>개의 배차가 검색되었습니다.
              {filteredDispatches.length !== dispatches.length && (
                <span className="ml-2">(전체 {dispatches.length}개 중)</span>
              )}
            </div>
          </div>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">전체 배차</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{filteredDispatches.length}</p>
              </div>
              <Truck className="text-gray-400" size={32} />
            </div>
          </Card>
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">진행 중</p>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  {filteredDispatches.filter((d) => d.status === '진행중').length}
                </p>
              </div>
              <Navigation className="text-green-400" size={32} />
            </div>
          </Card>
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">배차 확정</p>
                <p className="text-2xl font-bold text-yellow-600 mt-1">
                  {filteredDispatches.filter((d) => d.status === '확정').length}
                </p>
              </div>
              <Clock className="text-yellow-400" size={32} />
            </div>
          </Card>
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">완료</p>
                <p className="text-2xl font-bold text-gray-600 mt-1">
                  {filteredDispatches.filter((d) => d.status === 'COMPLETED').length}
                </p>
              </div>
              <CheckCircle className="text-gray-400" size={32} />
            </div>
          </Card>
        </div>

        {/* Map */}
        <Card title="실시간 차량 위치">
          <div className="h-96 rounded-lg overflow-hidden">
            <MapContainer
              center={[37.5665, 126.978]}
              zoom={11}
              style={{ height: '100%', width: '100%' }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {filteredDispatches
                .filter((d) => d.current_location_lat && d.current_location_lon)
                .map((dispatch) => (
                  <Marker
                    key={dispatch.id}
                    position={[dispatch.current_location_lat!, dispatch.current_location_lon!]}
                  >
                    <Popup>
                      <div className="p-2">
                        <p className="font-semibold">{dispatch.dispatch_number}</p>
                        <p className="text-sm text-gray-600">{dispatch.vehicle_plate}</p>
                        <p className="text-sm">{getStatusBadge(dispatch.status)}</p>
                      </div>
                    </Popup>
                  </Marker>
                ))}
            </MapContainer>
          </div>
        </Card>

        {/* Action Buttons - Always Visible */}
        <Card>
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {selectedIds.length > 0 ? (
                <span className="font-semibold">{selectedIds.length}개 항목 선택됨</span>
              ) : (
                <span>배차를 선택하여 일괄 작업을 수행하세요</span>
              )}
            </div>
            <div className="flex space-x-3">
              <button 
                className={`px-4 py-2 rounded-lg flex items-center text-sm font-medium ${
                  selectedIds.length > 0 && dispatches.filter(d => selectedIds.includes(d.id) && d.status === '임시저장').length > 0
                    ? 'bg-green-600 hover:bg-green-700 text-white'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
                onClick={handleConfirmSelected}
                disabled={selectedIds.length === 0 || dispatches.filter(d => selectedIds.includes(d.id) && d.status === '임시저장').length === 0}
              >
                <CheckCircle size={16} className="mr-2" />
                선택 배차 확정 ({dispatches.filter(d => selectedIds.includes(d.id) && d.status === '임시저장').length}건)
              </button>
              <button 
                className={`px-4 py-2 rounded-lg flex items-center text-sm ${
                  selectedIds.length > 0
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
                onClick={handleBulkDelete}
                disabled={selectedIds.length === 0}
              >
                <Trash2 size={16} className="mr-2" />
                선택 항목 삭제
              </button>
            </div>
          </div>
        </Card>

        {/* Legacy Bulk Actions - Keep for compatibility */}
        {false && selectedIds.length > 0 && (
          <Card>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">
                {selectedIds.length}개 항목 선택됨
              </span>
              <div className="flex space-x-3">
                <button 
                  className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center text-sm font-medium"
                  onClick={handleConfirmSelected}
                >
                  <CheckCircle size={16} className="mr-2" />
                  선택 배차 확정 ({dispatches.filter(d => selectedIds.includes(d.id) && d.status === '임시저장').length}건)
                </button>
                <button 
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg flex items-center text-sm"
                  onClick={handleBulkDelete}
                >
                  <Trash2 size={16} className="mr-2" />
                  선택 항목 삭제
                </button>
              </div>
            </div>
          </Card>
        )}

        {/* Dispatch List */}
        {isMobile ? (
          /* Mobile Card View */
          <div className="px-4 space-y-3">
            {dispatches.length === 0 ? (
              <div className="text-center py-12">
                <Truck size={48} className="mx-auto mb-4 text-gray-300" />
                <p className="text-gray-500">진행 중인 배차가 없습니다</p>
              </div>
            ) : (
              filteredDispatches.map((dispatch) => (
                <MobileDispatchCard
                  key={dispatch.id}
                  dispatch={{
                    id: dispatch.id,
                    dispatch_number: dispatch.dispatch_number,
                    dispatch_date: dispatch.dispatch_date || '',
                    vehicle: dispatch.vehicle_plate ? {
                      license_plate: dispatch.vehicle_plate,
                      vehicle_type: dispatch.vehicle_type || '',
                    } : undefined,
                    driver: dispatch.driver_name ? {
                      name: dispatch.driver_name,
                    } : undefined,
                    status: dispatch.status,
                    total_orders: dispatch.total_orders || 0,
                    total_pallets: dispatch.total_pallets || 0,
                    estimated_duration_minutes: dispatch.estimated_duration_minutes,
                    is_urgent: dispatch.is_urgent,
                  }}
                  onClick={() => {
                    setSelectedDispatch(dispatch);
                    setTrackingNumber(null); // Reset tracking number
                    setGuestToken(null); // Reset guest token
                    setShowModal(true);
                  }}
                />
              ))
            )}
          </div>
        ) : (
          /* Desktop Table View */
          <Card title="배차 목록">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="w-12 py-3 px-4">
                      <input
                        type="checkbox"
                        checked={dispatches.length > 0 && selectedIds.length === dispatches.length}
                        onChange={handleSelectAll}
                        className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                      />
                    </th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">배차번호</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">주문번호</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">차량번호</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">기사명</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">거리(km)</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">예상도착</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">상태</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">작업</th>
                  </tr>
                </thead>
                <tbody>
                  {dispatches.length === 0 ? (
                    <tr>
                      <td colSpan={9} className="text-center py-8 text-gray-500">
                        <Truck size={48} className="mx-auto mb-4 text-gray-300" />
                        <p>진행 중인 배차가 없습니다</p>
                      </td>
                    </tr>
                  ) : (
                    filteredDispatches.map((dispatch) => (
                      <tr
                        key={dispatch.id}
                        className="border-b border-gray-100 hover:bg-gray-50"
                      >
                        <td className="py-3 px-4">
                          <input
                            type="checkbox"
                            checked={selectedIds.includes(dispatch.id)}
                            onChange={() => handleSelectOne(dispatch.id)}
                            onClick={(e) => e.stopPropagation()}
                            className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                        </td>
                        <td className="py-3 px-4 font-medium text-blue-600">
                          {dispatch.dispatch_number}
                        </td>
                        <td className="py-3 px-4">{dispatch.order_number || '-'}</td>
                        <td className="py-3 px-4">{dispatch.vehicle_plate || '-'}</td>
                        <td className="py-3 px-4">{dispatch.driver_name || '-'}</td>
                        <td className="py-3 px-4">{dispatch.distance_km != null ? dispatch.distance_km.toFixed(1) : '-'}</td>
                        <td className="py-3 px-4">
                          {dispatch.estimated_arrival
                            ? new Date(dispatch.estimated_arrival).toLocaleString('ko-KR', {
                                month: 'short',
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit',
                              })
                            : '-'}
                        </td>
                        <td className="py-3 px-4">{getStatusBadge(dispatch.status)}</td>
                        <td className="py-3 px-4">
                          <div className="flex space-x-2">
                            <button 
                              className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center"
                              onClick={(e) => {
                                e.stopPropagation();
                                setSelectedDispatch(dispatch);
                                setTrackingNumber(null); // Reset tracking number
                    setGuestToken(null); // Reset guest token
                                setShowModal(true);
                              }}
                            >
                              <Edit2 size={14} className="mr-1" />
                              상세
                            </button>
                            <button 
                              className="text-red-600 hover:text-red-800 text-sm font-medium flex items-center"
                              onClick={() => handleDelete(dispatch.id)}
                            >
                              <Trash2 size={14} className="mr-1" />
                              삭제
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {/* Dispatch Detail Modal */}
        {showModal && selectedDispatch && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setShowModal(false)}>
            <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
              {/* Modal Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">배차 상세 정보</h2>
                  <p className="text-sm text-gray-600 mt-1">{selectedDispatch.dispatch_number}</p>
                </div>
                <button
                  onClick={() => setShowModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X size={24} />
                </button>
              </div>

              {/* Modal Body */}
              <div className="p-6 space-y-6">
                {/* 기본 정보 */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">배차 상태</label>
                    <div className="mt-1">{getStatusBadge(selectedDispatch.status)}</div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">배차 일자</label>
                    <p className="mt-1 text-gray-900">
                      {selectedDispatch.dispatch_date
                        ? new Date(selectedDispatch.dispatch_date).toLocaleDateString('ko-KR')
                        : '-'}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">차량 번호</label>
                    <p className="mt-1 text-gray-900">{selectedDispatch.vehicle_plate || '-'}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">기사명</label>
                    <p className="mt-1 text-gray-900">{selectedDispatch.driver_name || '-'}</p>
                  </div>
                </div>

                {/* 배송 정보 */}
                <div className="border-t border-gray-200 pt-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Package size={20} className="mr-2" />
                    배송 정보
                  </h3>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="text-sm font-medium text-gray-700">총 거리</label>
                      <p className="mt-1 text-gray-900">
                        {selectedDispatch.distance_km != null
                          ? `${selectedDispatch.distance_km.toFixed(1)} km`
                          : '-'}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">예상 도착</label>
                      <p className="mt-1 text-gray-900">
                        {selectedDispatch.estimated_arrival
                          ? new Date(selectedDispatch.estimated_arrival).toLocaleString('ko-KR')
                          : '-'}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium text-gray-700">주문 번호</label>
                      <p className="mt-1 text-gray-900">{selectedDispatch.order_number || '-'}</p>
                    </div>
                  </div>
                </div>

                {/* 위치 정보 */}
                {selectedDispatch.current_location_lat && selectedDispatch.current_location_lon && (
                  <div className="border-t border-gray-200 pt-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <MapPin size={20} className="mr-2" />
                      현재 위치
                    </h3>
                    <div className="h-64 rounded-lg overflow-hidden">
                      <MapContainer
                        center={[selectedDispatch.current_location_lat, selectedDispatch.current_location_lon]}
                        zoom={13}
                        style={{ height: '100%', width: '100%' }}
                      >
                        <TileLayer
                          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                        <Marker position={[selectedDispatch.current_location_lat, selectedDispatch.current_location_lon]}>
                          <Popup>
                            <div className="p-2">
                              <p className="font-semibold">{selectedDispatch.dispatch_number}</p>
                              <p className="text-sm text-gray-600">{selectedDispatch.vehicle_plate}</p>
                            </div>
                          </Popup>
                        </Marker>
                      </MapContainer>
                    </div>
                  </div>
                )}

                {/* 실시간 추적 */}
                <div className="border-t border-gray-200 pt-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Link2 size={20} className="mr-2" />
                    실시간 배송 추적
                  </h3>
                  
                  {trackingNumber ? (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-medium text-green-800">추적 번호</p>
                        <span className="px-3 py-1 bg-green-100 text-green-800 text-xs font-mono rounded">
                          {trackingNumber}
                        </span>
                      </div>
                      <p className="text-sm text-green-700 mb-3">
                        고객사에 아래 URL을 공유하여 실시간 배송 위치를 확인할 수 있습니다.
                      </p>
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          readOnly
                          value={`${window.location.origin}/track/${trackingNumber}`}
                          className="flex-1 px-3 py-2 border border-green-300 rounded-lg text-sm font-mono bg-white"
                        />
                        <button
                          onClick={copyTrackingUrl}
                          className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center text-sm"
                        >
                          <Copy size={16} className="mr-2" />
                          복사
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <p className="text-sm text-blue-700 mb-3">
                        고객사가 로그인 없이 실시간 배송 위치를 확인할 수 있는 추적 번호를 생성하세요.
                      </p>
                      <button
                        onClick={() => generateTrackingNumber(selectedDispatch.id)}
                        disabled={generatingTracking}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center text-sm disabled:opacity-50"
                      >
                        <Link2 size={16} className="mr-2" />
                        {generatingTracking ? '생성 중...' : '추적 번호 생성'}
                      </button>
                    </div>
                  )}
                </div>

                {/* 기사 전용 링크 (1회용) */}
                <div className="border-t border-gray-200 pt-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <UserPlus size={20} className="mr-2" />
                    기사 전용 링크 (회원가입 불필요)
                  </h3>
                  
                  {guestToken ? (
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-sm font-medium text-purple-800">1회용 링크</p>
                        <span className="px-3 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                          유효기간: 24시간
                        </span>
                      </div>
                      <p className="text-sm text-purple-700 mb-3">
                        기사님께 아래 링크를 SMS로 전송하면 회원가입 없이 바로 배송 작업을 시작할 수 있습니다.
                      </p>
                      <div className="flex items-center gap-2">
                        <input
                          type="text"
                          readOnly
                          value={`${window.location.origin}/guest/delivery/${guestToken}`}
                          className="flex-1 px-3 py-2 border border-purple-300 rounded-lg text-sm font-mono bg-white"
                        />
                        <button
                          onClick={copyGuestUrl}
                          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center text-sm"
                        >
                          <Copy size={16} className="mr-2" />
                          복사
                        </button>
                      </div>
                      <div className="mt-3 text-xs text-purple-600">
                        💡 이 링크로 기사님이 GPS 위치 전송과 서류 업로드를 할 수 있습니다.
                      </div>
                      {/* 실시간 추적 버튼 */}
                      <div className="mt-3 pt-3 border-t border-purple-200">
                        <button
                          onClick={() => openTrackingModal(guestToken!)}
                          className="w-full px-4 py-2.5 bg-orange-500 hover:bg-orange-600 text-white rounded-lg flex items-center justify-center gap-2 text-sm font-medium transition-colors shadow-sm"
                        >
                          <Radio size={16} className="animate-pulse" />
                          🗺️ 실시간 차량 위치 추적
                        </button>
                        <p className="text-xs text-purple-500 mt-1.5 text-center">기사님이 GPS를 시작하면 지도에 위치가 표시됩니다</p>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                      <p className="text-sm text-purple-700 mb-3">
                        1회성 기사님을 위한 간편 접속 링크를 생성하세요. 회원가입 없이 GPS 추적과 서류 업로드가 가능합니다.
                      </p>
                      <button
                        onClick={() => generateGuestToken(selectedDispatch.id)}
                        disabled={generatingGuest}
                        className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center text-sm disabled:opacity-50"
                      >
                        <UserPlus size={16} className="mr-2" />
                        {generatingGuest ? '생성 중...' : '기사 링크 생성'}
                      </button>
                    </div>
                  )}
                </div>

                {/* 상태별 안내 */}
                {selectedDispatch.status === '임시저장' && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex items-start">
                    <AlertCircle className="text-yellow-600 mr-3 flex-shrink-0" size={20} />
                    <div>
                      <p className="text-sm font-medium text-yellow-800">임시저장 상태</p>
                      <p className="text-sm text-yellow-700 mt-1">
                        이 배차는 아직 확정되지 않았습니다. 확정하려면 체크박스를 선택하고 '선택 배차 확정' 버튼을 클릭하세요.
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Modal Footer */}
              <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
                <button
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg"
                >
                  닫기
                </button>
                {selectedDispatch.status === '임시저장' && (
                  <button
                    onClick={() => {
                      setSelectedIds([selectedDispatch.id]);
                      setShowModal(false);
                      setTimeout(() => handleConfirmSelected(), 100);
                    }}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center"
                  >
                    <CheckCircle size={16} className="mr-2" />
                    이 배차 확정
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 실시간 차량 추적 모달 */}
      {showTrackingModal && trackingModalToken && (
        <GuestTrackingModal
          token={trackingModalToken}
          onClose={() => {
            setShowTrackingModal(false);
            setTrackingModalToken(null);
          }}
        />
      )}
  </>
  );
};

export default DispatchesPage;
