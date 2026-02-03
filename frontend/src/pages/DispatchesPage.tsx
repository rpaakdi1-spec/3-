import React, { useEffect, useState } from 'react';
import Layout from '../components/common/Layout';
import Card from '../components/common/Card';
import Loading from '../components/common/Loading';
import apiClient from '../api/client';
import { Dispatch } from '../types';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Truck, Navigation, Clock, CheckCircle, Trash2, Edit2 } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import toast from 'react-hot-toast';

const DispatchesPage: React.FC = () => {
  const [dispatches, setDispatches] = useState<Dispatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDispatch, setSelectedDispatch] = useState<Dispatch | null>(null);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);

  useEffect(() => {
    fetchDispatches();
    const interval = setInterval(fetchDispatches, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDispatches = async () => {
    try {
      // Fetch all dispatches (no status filter to show drafts too)
      const response = await apiClient.getDispatches({});
      setDispatches(response.items || response);
      setSelectedIds([]);
      if (loading) setLoading(false);
    } catch (error) {
      toast.error('배차 목록을 불러오는데 실패했습니다');
      if (loading) setLoading(false);
    }
  };

  const handleSelectAll = () => {
    if (selectedIds.length === dispatches.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(dispatches.map(d => d.id));
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
        
        fetchDispatches();
        setSelectedIds([]);
      } else {
        toast.error('배차 확정에 실패했습니다');
      }
    } catch (error: any) {
      console.error('배차 확정 실패:', error);
      toast.error(error.response?.data?.detail || '배차 확정에 실패했습니다');
    }
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
    return (
      <Layout>
        <Loading />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">배차 관리</h1>
            <p className="text-gray-600 mt-2">실시간 배송 현황을 모니터링하세요</p>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">전체 배차</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{dispatches.length}</p>
              </div>
              <Truck className="text-gray-400" size={32} />
            </div>
          </Card>
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">진행 중</p>
                <p className="text-2xl font-bold text-green-600 mt-1">
                  {dispatches.filter((d) => d.status === '진행중').length}
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
                  {dispatches.filter((d) => d.status === '확정').length}
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
                  {dispatches.filter((d) => d.status === 'COMPLETED').length}
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
              {dispatches
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

        {/* Bulk Actions */}
        {selectedIds.length > 0 && (
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
                  dispatches.map((dispatch) => (
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
                            onClick={() => setSelectedDispatch(dispatch)}
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
      </div>
    </Layout>
  );
};

export default DispatchesPage;
