import React, { useState, useEffect } from 'react';
import {
  Wrench,
  Package,
  Calendar,
  ClipboardCheck,
  AlertTriangle,
  CheckCircle,
  Clock,
  TrendingUp,
  Filter,
  Search,
  RefreshCw,
  Plus,
  DollarSign,
  FileText,
  Tool,
  Truck,
  PlayCircle,
  StopCircle,
  Bell
} from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface MaintenanceRecord {
  id: number;
  maintenance_number: string;
  vehicle: {
    id: number;
    plate_number: string;
    code: string;
  };
  maintenance_type: string;
  status: string;
  priority: string;
  scheduled_date: string;
  started_at?: string;
  completed_at?: string;
  odometer_reading?: number;
  service_center?: string;
  mechanic_name?: string;
  labor_cost: number;
  parts_cost: number;
  total_cost: number;
  description?: string;
  findings?: string;
  recommendations?: string;
}

interface VehiclePart {
  id: number;
  part_number: string;
  part_name: string;
  category: string;
  manufacturer?: string;
  quantity_in_stock: number;
  minimum_stock: number;
  unit: string;
  unit_price: number;
  supplier?: string;
}

interface MaintenanceSchedule {
  id: number;
  vehicle: {
    id: number;
    plate_number: string;
  };
  maintenance_type: string;
  interval_km?: number;
  interval_months?: number;
  last_maintenance_date?: string;
  last_maintenance_odometer?: number;
  next_maintenance_date?: string;
  next_maintenance_odometer?: number;
  is_overdue: boolean;
}

interface VehicleInspection {
  id: number;
  vehicle: {
    id: number;
    plate_number: string;
  };
  inspection_type: string;
  inspection_date: string;
  expiry_date: string;
  pass_status: boolean;
  inspection_cost?: number;
  inspection_center?: string;
}

interface MaintenanceAlert {
  vehicle_id: number;
  vehicle_plate: string;
  alert_type: 'overdue' | 'upcoming' | 'expiring_inspection' | 'low_stock';
  message: string;
  severity: 'high' | 'medium' | 'low';
  scheduled_date?: string;
  expiry_date?: string;
  days_until?: number;
  maintenance_type?: string;
  part_name?: string;
  current_stock?: number;
  minimum_stock?: number;
}

const VehicleMaintenancePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'records' | 'parts' | 'schedules' | 'inspections' | 'alerts'>('records');
  const [records, setRecords] = useState<MaintenanceRecord[]>([]);
  const [parts, setParts] = useState<VehiclePart[]>([]);
  const [schedules, setSchedules] = useState<MaintenanceSchedule[]>([]);
  const [inspections, setInspections] = useState<VehicleInspection[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [showLowStock, setShowLowStock] = useState(false);
  const [showOverdue, setShowOverdue] = useState(false);
  const [alerts, setAlerts] = useState<{
    overdue: MaintenanceAlert[];
    upcoming: MaintenanceAlert[];
    expiring: MaintenanceAlert[];
    low_stock: MaintenanceAlert[];
    total_count: number;
  }>({
    overdue: [],
    upcoming: [],
    expiring: [],
    low_stock: [],
    total_count: 0
  });

  useEffect(() => {
    loadData();
  }, [activeTab, statusFilter, showLowStock, showOverdue]);

  const loadData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };

      if (activeTab === 'records') {
        const params: any = { limit: 100 };
        if (statusFilter !== 'all') params.status = statusFilter;
        
        const res = await axios.get(`${API_URL}/api/v1/maintenance/records`, {
          headers,
          params
        });
        setRecords(res.data);
      } else if (activeTab === 'parts') {
        const params: any = {};
        if (showLowStock) params.low_stock = true;
        
        const res = await axios.get(`${API_URL}/api/v1/maintenance/parts`, {
          headers,
          params
        });
        setParts(res.data);
      } else if (activeTab === 'schedules') {
        const params: any = {};
        if (showOverdue) params.is_overdue = true;
        
        const res = await axios.get(`${API_URL}/api/v1/maintenance/schedules`, {
          headers,
          params
        });
        setSchedules(res.data);
      } else if (activeTab === 'inspections') {
        const res = await axios.get(`${API_URL}/api/v1/maintenance/inspections`, {
          headers,
          params: { limit: 100 }
        });
        setInspections(res.data);
      } else if (activeTab === 'alerts') {
        const res = await axios.get(`${API_URL}/api/v1/maintenance/alerts/dashboard`, {
          headers
        });
        setAlerts({
          overdue: res.data.overdue_alerts || [],
          upcoming: res.data.upcoming_alerts || [],
          expiring: res.data.expiring_alerts || [],
          low_stock: res.data.low_stock_alerts || [],
          total_count: res.data.total_alerts || 0
        });
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStartMaintenance = async (recordId: number) => {
    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_URL}/api/v1/maintenance/records/${recordId}/start`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('정비가 시작되었습니다.');
      loadData();
    } catch (error) {
      console.error('Failed to start maintenance:', error);
      alert('정비 시작에 실패했습니다.');
    }
  };

  const handleCompleteMaintenance = async (recordId: number) => {
    const laborCost = prompt('인건비를 입력하세요 (원):');
    if (!laborCost) return;

    const partsCost = prompt('부품비를 입력하세요 (원):');
    if (!partsCost) return;

    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_URL}/api/v1/maintenance/records/${recordId}/complete`,
        {
          labor_cost: parseFloat(laborCost),
          parts_cost: parseFloat(partsCost)
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('정비가 완료되었습니다.');
      loadData();
    } catch (error) {
      console.error('Failed to complete maintenance:', error);
      alert('정비 완료 처리에 실패했습니다.');
    }
  };

  const handleUpdateStock = async (partId: number, currentStock: number) => {
    const change = prompt(`현재 재고: ${currentStock}개\n변경량을 입력하세요 (양수: 입고, 음수: 출고):`);
    if (!change) return;

    try {
      const token = localStorage.getItem('access_token');
      await axios.post(
        `${API_URL}/api/v1/maintenance/parts/${partId}/stock`,
        { quantity_change: parseInt(change) },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('재고가 업데이트되었습니다.');
      loadData();
    } catch (error) {
      console.error('Failed to update stock:', error);
      alert('재고 업데이트에 실패했습니다.');
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; color: string; icon: JSX.Element }> = {
      SCHEDULED: { label: '예정', color: 'bg-blue-100 text-blue-800', icon: <Calendar className="w-3 h-3" /> },
      IN_PROGRESS: { label: '진행중', color: 'bg-yellow-100 text-yellow-800', icon: <Clock className="w-3 h-3" /> },
      COMPLETED: { label: '완료', color: 'bg-green-100 text-green-800', icon: <CheckCircle className="w-3 h-3" /> },
      CANCELLED: { label: '취소', color: 'bg-gray-100 text-gray-600', icon: <StopCircle className="w-3 h-3" /> }
    };

    const config = statusConfig[status] || statusConfig.SCHEDULED;
    
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        {config.icon}
        {config.label}
      </span>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const priorityConfig: Record<string, { label: string; color: string }> = {
      '낮음': { label: '낮음', color: 'bg-gray-100 text-gray-600' },
      '보통': { label: '보통', color: 'bg-blue-100 text-blue-600' },
      '높음': { label: '높음', color: 'bg-orange-100 text-orange-600' },
      '긴급': { label: '긴급', color: 'bg-red-100 text-red-600' }
    };

    const config = priorityConfig[priority] || priorityConfig['보통'];
    
    return (
      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${config.color}`}>
        {config.label}
      </span>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW'
    }).format(amount);
  };

  const getMaintenanceTypeIcon = (type: string) => {
    const icons: Record<string, JSX.Element> = {
      '정기점검': <ClipboardCheck className="w-5 h-5 text-blue-500" />,
      '수리': <Tool className="w-5 h-5 text-orange-500" />,
      '부품교체': <Package className="w-5 h-5 text-purple-500" />,
      '오일교환': <Wrench className="w-5 h-5 text-green-500" />,
      '타이어교체': <Truck className="w-5 h-5 text-gray-600" />
    };
    return icons[type] || <Wrench className="w-5 h-5 text-gray-500" />;
  };

  const filteredRecords = records.filter(record => {
    const matchesSearch = 
      record.maintenance_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      record.vehicle.plate_number.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesSearch;
  });

  const filteredParts = parts.filter(part => {
    const matchesSearch = 
      part.part_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      part.part_name.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesSearch;
  });

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
            <Wrench className="w-8 h-8" />
            차량 유지보수 관리
          </h1>
          <p className="text-gray-600">정비 기록, 부품 재고, 정비 스케줄 및 검사 관리</p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">총 정비 건수</span>
              <FileText className="w-5 h-5 text-blue-500" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{records.length}</p>
            <p className="text-xs text-gray-500 mt-1">이번 달</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">진행중</span>
              <Clock className="w-5 h-5 text-yellow-500" />
            </div>
            <p className="text-2xl font-bold text-yellow-600">
              {records.filter(r => r.status === 'IN_PROGRESS').length}
            </p>
            <p className="text-xs text-gray-500 mt-1">정비 작업</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">재고 부족</span>
              <AlertTriangle className="w-5 h-5 text-red-500" />
            </div>
            <p className="text-2xl font-bold text-red-600">
              {parts.filter(p => p.quantity_in_stock <= p.minimum_stock).length}
            </p>
            <p className="text-xs text-gray-500 mt-1">부품</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">총 알림</span>
              <Bell className="w-5 h-5 text-purple-500" />
            </div>
            <p className="text-2xl font-bold text-purple-600">
              {alerts.total_count}
            </p>
            <p className="text-xs text-gray-500 mt-1">확인 필요</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('records')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'records'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Wrench className="w-4 h-4" />
                  정비 기록
                </div>
              </button>
              <button
                onClick={() => setActiveTab('parts')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'parts'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Package className="w-4 h-4" />
                  부품 재고
                </div>
              </button>
              <button
                onClick={() => setActiveTab('schedules')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'schedules'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  정비 스케줄
                </div>
              </button>
              <button
                onClick={() => setActiveTab('inspections')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'inspections'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <ClipboardCheck className="w-4 h-4" />
                  차량 검사
                </div>
              </button>
              <button
                onClick={() => setActiveTab('alerts')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'alerts'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-2">
                  <Bell className="w-4 h-4" />
                  알림
                  {alerts.total_count > 0 && (
                    <span className="bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                      {alerts.total_count}
                    </span>
                  )}
                </div>
              </button>
            </nav>
          </div>

          {/* Filters */}
          <div className="p-4 border-b border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="검색..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {activeTab === 'records' && (
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">전체 상태</option>
                  <option value="SCHEDULED">예정</option>
                  <option value="IN_PROGRESS">진행중</option>
                  <option value="COMPLETED">완료</option>
                  <option value="CANCELLED">취소</option>
                </select>
              )}

              {activeTab === 'parts' && (
                <label className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={showLowStock}
                    onChange={(e) => setShowLowStock(e.target.checked)}
                    className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="text-sm text-gray-700">재고 부족만</span>
                </label>
              )}

              {activeTab === 'schedules' && (
                <label className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                  <input
                    type="checkbox"
                    checked={showOverdue}
                    onChange={(e) => setShowOverdue(e.target.checked)}
                    className="w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="text-sm text-gray-700">연체만</span>
                </label>
              )}

              <button
                onClick={loadData}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2 ml-auto"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                새로고침
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            {activeTab === 'records' && (
              <div className="space-y-4">
                {filteredRecords.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    정비 기록이 없습니다.
                  </div>
                ) : (
                  filteredRecords.map((record) => (
                    <div key={record.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-start gap-3">
                          <div className="mt-1">
                            {getMaintenanceTypeIcon(record.maintenance_type)}
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900">{record.maintenance_number}</h3>
                            <p className="text-sm text-gray-600 mt-1">
                              {record.vehicle.plate_number} ({record.vehicle.code})
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                              {record.maintenance_type} • 예정일: {record.scheduled_date}
                            </p>
                            {record.odometer_reading && (
                              <p className="text-xs text-gray-500">
                                주행거리: {record.odometer_reading.toLocaleString()}km
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="flex gap-2 mb-2">
                            {getStatusBadge(record.status)}
                            {getPriorityBadge(record.priority)}
                          </div>
                          {record.total_cost > 0 && (
                            <p className="text-lg font-bold text-gray-900">
                              {formatCurrency(record.total_cost)}
                            </p>
                          )}
                        </div>
                      </div>

                      {record.service_center && (
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-4">
                          <div>
                            <span className="text-gray-500">정비소:</span>
                            <span className="ml-2 text-gray-900">{record.service_center}</span>
                          </div>
                          {record.mechanic_name && (
                            <div>
                              <span className="text-gray-500">정비사:</span>
                              <span className="ml-2 text-gray-900">{record.mechanic_name}</span>
                            </div>
                          )}
                          {record.labor_cost > 0 && (
                            <div>
                              <span className="text-gray-500">인건비:</span>
                              <span className="ml-2 text-gray-900">{formatCurrency(record.labor_cost)}</span>
                            </div>
                          )}
                          {record.parts_cost > 0 && (
                            <div>
                              <span className="text-gray-500">부품비:</span>
                              <span className="ml-2 text-gray-900">{formatCurrency(record.parts_cost)}</span>
                            </div>
                          )}
                        </div>
                      )}

                      {record.description && (
                        <p className="text-sm text-gray-600 mb-3">
                          <strong>설명:</strong> {record.description}
                        </p>
                      )}

                      {record.findings && (
                        <p className="text-sm text-gray-600 mb-3">
                          <strong>발견사항:</strong> {record.findings}
                        </p>
                      )}

                      {record.recommendations && (
                        <p className="text-sm text-orange-600 mb-3">
                          <strong>권고사항:</strong> {record.recommendations}
                        </p>
                      )}

                      <div className="flex flex-wrap gap-2">
                        {record.status === 'SCHEDULED' && (
                          <button
                            onClick={() => handleStartMaintenance(record.id)}
                            className="px-3 py-1.5 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors flex items-center gap-1"
                          >
                            <PlayCircle className="w-4 h-4" />
                            정비 시작
                          </button>
                        )}
                        
                        {record.status === 'IN_PROGRESS' && (
                          <button
                            onClick={() => handleCompleteMaintenance(record.id)}
                            className="px-3 py-1.5 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors flex items-center gap-1"
                          >
                            <CheckCircle className="w-4 h-4" />
                            정비 완료
                          </button>
                        )}
                        
                        <button
                          className="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors flex items-center gap-1"
                        >
                          <FileText className="w-4 h-4" />
                          상세보기
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'parts' && (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        부품 번호
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        부품명
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        카테고리
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        재고
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        단가
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        공급업체
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        작업
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredParts.map((part) => (
                      <tr key={part.id} className={part.quantity_in_stock <= part.minimum_stock ? 'bg-red-50' : ''}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {part.part_number}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {part.part_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {part.category}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-2">
                            <span className={`text-sm font-medium ${
                              part.quantity_in_stock <= part.minimum_stock
                                ? 'text-red-600'
                                : 'text-gray-900'
                            }`}>
                              {part.quantity_in_stock} {part.unit}
                            </span>
                            {part.quantity_in_stock <= part.minimum_stock && (
                              <AlertTriangle className="w-4 h-4 text-red-500" />
                            )}
                          </div>
                          <span className="text-xs text-gray-500">
                            최소: {part.minimum_stock} {part.unit}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {formatCurrency(part.unit_price)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {part.supplier || '-'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          <button
                            onClick={() => handleUpdateStock(part.id, part.quantity_in_stock)}
                            className="text-blue-600 hover:text-blue-900 font-medium"
                          >
                            재고 조정
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {activeTab === 'schedules' && (
              <div className="space-y-4">
                {schedules.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    정비 스케줄이 없습니다.
                  </div>
                ) : (
                  schedules.map((schedule) => (
                    <div key={schedule.id} className={`border rounded-lg p-4 ${
                      schedule.is_overdue ? 'border-red-300 bg-red-50' : 'border-gray-200'
                    }`}>
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {schedule.vehicle.plate_number}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">
                            {schedule.maintenance_type}
                          </p>
                          
                          <div className="mt-3 space-y-1 text-sm">
                            {schedule.interval_km && (
                              <p className="text-gray-600">
                                주기: {schedule.interval_km.toLocaleString()}km마다
                              </p>
                            )}
                            {schedule.interval_months && (
                              <p className="text-gray-600">
                                주기: {schedule.interval_months}개월마다
                              </p>
                            )}
                            {schedule.last_maintenance_date && (
                              <p className="text-gray-600">
                                마지막 정비: {schedule.last_maintenance_date}
                                {schedule.last_maintenance_odometer && (
                                  <span> ({schedule.last_maintenance_odometer.toLocaleString()}km)</span>
                                )}
                              </p>
                            )}
                            {schedule.next_maintenance_date && (
                              <p className={schedule.is_overdue ? 'text-red-600 font-medium' : 'text-gray-600'}>
                                다음 정비: {schedule.next_maintenance_date}
                                {schedule.next_maintenance_odometer && (
                                  <span> ({schedule.next_maintenance_odometer.toLocaleString()}km)</span>
                                )}
                              </p>
                            )}
                          </div>
                        </div>
                        
                        {schedule.is_overdue && (
                          <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            <AlertTriangle className="w-3 h-3" />
                            정비 필요
                          </span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'inspections' && (
              <div className="space-y-4">
                {inspections.length === 0 ? (
                  <div className="text-center py-12 text-gray-500">
                    검사 기록이 없습니다.
                  </div>
                ) : (
                  inspections.map((inspection) => (
                    <div key={inspection.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {inspection.vehicle.plate_number}
                          </h3>
                          <p className="text-sm text-gray-600 mt-1">
                            {inspection.inspection_type}
                          </p>
                          
                          <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="text-gray-500">검사일:</span>
                              <span className="ml-2 text-gray-900">{inspection.inspection_date}</span>
                            </div>
                            <div>
                              <span className="text-gray-500">만료일:</span>
                              <span className="ml-2 text-gray-900">{inspection.expiry_date}</span>
                            </div>
                            {inspection.inspection_center && (
                              <div>
                                <span className="text-gray-500">검사소:</span>
                                <span className="ml-2 text-gray-900">{inspection.inspection_center}</span>
                              </div>
                            )}
                            {inspection.inspection_cost && (
                              <div>
                                <span className="text-gray-500">비용:</span>
                                <span className="ml-2 text-gray-900">{formatCurrency(inspection.inspection_cost)}</span>
                              </div>
                            )}
                          </div>
                        </div>
                        
                        <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${
                          inspection.pass_status
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {inspection.pass_status ? (
                            <>
                              <CheckCircle className="w-3 h-3" />
                              합격
                            </>
                          ) : (
                            <>
                              <AlertTriangle className="w-3 h-3" />
                              불합격
                            </>
                          )}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'alerts' && (
              <div className="space-y-6">
                {/* Overdue Maintenance */}
                {alerts.overdue.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 text-red-500" />
                      연체된 정비 ({alerts.overdue.length})
                    </h3>
                    <div className="space-y-3">
                      {alerts.overdue.map((alert, idx) => (
                        <div key={idx} className="border-l-4 border-red-500 bg-red-50 p-4 rounded">
                          <div className="flex items-start justify-between">
                            <div>
                              <h4 className="font-semibold text-gray-900">{alert.vehicle_plate}</h4>
                              <p className="text-sm text-gray-700 mt-1">{alert.message}</p>
                              {alert.scheduled_date && (
                                <p className="text-xs text-gray-500 mt-1">예정일: {alert.scheduled_date}</p>
                              )}
                            </div>
                            <span className="bg-red-100 text-red-800 text-xs font-medium px-2.5 py-0.5 rounded">
                              긴급
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Upcoming Maintenance */}
                {alerts.upcoming.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Clock className="w-5 h-5 text-yellow-500" />
                      다가오는 정비 ({alerts.upcoming.length})
                    </h3>
                    <div className="space-y-3">
                      {alerts.upcoming.map((alert, idx) => (
                        <div key={idx} className="border-l-4 border-yellow-500 bg-yellow-50 p-4 rounded">
                          <div className="flex items-start justify-between">
                            <div>
                              <h4 className="font-semibold text-gray-900">{alert.vehicle_plate}</h4>
                              <p className="text-sm text-gray-700 mt-1">{alert.message}</p>
                              {alert.scheduled_date && (
                                <p className="text-xs text-gray-500 mt-1">예정일: {alert.scheduled_date}</p>
                              )}
                            </div>
                            <span className="bg-yellow-100 text-yellow-800 text-xs font-medium px-2.5 py-0.5 rounded">
                              주의
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Expiring Inspections */}
                {alerts.expiring.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <ClipboardCheck className="w-5 h-5 text-orange-500" />
                      만료 예정 검사 ({alerts.expiring.length})
                    </h3>
                    <div className="space-y-3">
                      {alerts.expiring.map((alert, idx) => (
                        <div key={idx} className="border-l-4 border-orange-500 bg-orange-50 p-4 rounded">
                          <div className="flex items-start justify-between">
                            <div>
                              <h4 className="font-semibold text-gray-900">{alert.vehicle_plate}</h4>
                              <p className="text-sm text-gray-700 mt-1">{alert.message}</p>
                              {alert.expiry_date && (
                                <p className="text-xs text-gray-500 mt-1">만료일: {alert.expiry_date}</p>
                              )}
                            </div>
                            <span className="bg-orange-100 text-orange-800 text-xs font-medium px-2.5 py-0.5 rounded">
                              경고
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Low Stock Parts */}
                {alerts.low_stock.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                      <Package className="w-5 h-5 text-blue-500" />
                      부품 재고 부족 ({alerts.low_stock.length})
                    </h3>
                    <div className="space-y-3">
                      {alerts.low_stock.map((alert, idx) => (
                        <div key={idx} className="border-l-4 border-blue-500 bg-blue-50 p-4 rounded">
                          <div className="flex items-start justify-between">
                            <div>
                              <h4 className="font-semibold text-gray-900">{alert.part_name}</h4>
                              <p className="text-sm text-gray-700 mt-1">{alert.message}</p>
                              {alert.current_stock !== undefined && alert.minimum_stock !== undefined && (
                                <p className="text-xs text-gray-500 mt-1">
                                  현재 재고: {alert.current_stock} / 최소 재고: {alert.minimum_stock}
                                </p>
                              )}
                            </div>
                            <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                              재고 부족
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* No Alerts */}
                {alerts.total_count === 0 && (
                  <div className="text-center py-12">
                    <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">알림 없음</h3>
                    <p className="text-gray-500">모든 정비와 검사가 정상입니다.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VehicleMaintenancePage;
