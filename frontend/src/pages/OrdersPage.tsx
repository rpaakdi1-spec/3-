import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/common/Layout';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Loading from '../components/common/Loading';
import OrderModal from '../components/orders/OrderModal';
import apiClient from '../api/client';
import { Order } from '../types';
import { Package, Plus, Search, Filter, Upload, Download, Trash2, Edit2, FileSpreadsheet, Zap, Calendar, Clock } from 'lucide-react';
import toast from 'react-hot-toast';

const OrdersPage: React.FC = () => {
  const navigate = useNavigate();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [uploading, setUploading] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getOrders();
      // Safely extract items array
      const items = response.items || response.data?.items || response.data || [];
      // Ensure items is an array
      const ordersArray = Array.isArray(items) ? items : [];
      setOrders(ordersArray);
      setSelectedIds([]); // Reset selection
    } catch (error) {
      console.error('Failed to fetch orders:', error);
      toast.error('주문 목록을 불러오는데 실패했습니다');
      setOrders([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAll = () => {
    if (selectedIds.length === filteredOrders.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredOrders.map(o => o.id));
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
    if (!window.confirm('이 주문을 삭제하시겠습니까?')) return;
    
    try {
      await apiClient.deleteOrder(id);
      toast.success('주문이 삭제되었습니다');
      fetchOrders();
    } catch (error) {
      toast.error('주문 삭제에 실패했습니다');
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) {
      toast.error('삭제할 주문을 선택해주세요');
      return;
    }
    
    if (!window.confirm(`선택한 ${selectedIds.length}개의 주문을 삭제하시겠습니까?`)) return;
    
    try {
      await Promise.all(selectedIds.map(id => apiClient.deleteOrder(id)));
      toast.success(`${selectedIds.length}개의 주문이 삭제되었습니다`);
      fetchOrders();
    } catch (error) {
      toast.error('일괄 삭제에 실패했습니다');
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await fetch('/api/v1/orders/template/download');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'orders_template.xlsx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('양식 파일이 다운로드되었습니다');
    } catch (error) {
      toast.error('양식 다운로드에 실패했습니다');
    }
  };

  const handleDownloadAll = async () => {
    try {
      const params = new URLSearchParams();
      if (statusFilter !== 'ALL') params.append('status', statusFilter);
      
      const response = await fetch(`/api/v1/orders/export/excel?${params.toString()}`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `orders_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('주문 목록이 다운로드되었습니다');
    } catch (error) {
      toast.error('다운로드에 실패했습니다');
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploading(true);
      const response = await fetch('/api/v1/orders/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      const result = await response.json();
      toast.success(`${result.created || 0}개의 주문이 등록되었습니다`);
      fetchOrders();
    } catch (error) {
      toast.error('파일 업로드에 실패했습니다');
    } finally {
      setUploading(false);
      event.target.value = ''; // Reset file input
    }
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      PENDING: 'bg-yellow-100 text-yellow-800',
      ASSIGNED: 'bg-blue-100 text-blue-800',
      IN_TRANSIT: 'bg-green-100 text-green-800',
      DELIVERED: 'bg-gray-100 text-gray-800',
      CANCELLED: 'bg-red-100 text-red-800',
    };
    const labels = {
      PENDING: '배차대기',
      ASSIGNED: '배차완료',
      IN_TRANSIT: '운송중',
      DELIVERED: '배송완료',
      CANCELLED: '취소',
    };
    return (
      <span className={`px-3 py-1 rounded-full text-sm font-medium ${styles[status as keyof typeof styles]}`}>
        {labels[status as keyof typeof labels] || status}
      </span>
    );
  };

  const isPastOrder = (order: Order): boolean => {
    const now = new Date();
    const pickupTime = new Date(`${order.order_date}T${order.pickup_time_start || '00:00:00'}`);
    return pickupTime < now && order.status === 'PENDING';
  };

  const formatDateTime = (date: string, time?: string): string => {
    const d = new Date(date);
    const dateStr = `${d.getMonth() + 1}/${d.getDate()}`;
    if (time) {
      const timeStr = time.substring(0, 5); // HH:MM
      return `${dateStr} ${timeStr}`;
    }
    return dateStr;
  };

  const filteredOrders = orders.filter((order) => {
    const matchesSearch =
      order.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (order.client_name?.toLowerCase() || '').includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || order.status === statusFilter;
    
    // 날짜 필터링
    let matchesDate = true;
    if (startDate || endDate) {
      const orderDate = new Date(order.order_date);
      if (startDate && endDate) {
        matchesDate = orderDate >= new Date(startDate) && orderDate <= new Date(endDate);
      } else if (startDate) {
        matchesDate = orderDate >= new Date(startDate);
      } else if (endDate) {
        matchesDate = orderDate <= new Date(endDate);
      }
    }
    
    return matchesSearch && matchesStatus && matchesDate;
  });

  // Calculate pending orders count for AI dispatch
  const pendingOrders = orders.filter(order => 
    order.status === 'PENDING'
  );
  const pendingOrdersCount = pendingOrders.length;

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
            <h1 className="text-3xl font-bold text-gray-900">주문 관리</h1>
            <p className="text-gray-600 mt-2">배송 주문을 관리하세요</p>
          </div>
          <div className="flex flex-wrap gap-2 mt-4 md:mt-0">
            <Button 
              variant={pendingOrdersCount > 0 ? "success" : "secondary"}
              onClick={() => {
                const orderIds = pendingOrders.map(o => o.id).join(',');
                navigate(`/optimization?order_ids=${orderIds}`);
              }}
              className={pendingOrdersCount > 0 ? "animate-pulse" : ""}
              disabled={pendingOrdersCount === 0}
              title={pendingOrdersCount === 0 ? "배차대기 주문이 없습니다" : "AI 배차 최적화 페이지로 이동"}
            >
              <Zap size={20} className="mr-2" />
              AI 배차 {pendingOrdersCount > 0 ? `(${pendingOrdersCount}건)` : ''}
            </Button>
            <Button 
              variant="secondary"
              onClick={handleDownloadTemplate}
            >
              <FileSpreadsheet size={20} className="mr-2" />
              양식 다운로드
            </Button>
            <label>
              <input
                type="file"
                accept=".xlsx,.xls"
                onChange={handleFileUpload}
                className="hidden"
                disabled={uploading}
              />
              <Button 
                variant="secondary"
                as="span"
                disabled={uploading}
              >
                <Upload size={20} className="mr-2" />
                {uploading ? '업로드 중...' : '엑셀 업로드'}
              </Button>
            </label>
            <Button 
              variant="secondary"
              onClick={handleDownloadAll}
            >
              <Download size={20} className="mr-2" />
              전체 다운로드
            </Button>
            <Button 
              variant="primary"
              onClick={() => {
                setSelectedOrder(null);
                setModalOpen(true);
              }}
            >
              <Plus size={20} className="mr-2" />
              신규 등록
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="col-span-1 md:col-span-2 lg:col-span-2">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  placeholder="주문번호 또는 거래처명 검색"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>
            <div>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="date"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  placeholder="시작일"
                />
              </div>
            </div>
            <div>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="date"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  placeholder="종료일"
                />
              </div>
            </div>
            <div>
              <select
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="ALL">전체 상태</option>
                <option value="PENDING">배차대기</option>
                <option value="ASSIGNED">배차완료</option>
                <option value="IN_TRANSIT">운송중</option>
                <option value="DELIVERED">배송완료</option>
                <option value="CANCELLED">취소</option>
              </select>
            </div>
          </div>
          <div className="mt-4 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              {startDate || endDate ? (
                <>
                  {startDate && <span>시작: {new Date(startDate).toLocaleDateString('ko-KR')}</span>}
                  {startDate && endDate && <span className="mx-2">~</span>}
                  {endDate && <span>종료: {new Date(endDate).toLocaleDateString('ko-KR')}</span>}
                </>
              ) : (
                <span>전체 기간</span>
              )}
            </div>
            <Button 
              variant="secondary" 
              size="sm"
              onClick={() => {
                setSearchTerm('');
                setStatusFilter('ALL');
                setStartDate('');
                setEndDate('');
              }}
            >
              <Filter size={16} className="mr-2" />
              필터 초기화
            </Button>
          </div>
        </Card>

        {/* Bulk Actions */}
        {selectedIds.length > 0 && (
          <Card>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">
                {selectedIds.length}개 항목 선택됨
              </span>
              <Button 
                variant="danger"
                size="sm"
                onClick={handleBulkDelete}
              >
                <Trash2 size={16} className="mr-2" />
                선택 항목 삭제
              </Button>
            </div>
          </Card>
        )}

        {/* Orders Table */}
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="w-12 py-3 px-4">
                    <input
                      type="checkbox"
                      checked={filteredOrders.length > 0 && selectedIds.length === filteredOrders.length}
                      onChange={handleSelectAll}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                    />
                  </th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">주문번호</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">상차 날짜/시간</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">거래처</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">상차지</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">하차지</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">화물유형</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">팔레트</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">상태</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">작업</th>
                </tr>
              </thead>
              <tbody>
                {filteredOrders.length === 0 ? (
                  <tr>
                    <td colSpan={10} className="text-center py-8 text-gray-500">
                      <Package size={48} className="mx-auto mb-4 text-gray-300" />
                      <p>주문이 없습니다</p>
                    </td>
                  </tr>
                ) : (
                  filteredOrders.map((order) => {
                    const isPast = isPastOrder(order);
                    return (
                      <tr 
                        key={order.id} 
                        className={`border-b border-gray-100 hover:bg-gray-50 ${isPast ? 'bg-red-50' : ''}`}
                      >
                        <td className="py-3 px-4">
                          <input
                            type="checkbox"
                            checked={selectedIds.includes(order.id)}
                            onChange={() => handleSelectOne(order.id)}
                            className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
                          />
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-blue-600">{order.order_number}</span>
                            {isPast && (
                              <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-medium">
                                지난 오더
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-1 text-sm">
                            <Clock size={14} className="text-gray-400" />
                            <span>{formatDateTime(order.order_date, order.pickup_time_start)}</span>
                          </div>
                          {order.pickup_time_start && order.pickup_time_end && (
                            <div className="text-xs text-gray-500 mt-1">
                              {order.pickup_time_start.substring(0, 5)} ~ {order.pickup_time_end.substring(0, 5)}
                            </div>
                          )}
                        </td>
                        <td className="py-3 px-4">{order.client_name || order.pickup_client_name || order.delivery_client_name || '-'}</td>
                        <td className="py-3 px-4 max-w-xs truncate">{order.pickup_address || order.pickup_client_name || '-'}</td>
                        <td className="py-3 px-4 max-w-xs truncate">{order.delivery_address || order.delivery_client_name || '-'}</td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                            {order.temperature_zone || order.cargo_type || '-'}
                          </span>
                        </td>
                        <td className="py-3 px-4">{order.pallet_count || 0}개</td>
                        <td className="py-3 px-4">{getStatusBadge(order.status)}</td>
                        <td className="py-3 px-4">
                          <div className="flex space-x-2">
                            <Button 
                              size="sm" 
                              variant="secondary"
                              onClick={() => {
                                setSelectedOrder(order);
                                setModalOpen(true);
                              }}
                            >
                              <Edit2 size={14} className="mr-1" />
                              수정
                            </Button>
                            <Button 
                              size="sm" 
                              variant="danger"
                              onClick={() => handleDelete(order.id)}
                            >
                              <Trash2 size={14} className="mr-1" />
                              삭제
                            </Button>
                          </div>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </Card>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600">전체 주문</p>
              <p className="text-3xl font-bold text-gray-900 mt-2">{orders.length}</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600">대기 중</p>
              <p className="text-3xl font-bold text-yellow-600 mt-2">
                {orders.filter((o) => o.status === 'PENDING').length}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600">진행 중</p>
              <p className="text-3xl font-bold text-green-600 mt-2">
                {orders.filter((o) => o.status === 'IN_PROGRESS').length}
              </p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-sm text-gray-600">완료</p>
              <p className="text-3xl font-bold text-gray-600 mt-2">
                {orders.filter((o) => o.status === 'COMPLETED').length}
              </p>
            </div>
          </Card>
        </div>
      </div>

      <OrderModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSelectedOrder(null);
        }}
        onSuccess={() => {
          setModalOpen(false);
          setSelectedOrder(null);
          fetchOrders();
          toast.success(selectedOrder ? '주문이 수정되었습니다' : '주문이 등록되었습니다');
        }}
        order={selectedOrder}
      />
    </Layout>
  );
};

export default OrdersPage;
