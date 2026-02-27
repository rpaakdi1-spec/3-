import React, { useState, useEffect } from 'react';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { Users, Truck, Phone, Clock, AlertCircle, Search, RefreshCw } from 'lucide-react';
import { toast } from 'react-hot-toast';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Loading from '../components/common/Loading';
import { vehiclesAPI } from '../services/api';

const ItemTypes = {
  DRIVER: 'driver'
};

interface Driver {
  id: number;
  code: string;
  name: string;
  phone: string;
  emergency_contact?: string;
  work_start_time: string;
  work_end_time: string;
  max_work_hours: number;
  license_number?: string;
  license_type?: string;
  notes?: string;
  is_active: boolean;
  assigned_vehicle_id?: number;
}

interface Vehicle {
  id: number;
  code: string;
  plate_number: string;
  vehicle_type: string;
  tonnage: number;
  status: string;
  driver_name?: string;
  driver_phone?: string;
  assigned_driver?: Driver;
}

const VehicleDriverManagementPage: React.FC = () => {
  const [drivers, setDrivers] = useState<Driver[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [licenseFilter, setLicenseFilter] = useState<string>('all');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch vehicles
      const vehiclesResponse = await vehiclesAPI.list();
      const vehiclesList = vehiclesResponse.data.items || [];
      
      // TODO: Fetch drivers from API endpoint
      // For now, using mock data - replace with actual API call
      const mockDrivers: Driver[] = [
        {
          id: 1,
          code: 'D001',
          name: '김철수',
          phone: '010-1234-5678',
          emergency_contact: '010-9876-5432',
          work_start_time: '08:00',
          work_end_time: '18:00',
          max_work_hours: 10,
          license_number: '서울12-345678-90',
          license_type: '1종 대형',
          is_active: true
        },
        {
          id: 2,
          code: 'D002',
          name: '이영희',
          phone: '010-2345-6789',
          work_start_time: '09:00',
          work_end_time: '19:00',
          max_work_hours: 10,
          license_type: '1종 보통',
          is_active: true
        },
        {
          id: 3,
          code: 'D003',
          name: '박민수',
          phone: '010-3456-7890',
          work_start_time: '07:00',
          work_end_time: '17:00',
          max_work_hours: 10,
          license_type: '1종 대형',
          is_active: true
        },
        {
          id: 4,
          code: 'D004',
          name: '정수진',
          phone: '010-4567-8901',
          work_start_time: '08:30',
          work_end_time: '18:30',
          max_work_hours: 10,
          license_type: '1종 보통',
          is_active: true
        },
        {
          id: 5,
          code: 'D005',
          name: '최동욱',
          phone: '010-5678-9012',
          work_start_time: '06:00',
          work_end_time: '16:00',
          max_work_hours: 10,
          license_type: '1종 대형',
          is_active: true
        }
      ];
      
      // Match drivers with vehicles based on driver_name or driver_phone
      const vehiclesWithDrivers = vehiclesList.map((vehicle: Vehicle) => {
        const assignedDriver = mockDrivers.find(d => 
          d.name === vehicle.driver_name || 
          d.phone === vehicle.driver_phone
        );
        return {
          ...vehicle,
          assigned_driver: assignedDriver
        };
      });
      
      // Mark drivers as assigned
      const driversWithAssignment = mockDrivers.map(driver => ({
        ...driver,
        assigned_vehicle_id: vehiclesWithDrivers.find(v => v.assigned_driver?.id === driver.id)?.id
      }));
      
      setVehicles(vehiclesWithDrivers);
      setDrivers(driversWithAssignment);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      toast.error('데이터 로드에 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleDropDriver = async (vehicleId: number | null, driver: Driver, sourceVehicleId?: number) => {
    try {
      if (vehicleId === null) {
        // Unassign driver - find current vehicle
        const currentVehicle = vehicles.find(v => v.assigned_driver?.id === driver.id);
        if (currentVehicle) {
          await vehiclesAPI.update(currentVehicle.id, {
            driver_name: null,
            driver_phone: null
          });
          toast.success(`${driver.name}님의 배정이 해제되었습니다`);
        }
      } else {
        // When moving from vehicle to vehicle, unassign from source first
        if (sourceVehicleId) {
          await vehiclesAPI.update(sourceVehicleId, {
            driver_name: null,
            driver_phone: null
          });
        }
        
        // Then assign to new vehicle
        await vehiclesAPI.update(vehicleId, {
          driver_name: driver.name,
          driver_phone: driver.phone
        });
        
        if (sourceVehicleId) {
          toast.success(`${driver.name}님이 다른 차량으로 이동되었습니다`);
        } else {
          toast.success(`${driver.name}님이 차량에 배정되었습니다`);
        }
      }
      
      // Refresh data
      await fetchData();
    } catch (error) {
      console.error('Failed to update assignment:', error);
      toast.error('배정 변경에 실패했습니다');
    }
  };

  const unassignedDrivers = drivers.filter(d => !d.assigned_vehicle_id && d.is_active);
  
  // Apply filters
  const filteredVehicles = vehicles.filter(vehicle => {
    // Search filter
    const matchesSearch = vehicle.plate_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vehicle.driver_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      vehicle.vehicle_type?.toLowerCase().includes(searchTerm.toLowerCase());
    
    // Status filter
    const matchesStatus = statusFilter === 'all' || vehicle.status === statusFilter;
    
    // Type filter
    const matchesType = typeFilter === 'all' || vehicle.vehicle_type === typeFilter;
    
    // License filter (for assigned drivers)
    const matchesLicense = licenseFilter === 'all' || 
      (vehicle.assigned_driver?.license_type?.includes(licenseFilter));
    
    return matchesSearch && matchesStatus && matchesType && matchesLicense;
  });

  if (loading) return <Loading />;

  return (
    <DndProvider backend={HTML5Backend}>
      <div className="p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-800">차량-운전자 배정 관리</h1>
          <p className="text-gray-600 mt-1">드래그 앤 드롭으로 운전자를 차량에 배정하거나 해제하세요</p>
        </div>

        {/* Search and Filters */}
        <Card className="mb-6">
          <div className="space-y-4">
            {/* Search Bar */}
            <div className="flex items-center gap-4">
              <Search size={20} className="text-gray-400" />
              <Input
                placeholder="차량번호, 운전자명, 차량유형으로 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="flex-1"
              />
              <Button
                onClick={fetchData}
                variant="outline"
                size="sm"
              >
                <RefreshCw size={18} className="mr-2" />
                새로고침
              </Button>
            </div>
            
            {/* Filters */}
            <div className="flex flex-wrap gap-3">
              {/* Status Filter */}
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700">상태:</label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">전체</option>
                  <option value="운행가능">운행가능</option>
                  <option value="운행중">운행중</option>
                  <option value="정비중">정비중</option>
                  <option value="운행불가">운행불가</option>
                </select>
              </div>
              
              {/* Type Filter */}
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700">차량유형:</label>
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">전체</option>
                  <option value="냉동">냉동</option>
                  <option value="냉장">냉장</option>
                  <option value="겸용">겸용</option>
                  <option value="상온">상온</option>
                </select>
              </div>
              
              {/* License Filter */}
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium text-gray-700">운전자 면허:</label>
                <select
                  value={licenseFilter}
                  onChange={(e) => setLicenseFilter(e.target.value)}
                  className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">전체</option>
                  <option value="1종 대형">1종 대형</option>
                  <option value="1종 보통">1종 보통</option>
                  <option value="2종">2종</option>
                </select>
              </div>
              
              {/* Clear Filters */}
              {(statusFilter !== 'all' || typeFilter !== 'all' || licenseFilter !== 'all' || searchTerm) && (
                <Button
                  onClick={() => {
                    setStatusFilter('all');
                    setTypeFilter('all');
                    setLicenseFilter('all');
                    setSearchTerm('');
                  }}
                  variant="ghost"
                  size="sm"
                  className="ml-auto"
                >
                  필터 초기화
                </Button>
              )}
            </div>
          </div>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Driver Pool - Left Side */}
          <div className="lg:col-span-1">
            <Card className="sticky top-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Users className="text-blue-600" size={24} />
                  <h2 className="text-xl font-bold text-gray-800">운전자 풀</h2>
                </div>
                <span className="text-sm text-gray-500 font-semibold bg-blue-100 px-3 py-1 rounded-full">
                  {unassignedDrivers.length}명
                </span>
              </div>

              <DriverPool 
                drivers={unassignedDrivers} 
                onDropDriver={handleDropDriver}
              />
            </Card>
          </div>

          {/* Vehicle List - Right Side */}
          <div className="lg:col-span-2">
            <div className="space-y-4">
              {filteredVehicles.length === 0 ? (
                <Card>
                  <div className="text-center py-12">
                    <Truck size={48} className="mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">차량이 없습니다</p>
                  </div>
                </Card>
              ) : (
                filteredVehicles.map((vehicle) => (
                  <VehicleCard
                    key={vehicle.id}
                    vehicle={vehicle}
                    onDropDriver={handleDropDriver}
                  />
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </DndProvider>
  );
};

// Driver Pool Component with Drop Zone
interface DriverPoolProps {
  drivers: Driver[];
  onDropDriver: (vehicleId: number | null, driver: Driver, sourceVehicleId?: number) => void;
}

const DriverPool: React.FC<DriverPoolProps> = ({ drivers, onDropDriver }) => {
  const [{ isOver }, drop] = useDrop(() => ({
    accept: ItemTypes.DRIVER,
    drop: (item: { driver: Driver; sourceType: string; vehicleId?: number }) => {
      if (item.sourceType === 'vehicle') {
        onDropDriver(null, item.driver, item.vehicleId);
      }
    },
    collect: (monitor) => ({
      isOver: !!monitor.isOver()
    })
  }));

  return (
    <div
      ref={drop}
      className={`min-h-[400px] max-h-[600px] overflow-y-auto space-y-3 p-4 rounded-lg border-2 border-dashed transition-all ${
        isOver 
          ? 'border-red-400 bg-red-50 scale-[1.02]' 
          : 'border-gray-300 bg-gray-50'
      }`}
    >
      {drivers.length === 0 ? (
        <div className="text-center py-12">
          <Users size={48} className="mx-auto text-gray-300 mb-4" />
          <p className="text-gray-500">배정 가능한 운전자가 없습니다</p>
          <p className="text-sm text-gray-400 mt-2">모든 운전자가 차량에 배정되었습니다</p>
        </div>
      ) : (
        <>
          {drivers.map((driver) => (
            <DriverCard
              key={driver.id}
              driver={driver}
              sourceType="pool"
            />
          ))}
          {isOver && (
            <div className="absolute top-2 right-2 bg-red-100 border border-red-300 rounded-lg p-2">
              <p className="text-xs text-red-700 flex items-center gap-1">
                <AlertCircle size={14} />
                배정 해제됩니다
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
};

// Driver Card Component (Draggable)
interface DriverCardProps {
  driver: Driver;
  sourceType: 'pool' | 'vehicle';
  vehicleId?: number;
}

const DriverCard: React.FC<DriverCardProps> = ({ driver, sourceType, vehicleId }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: ItemTypes.DRIVER,
    item: { driver, sourceType, vehicleId },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging()
    })
  }));

  return (
    <div
      ref={drag}
      className={`bg-white border rounded-lg p-4 cursor-move transition-all hover:shadow-md hover:border-blue-400 ${
        isDragging ? 'opacity-50 scale-95' : 'opacity-100'
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <div>
          <h3 className="font-bold text-gray-800">{driver.name}</h3>
          <p className="text-xs text-gray-500">{driver.code}</p>
        </div>
        <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full font-medium">
          {driver.license_type || '면허정보없음'}
        </span>
      </div>
      
      <div className="space-y-1 text-sm">
        <div className="flex items-center gap-2 text-gray-600">
          <Phone size={14} />
          <span>{driver.phone}</span>
        </div>
        <div className="flex items-center gap-2 text-gray-600">
          <Clock size={14} />
          <span>{driver.work_start_time} ~ {driver.work_end_time}</span>
        </div>
      </div>
    </div>
  );
};

// Vehicle Card Component (Drop Target)
interface VehicleCardProps {
  vehicle: Vehicle;
  onDropDriver: (vehicleId: number | null, driver: Driver, sourceVehicleId?: number) => void;
}

const VehicleCard: React.FC<VehicleCardProps> = ({ vehicle, onDropDriver }) => {
  const [{ isOver }, drop] = useDrop(() => ({
    accept: ItemTypes.DRIVER,
    drop: (item: { driver: Driver; sourceType: string; vehicleId?: number }) => {
      // Prevent dropping driver on same vehicle
      if (item.vehicleId !== vehicle.id) {
        // Pass sourceVehicleId to properly handle the move operation
        onDropDriver(vehicle.id, item.driver, item.vehicleId);
      }
    },
    collect: (monitor) => ({
      isOver: !!monitor.isOver()
    })
  }));

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      '운행가능': 'bg-green-100 text-green-800',
      '운행중': 'bg-blue-100 text-blue-800',
      '정비중': 'bg-yellow-100 text-yellow-800',
      '운행불가': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  return (
    <Card
      className={`transition-all ${
        isOver ? 'ring-4 ring-blue-400 bg-blue-50 shadow-lg scale-[1.02]' : ''
      }`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <Truck className="text-blue-600" size={24} />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-800">{vehicle.plate_number}</h3>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <span>{vehicle.vehicle_type}</span>
              <span>•</span>
              <span>{vehicle.tonnage}톤</span>
            </div>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(vehicle.status)}`}>
          {vehicle.status}
        </span>
      </div>

      {/* Driver Assignment Area */}
      <div
        ref={drop}
        className={`p-4 rounded-lg border-2 transition-all min-h-[140px] ${
          vehicle.assigned_driver 
            ? 'border-green-300 bg-green-50' 
            : isOver
              ? 'border-blue-400 bg-blue-100 animate-pulse'
              : 'border-dashed border-gray-300 bg-gray-50'
        }`}
      >
        {vehicle.assigned_driver ? (
          <DriverCard
            driver={vehicle.assigned_driver}
            sourceType="vehicle"
            vehicleId={vehicle.id}
          />
        ) : (
          <div className="text-center py-6">
            <Users size={32} className="mx-auto text-gray-300 mb-2" />
            <p className="text-sm text-gray-500 font-medium">
              {isOver ? '✓ 여기에 놓으세요' : '배정된 운전자가 없습니다'}
            </p>
            <p className="text-xs text-gray-400 mt-1">
              {isOver ? '배정이 완료됩니다' : '운전자를 드래그하여 배정하세요'}
            </p>
          </div>
        )}
      </div>
    </Card>
  );
};

export default VehicleDriverManagementPage;
