import React, { useState, useEffect } from 'react';
import { Truck, Plus, Edit2, Trash2, ThermometerSnowflake, RefreshCw, Upload, Download, FileSpreadsheet, CheckSquare } from 'lucide-react';
import { toast } from 'react-hot-toast';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Loading from '../components/common/Loading';
import { vehiclesAPI } from '../services/api';
import { useResponsive } from '../hooks/useResponsive';
import { MobileVehicleCard } from '../components/mobile/MobileVehicleCard';

interface Vehicle {
  id: number;
  code: string;
  plate_number: string;
  vehicle_type: string;
  driver_name?: string;
  driver_phone?: string;
  max_pallets: number;
  max_weight_kg: number;
  tonnage: number;
  forklift_operator_available: boolean;
  length_m?: number;
  min_temp_celsius?: number;
  max_temp_celsius?: number;
  garage_address?: string;
  status: string;
  uvis_device_id?: string;
  uvis_enabled: boolean;
  is_active: boolean;
  created_at: string;
  gps_data?: {
    latitude?: number;
    longitude?: number;
    is_engine_on?: boolean;
    speed_kmh?: number;
    temperature_a?: number;
    temperature_b?: number;
    battery_voltage?: number;
    last_updated?: string;
    gps_datetime?: string;
  };
}

const VehiclesPage: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [uploading, setUploading] = useState(false);
  const { isMobile } = useResponsive();
  
  const [formData, setFormData] = useState({
    code: '',
    plate_number: '',
    vehicle_type: '냉동',
    driver_name: '',
    driver_phone: '',
    max_pallets: '',
    max_weight_kg: '',
    tonnage: '',
    forklift_operator_available: false,
    length_m: '',
    min_temp_celsius: '',
    max_temp_celsius: '',
    garage_address: '',
    status: '운행가능'
  });

  useEffect(() => {
    fetchVehicles();
  }, []);

  const fetchVehicles = async () => {
    try {
      // Include GPS data in the request
      const response = await vehiclesAPI.list();
      // Backend returns { total, items } structure
      setVehicles(response.data.items || []);
      setSelectedIds([]);
    } catch (error) {
      console.error('Failed to fetch vehicles:', error);
      setVehicles([]); // Set empty array on error
    } finally {
      setLoading(false);
    }
  };

  const handleSelectAll = () => {
    if (selectedIds.length === filteredVehicles.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(filteredVehicles.map(v => v.id));
    }
  };

  const handleSelectOne = (id: number) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(selectedId => selectedId !== id));
    } else {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) {
      toast.error('삭제할 차량을 선택해주세요');
      return;
    }
    
    if (!window.confirm(`선택한 ${selectedIds.length}개의 차량을 삭제하시겠습니까?`)) return;
    
    try {
      await Promise.all(selectedIds.map(id => vehiclesAPI.delete(id)));
      toast.success(`${selectedIds.length}개의 차량이 삭제되었습니다`);
      fetchVehicles();
    } catch (error) {
      toast.error('일괄 삭제에 실패했습니다');
    }
  };

  const handleDownloadTemplate = async () => {
    try {
      const response = await fetch('/api/v1/vehicles/template/download');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'vehicles_template.xlsx';
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
      const response = await fetch('/api/v1/vehicles/export/excel');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `vehicles_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('차량 목록이 다운로드되었습니다');
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
      const response = await fetch('/api/v1/vehicles/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Upload failed');

      const result = await response.json();
      toast.success(`${result.created || 0}개의 차량이 등록되었습니다`);
      fetchVehicles();
    } catch (error) {
      toast.error('파일 업로드에 실패했습니다');
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  };

  const openModal = (vehicle?: Vehicle) => {
    if (vehicle) {
      setEditingVehicle(vehicle);
      setFormData({
        code: vehicle.code,
        plate_number: vehicle.plate_number,
        vehicle_type: vehicle.vehicle_type,
        driver_name: vehicle.driver_name || '',
        driver_phone: vehicle.driver_phone || '',
        max_pallets: vehicle.max_pallets.toString(),
        max_weight_kg: vehicle.max_weight_kg.toString(),
        tonnage: vehicle.tonnage.toString(),
        forklift_operator_available: vehicle.forklift_operator_available || false,
        length_m: vehicle.length_m?.toString() || '',
        min_temp_celsius: vehicle.min_temp_celsius?.toString() || '',
        max_temp_celsius: vehicle.max_temp_celsius?.toString() || '',
        garage_address: vehicle.garage_address || '',
        status: vehicle.status
      });
    } else {
      setEditingVehicle(null);
      setFormData({
        code: '',
        plate_number: '',
        vehicle_type: '냉동',
        driver_name: '',
        driver_phone: '',
        max_pallets: '20',
        max_weight_kg: '5000',
        tonnage: '5',
        forklift_operator_available: false,
        length_m: '6.0',
        min_temp_celsius: '-20',
        max_temp_celsius: '-15',
        garage_address: '',
        status: '운행가능'
      });
    }
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const payload = {
        ...formData,
        max_pallets: parseInt(formData.max_pallets),
        max_weight_kg: parseFloat(formData.max_weight_kg),
        tonnage: parseFloat(formData.tonnage),
        length_m: formData.length_m ? parseFloat(formData.length_m) : undefined,
        min_temp_celsius: formData.min_temp_celsius ? parseFloat(formData.min_temp_celsius) : undefined,
        max_temp_celsius: formData.max_temp_celsius ? parseFloat(formData.max_temp_celsius) : undefined,
        garage_address: formData.garage_address || undefined,
        driver_name: formData.driver_name || undefined,
        driver_phone: formData.driver_phone || undefined
      };

      if (editingVehicle) {
        await vehiclesAPI.update(editingVehicle.id, payload);
        toast.success('차량이 수정되었습니다');
      } else {
        await vehiclesAPI.create(payload);
        toast.success('차량이 등록되었습니다');
      }

      fetchVehicles();
      setModalOpen(false);
    } catch (error) {
      console.error('Failed to save vehicle:', error);
      toast.error('차량 저장에 실패했습니다');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('정말로 이 차량을 삭제하시겠습니까?')) return;
    
    try {
      await vehiclesAPI.delete(id);
      fetchVehicles();
      toast.success('차량이 삭제되었습니다');
    } catch (error) {
      console.error('Failed to delete vehicle:', error);
      toast.error('차량 삭제에 실패했습니다');
    }
  };

  const handleSyncUvis = async () => {
    setSyncing(true);
    try {
      const response = await vehiclesAPI.syncUvis();
      const result = response.data;
      
      if (result.success) {
        toast.success(`UVIS 차량 ${result.synced}건 동기화 완료 (신규 ${result.created}건, 업데이트 ${result.updated}건)`);
        fetchVehicles();
      } else {
        toast.error(result.message || 'UVIS 동기화에 실패했습니다');
      }
    } catch (error) {
      console.error('Failed to sync UVIS vehicles:', error);
      toast.error('UVIS 동기화 중 오류가 발생했습니다');
    } finally {
      setSyncing(false);
    }
  };

  const filteredVehicles = vehicles.filter(vehicle =>
    vehicle.plate_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    vehicle.driver_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    vehicle.vehicle_type?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusBadge = (status: string) => {
    const colors: { [key: string]: string } = {
      '운행가능': 'bg-green-100 text-green-800',
      '운행중': 'bg-blue-100 text-blue-800',
      '정비중': 'bg-yellow-100 text-yellow-800',
      '운행불가': 'bg-gray-100 text-gray-800'
    };
    const labels: { [key: string]: string } = {
      '운행가능': '운행가능',
      '운행중': '운행중',
      '정비중': '정비중',
      '운행불가': '운행불가'
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status]}`}>
        {labels[status]}
      </span>
    );
  };

  if (loading) return (<Loading />
  );

  return (<div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">차량 관리</h1>
          <p className="text-gray-600 mt-1">냉장/냉동 차량 정보를 관리합니다</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button 
            onClick={handleDownloadTemplate}
            variant="secondary"
            size="sm"
          >
            <FileSpreadsheet size={18} className="mr-2" />
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
              as="span"
              variant="secondary"
              size="sm"
              disabled={uploading}
            >
              <Upload size={18} className="mr-2" />
              {uploading ? '업로드 중...' : '엑셀 업로드'}
            </Button>
          </label>
          <Button 
            onClick={handleDownloadAll}
            variant="secondary"
            size="sm"
          >
            <Download size={18} className="mr-2" />
            전체 다운로드
          </Button>
          <Button 
            onClick={handleSyncUvis} 
            disabled={syncing}
            variant="outline"
            size="sm"
          >
            <RefreshCw size={18} className={`mr-2 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? '동기화 중...' : 'UVIS 불러오기'}
          </Button>
          <Button onClick={() => openModal()} size="sm">
            <Plus size={18} className="mr-2" />
            신규 등록
          </Button>
        </div>
      </div>

      <Card className="mb-6">
        <div className="flex items-center gap-4">
          <Input
            placeholder="차량번호, 운전자명, 차량유형으로 검색..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1"
          />
          <Button 
            onClick={handleSelectAll}
            variant="outline"
            size="sm"
          >
            <CheckSquare size={18} className="mr-2" />
            {selectedIds.length === filteredVehicles.length && filteredVehicles.length > 0 ? '전체 해제' : '전체 선택'}
          </Button>
          {selectedIds.length > 0 && (
            <Button 
              onClick={handleBulkDelete}
              variant="danger"
              size="sm"
            >
              <Trash2 size={18} className="mr-2" />
              선택 삭제 ({selectedIds.length})
            </Button>
          )}
        </div>
      </Card>

      {selectedIds.length > 0 && (
        <Card className="mb-6 bg-blue-50 border-blue-200">
          <div className="flex items-center justify-between">
            <span className="text-sm text-blue-700 font-medium">
              ✓ {selectedIds.length}개 항목 선택됨
            </span>
            <Button 
              onClick={() => setSelectedIds([])}
              variant="ghost"
              size="sm"
            >
              선택 해제
            </Button>
          </div>
        </Card>
      )}

      {/* Vehicle Cards - Mobile/Desktop Views */}
      {isMobile ? (
        /* Mobile View */
        <div className="px-4 space-y-3">
          {filteredVehicles.length === 0 ? (
            <div className="text-center py-12">
              <Truck size={48} className="mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600">등록된 차량이 없습니다</p>
            </div>
          ) : (
            filteredVehicles.map((vehicle) => (
              <MobileVehicleCard
                key={vehicle.id}
                vehicle={{
                  id: vehicle.id,
                  license_plate: vehicle.plate_number,
                  vehicle_type: vehicle.vehicle_type,
                  capacity_ton: vehicle.tonnage,
                  temp_min: vehicle.min_temp_celsius,
                  temp_max: vehicle.max_temp_celsius,
                  status: vehicle.status,
                  current_location_lat: vehicle.gps_data?.latitude,
                  current_location_lon: vehicle.gps_data?.longitude,
                  last_location_update: vehicle.gps_data?.last_updated,
                }}
                onEdit={() => openModal(vehicle)}
                onViewLocation={() => {
                  if (vehicle.gps_data?.latitude && vehicle.gps_data?.longitude) {
                    window.open(
                      `https://www.google.com/maps/search/?api=1&query=${vehicle.gps_data.latitude},${vehicle.gps_data.longitude}`,
                      '_blank'
                    );
                  }
                }}
              />
            ))
          )}
        </div>
      ) : (
        /* Desktop View */
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredVehicles.map((vehicle) => (
          <Card 
            key={vehicle.id} 
            className={`hover:shadow-lg transition-shadow relative ${
              selectedIds.includes(vehicle.id) ? 'ring-2 ring-blue-500 bg-blue-50' : ''
            }`}
          >
            <div className="absolute top-4 right-4">
              <input
                type="checkbox"
                checked={selectedIds.includes(vehicle.id)}
                onChange={() => handleSelectOne(vehicle.id)}
                className="w-5 h-5 text-blue-600 rounded focus:ring-2 focus:ring-blue-500 cursor-pointer"
              />
            </div>
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                  <Truck className="text-blue-600" size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-800">{vehicle.plate_number}</h3>
                  <p className="text-sm text-gray-500">{vehicle.vehicle_type}</p>
                </div>
              </div>
              {getStatusBadge(vehicle.status)}
            </div>

            <div className="space-y-2 mb-4">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">운전자</span>
                <span className="font-medium">{vehicle.driver_name || '-'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">연락처</span>
                <span className="font-medium">{vehicle.driver_phone || '-'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">적재용량</span>
                <span className="font-medium">{vehicle.max_weight_kg}kg</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">팔레트</span>
                <span className="font-medium">{vehicle.max_pallets}개</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">지게차 운전능력</span>
                <span className={`font-semibold ${vehicle.forklift_operator_available ? 'text-green-600' : 'text-gray-400'}`}>
                  {vehicle.forklift_operator_available ? '✓ 가능' : '✗ 불가능'}
                </span>
              </div>
              {vehicle.length_m && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">적재함 길이</span>
                  <span className="font-medium">{vehicle.length_m}m</span>
                </div>
              )}
              {vehicle.min_temp_celsius !== undefined && vehicle.max_temp_celsius !== undefined && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600 flex items-center">
                    <ThermometerSnowflake size={16} className="mr-1" />
                    온도범위
                  </span>
                  <span className="font-medium">
                    {vehicle.min_temp_celsius}°C ~ {vehicle.max_temp_celsius}°C
                  </span>
                </div>
              )}
              {vehicle.garage_address && (
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">차고지</span>
                  <span className="font-medium text-xs">{vehicle.garage_address}</span>
                </div>
              )}
            </div>

            {vehicle.uvis_device_id && (
              <div className="bg-blue-50 border border-blue-200 rounded p-2 mb-4">
                <p className="text-xs text-blue-800 font-semibold mb-2">
                  UVIS: {vehicle.uvis_device_id}
                </p>
                {vehicle.gps_data && (
                  <div className="space-y-1 text-xs">
                    {/* 시동 상태 */}
                    {vehicle.gps_data.is_engine_on !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-blue-700">시동:</span>
                        <span className={`font-semibold ${vehicle.gps_data.is_engine_on ? 'text-green-600' : 'text-gray-600'}`}>
                          {vehicle.gps_data.is_engine_on ? '🟢 ON' : '⚫ OFF'}
                        </span>
                      </div>
                    )}
                    {/* 속도 */}
                    {vehicle.gps_data.speed_kmh !== undefined && (
                      <div className="flex justify-between">
                        <span className="text-blue-700">속도:</span>
                        <span className="font-semibold text-blue-900">{vehicle.gps_data.speed_kmh} km/h</span>
                      </div>
                    )}
                    {/* 온도 A */}
                    {vehicle.gps_data.temperature_a !== undefined && vehicle.gps_data.temperature_a !== null && (
                      <div className="flex justify-between">
                        <span className="text-blue-700">냉동기온도 A:</span>
                        <span className={`font-semibold ${
                          vehicle.gps_data.temperature_a < -18 ? 'text-blue-600' :
                          vehicle.gps_data.temperature_a < 5 ? 'text-cyan-600' :
                          vehicle.gps_data.temperature_a < 15 ? 'text-green-600' :
                          'text-orange-600'
                        }`}>
                          {vehicle.gps_data.temperature_a.toFixed(1)}°C
                        </span>
                      </div>
                    )}
                    {/* 온도 B */}
                    {vehicle.gps_data.temperature_b !== undefined && vehicle.gps_data.temperature_b !== null && (
                      <div className="flex justify-between">
                        <span className="text-blue-700">냉동기온도 B:</span>
                        <span className={`font-semibold ${
                          vehicle.gps_data.temperature_b < -18 ? 'text-blue-600' :
                          vehicle.gps_data.temperature_b < 5 ? 'text-cyan-600' :
                          vehicle.gps_data.temperature_b < 15 ? 'text-green-600' :
                          'text-orange-600'
                        }`}>
                          {vehicle.gps_data.temperature_b.toFixed(1)}°C
                        </span>
                      </div>
                    )}
                    {/* 위도/경도 */}
                    {vehicle.gps_data.latitude && vehicle.gps_data.longitude && (
                      <div className="flex justify-between">
                        <span className="text-blue-700">위치:</span>
                        <span className="font-medium text-blue-900">
                          {vehicle.gps_data.latitude.toFixed(4)}, {vehicle.gps_data.longitude.toFixed(4)}
                        </span>
                      </div>
                    )}
                    {/* 전압 - 중지 모드 (백엔드 데이터 추가 시까지) */}
                    {/* {vehicle.gps_data.battery_voltage && (
                      <div className="flex justify-between">
                        <span className="text-blue-700">전압:</span>
                        <span className="font-semibold text-blue-900">{vehicle.gps_data.battery_voltage}V</span>
                      </div>
                    )} */}
                    {/* 최종 업데이트 */}
                    {vehicle.gps_data.last_updated && (
                      <div className="flex justify-between pt-1 border-t border-blue-200">
                        <span className="text-blue-600">업데이트:</span>
                        <span className="text-blue-800 text-sm">
                          {new Date(vehicle.gps_data.last_updated).toLocaleString('ko-KR', {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit',
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit',
                            hour12: false
                          })}
                        </span>
                      </div>
                    )}
                  </div>
                )}
                {!vehicle.gps_data && (
                  <p className="text-xs text-gray-500 italic">GPS 데이터 없음</p>
                )}
              </div>
            )}

            <div className="flex space-x-2 pt-4 border-t">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => openModal(vehicle)}
                className="flex-1"
              >
                <Edit2 size={16} className="mr-1" />
                수정
              </Button>
              <Button
                variant="danger"
                size="sm"
                onClick={() => handleDelete(vehicle.id)}
                className="flex-1"
              >
                <Trash2 size={16} className="mr-1" />
                삭제
              </Button>
            </div>
          </Card>
        ))}
      </div>

      {filteredVehicles.length === 0 && (
        <div className="text-center py-12">
          <Truck size={48} className="mx-auto text-gray-400 mb-4" />
          <p className="text-gray-600">등록된 차량이 없습니다</p>
        </div>
      )}
        </>
      )}

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b">
              <h2 className="text-2xl font-bold text-gray-800">
                {editingVehicle ? '차량 수정' : '차량 등록'}
              </h2>
              <button onClick={() => setModalOpen(false)} className="text-gray-500 hover:text-gray-700">
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="차량코드 *"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                  placeholder="V001"
                  required
                  disabled={!!editingVehicle}
                />

                <Input
                  label="차량번호 *"
                  value={formData.plate_number}
                  onChange={(e) => setFormData({ ...formData, plate_number: e.target.value })}
                  placeholder="00가0000"
                  required
                />

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    차량유형 *
                  </label>
                  <select
                    value={formData.vehicle_type}
                    onChange={(e) => setFormData({ ...formData, vehicle_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="냉동">냉동</option>
                    <option value="냉장">냉장</option>
                    <option value="겸용">겸용</option>
                    <option value="상온">상온</option>
                  </select>
                </div>

                <Input
                  label="톤수 *"
                  type="number"
                  value={formData.tonnage}
                  onChange={(e) => setFormData({ ...formData, tonnage: e.target.value })}
                  step="0.1"
                  min="0"
                  placeholder="5"
                  required
                />

                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <input
                    type="checkbox"
                    id="forklift_operator_available"
                    checked={formData.forklift_operator_available}
                    onChange={(e) => setFormData({ ...formData, forklift_operator_available: e.target.checked })}
                    className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="forklift_operator_available" className="text-sm font-medium text-gray-700 cursor-pointer">
                    지게차 운전능력 (가능/불가능) *
                  </label>
                </div>

                <Input
                  label="적재함 길이(m)"
                  type="number"
                  value={formData.length_m}
                  onChange={(e) => setFormData({ ...formData, length_m: e.target.value })}
                  step="0.1"
                  min="0"
                  placeholder="6.0"
                />

                <Input
                  label="운전자명"
                  value={formData.driver_name}
                  onChange={(e) => setFormData({ ...formData, driver_name: e.target.value })}
                />

                <Input
                  label="연락처"
                  value={formData.driver_phone}
                  onChange={(e) => setFormData({ ...formData, driver_phone: e.target.value })}
                  placeholder="010-0000-0000"
                />

                <Input
                  label="최대 팔레트 수 *"
                  type="number"
                  value={formData.max_pallets}
                  onChange={(e) => setFormData({ ...formData, max_pallets: e.target.value })}
                  min="1"
                  placeholder="20"
                  required
                />

                <Input
                  label="최대 적재중량(kg) *"
                  type="number"
                  value={formData.max_weight_kg}
                  onChange={(e) => setFormData({ ...formData, max_weight_kg: e.target.value })}
                  step="0.01"
                  min="0"
                  placeholder="5000"
                  required
                />

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    상태
                  </label>
                  <select
                    value={formData.status}
                    onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="운행가능">운행가능</option>
                    <option value="운행중">운행중</option>
                    <option value="정비중">정비중</option>
                    <option value="운행불가">운행불가</option>
                  </select>
                </div>

                <Input
                  label="최저 온도(°C)"
                  type="number"
                  value={formData.min_temp_celsius}
                  onChange={(e) => setFormData({ ...formData, min_temp_celsius: e.target.value })}
                  step="0.1"
                  placeholder="-20"
                />

                <Input
                  label="최고 온도(°C)"
                  type="number"
                  value={formData.max_temp_celsius}
                  onChange={(e) => setFormData({ ...formData, max_temp_celsius: e.target.value })}
                  step="0.1"
                  placeholder="-15"
                />

                <Input
                  label="차고지 주소"
                  value={formData.garage_address}
                  onChange={(e) => setFormData({ ...formData, garage_address: e.target.value })}
                  placeholder="서울특별시 강서구"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t">
                <Button type="button" variant="secondary" onClick={() => setModalOpen(false)}>
                  취소
                </Button>
                <Button type="submit" variant="primary">
                  {editingVehicle ? '수정' : '등록'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
      </div>
  );
};

export default VehiclesPage;
