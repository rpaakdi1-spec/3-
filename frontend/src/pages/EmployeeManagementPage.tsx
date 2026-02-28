/**
 * Employee Management Page (Simplified - No UI Library)
 * 인사관리 페이지
 */
import React, { useState, useEffect } from 'react';
import { Plus, Search, RefreshCw, Edit, Trash2, Users } from 'lucide-react';
import toast from 'react-hot-toast';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Card from '../components/common/Card';
import Loading from '../components/common/Loading';
import employeeAPI, { Employee, EmployeeFilterParams, EmployeeStatistics } from '../api/employees';

const EmployeeManagementPage: React.FC = () => {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [statistics, setStatistics] = useState<EmployeeStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<EmployeeFilterParams>({
    page: 1,
    page_size: 20,
  });
  const [total, setTotal] = useState(0);

  // Fetch employees
  const fetchEmployees = async () => {
    setLoading(true);
    try {
      const response = await employeeAPI.list({
        ...filters,
        search: searchTerm || undefined,
      });
      setEmployees(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to fetch employees:', error);
      toast.error('직원 목록 조회 실패');
    } finally {
      setLoading(false);
    }
  };

  // Fetch statistics
  const fetchStatistics = async () => {
    try {
      const stats = await employeeAPI.getStatistics();
      setStatistics(stats);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  };

  useEffect(() => {
    fetchEmployees();
    fetchStatistics();
  }, [filters]);

  // Handle search
  const handleSearch = () => {
    setFilters({ ...filters, page: 1 });
    fetchEmployees();
  };

  // Handle delete
  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`${name}님을 퇴사 처리하시겠습니까?`)) return;
    
    try {
      await employeeAPI.delete(id);
      toast.success('퇴사 처리되었습니다');
      fetchEmployees();
      fetchStatistics();
    } catch (error) {
      console.error('Failed to delete employee:', error);
      toast.error('퇴사 처리 실패');
    }
  };

  // Role label
  const getRoleLabel = (role: string) => {
    const labels: Record<string, string> = {
      MASTER: '총괄',
      ADMIN: '관리자',
      MANAGER: '현장관리자',
      DRIVER: '운전직',
    };
    return labels[role] || role;
  };

  // Role color
  const getRoleColor = (role: string) => {
    const colors: Record<string, string> = {
      MASTER: 'bg-purple-100 text-purple-800',
      ADMIN: 'bg-blue-100 text-blue-800',
      MANAGER: 'bg-green-100 text-green-800',
      DRIVER: 'bg-gray-100 text-gray-800',
    };
    return colors[role] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">인사 관리</h1>
          <p className="text-gray-500 mt-1">직원 정보 조회 및 관리</p>
        </div>
        <Button onClick={() => toast.info('신규 등록 기능은 곧 추가됩니다')} className="flex items-center gap-2">
          <Plus size={20} />
          신규 등록
        </Button>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <div className="p-4">
              <p className="text-sm font-medium text-gray-600 mb-2">전체 직원</p>
              <p className="text-3xl font-bold text-gray-900">{statistics.total_employees}명</p>
              <p className="text-xs text-gray-500 mt-1">재직 {statistics.active_employees}명</p>
            </div>
          </Card>
          <Card>
            <div className="p-4">
              <p className="text-sm font-medium text-gray-600 mb-2">운전직</p>
              <p className="text-3xl font-bold text-gray-900">{statistics.by_role?.DRIVER || 0}명</p>
              <p className="text-xs text-gray-500 mt-1">화물자격증 {statistics.drivers_with_cargo_license}명</p>
            </div>
          </Card>
          <Card>
            <div className="p-4">
              <p className="text-sm font-medium text-gray-600 mb-2">지게차 가능</p>
              <p className="text-3xl font-bold text-gray-900">{statistics.drivers_with_forklift_ability}명</p>
              <p className="text-xs text-gray-500 mt-1">자격증 {statistics.drivers_with_forklift_certificate}명</p>
            </div>
          </Card>
          <Card>
            <div className="p-4">
              <p className="text-sm font-medium text-gray-600 mb-2">교육 필요</p>
              <p className="text-3xl font-bold text-orange-600">{statistics.drivers_needing_training}명</p>
              <p className="text-xs text-gray-500 mt-1">지게차 교육 대상</p>
            </div>
          </Card>
        </div>
      )}

      {/* Search & Filters */}
      <Card>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {/* Search */}
            <div className="md:col-span-2 flex gap-2">
              <Input
                placeholder="이름, 사번, 전화번호 검색..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button onClick={handleSearch} variant="outline">
                <Search size={20} />
              </Button>
            </div>

            {/* Role Filter */}
            <select 
              className="px-3 py-2 border border-gray-300 rounded-md"
              value={filters.role || 'all'}
              onChange={(e) => setFilters({ ...filters, role: e.target.value === 'all' ? undefined : e.target.value, page: 1 })}
            >
              <option value="all">전체 직급</option>
              <option value="MASTER">총괄</option>
              <option value="ADMIN">관리자</option>
              <option value="MANAGER">현장관리자</option>
              <option value="DRIVER">운전직</option>
            </select>

            {/* Active Filter */}
            <select 
              className="px-3 py-2 border border-gray-300 rounded-md"
              value={filters.is_active === undefined ? 'all' : filters.is_active.toString()}
              onChange={(e) => setFilters({ ...filters, is_active: e.target.value === 'all' ? undefined : e.target.value === 'true', page: 1 })}
            >
              <option value="all">전체</option>
              <option value="true">재직</option>
              <option value="false">퇴사</option>
            </select>

            {/* Refresh */}
            <Button onClick={() => { fetchEmployees(); fetchStatistics(); }} variant="outline">
              <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
            </Button>
          </div>
        </div>
      </Card>

      {/* Employee List */}
      <Card>
        <div className="p-6">
          <div className="flex items-center gap-2 mb-4">
            <Users size={20} />
            <h2 className="text-xl font-bold">직원 목록 ({total}명)</h2>
          </div>

          {loading ? (
            <Loading />
          ) : employees.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              검색 결과가 없습니다
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {employees.map((emp) => (
                  <Card key={emp.id} className={!emp.is_active ? 'opacity-60' : ''}>
                    <div className="p-4">
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <div className="flex items-center gap-2 mb-2">
                            <span className={`px-2 py-1 rounded text-xs font-semibold ${getRoleColor(emp.role)}`}>
                              {getRoleLabel(emp.role)}
                            </span>
                            {!emp.is_active && (
                              <span className="px-2 py-1 rounded text-xs font-semibold bg-red-100 text-red-800">
                                퇴사
                              </span>
                            )}
                          </div>
                          <h3 className="text-lg font-bold">{emp.name}</h3>
                          <p className="text-sm text-gray-500">{emp.employee_code}</p>
                        </div>
                      </div>
                      
                      <div className="space-y-1 text-sm mb-4">
                        <p className="flex items-center gap-1">📞 {emp.phone}</p>
                        {emp.license_type && <p className="flex items-center gap-1">🚗 {emp.license_type}</p>}
                        <div className="flex gap-2 flex-wrap mt-2">
                          {emp.has_cargo_license && (
                            <span className="px-2 py-1 rounded text-xs bg-blue-100 text-blue-800">화물자격증 ✓</span>
                          )}
                          {emp.can_drive_forklift && (
                            <span className={`px-2 py-1 rounded text-xs ${emp.has_forklift_certificate ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800'}`}>
                              🔧 지게차 {emp.has_forklift_certificate ? '✅' : '⚠️'}
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button 
                          size="sm" 
                          variant="outline" 
                          onClick={() => toast.info('상세 보기 기능은 곧 추가됩니다')}
                          className="flex-1"
                        >
                          <Edit size={16} className="mr-1" />
                          수정
                        </Button>
                        <Button 
                          size="sm" 
                          variant="danger" 
                          onClick={() => handleDelete(emp.id, emp.name)}
                          className="flex-1"
                        >
                          <Trash2 size={16} className="mr-1" />
                          퇴사
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>

              {/* Pagination */}
              {total > (filters.page_size || 20) && (
                <div className="flex justify-center gap-2 mt-6">
                  <Button
                    variant="outline"
                    onClick={() => setFilters({ ...filters, page: (filters.page || 1) - 1 })}
                    disabled={filters.page === 1}
                  >
                    이전
                  </Button>
                  <span className="py-2 px-4">
                    {filters.page} / {Math.ceil(total / (filters.page_size || 20))}
                  </span>
                  <Button
                    variant="outline"
                    onClick={() => setFilters({ ...filters, page: (filters.page || 1) + 1 })}
                    disabled={filters.page === Math.ceil(total / (filters.page_size || 20))}
                  >
                    다음
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </Card>
    </div>
  );
};

export default EmployeeManagementPage;
