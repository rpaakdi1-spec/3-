/**
 * Employee Management Page (Simplified)
 * 인사관리 페이지
 */
import React, { useState, useEffect } from 'react';
import { Plus, Search, RefreshCw, Edit, Trash2, Users, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
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

  // Role badge color
  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'MASTER': return 'bg-purple-500';
      case 'ADMIN': return 'bg-blue-500';
      case 'MANAGER': return 'bg-green-500';
      case 'DRIVER': return 'bg-gray-500';
      default: return 'bg-gray-400';
    }
  };

  // Role label
  const getRoleLabel = (role: string) => {
    const labels = {
      MASTER: '총괄',
      ADMIN: '관리자',
      MANAGER: '현장관리자',
      DRIVER: '운전직',
    };
    return labels[role as keyof typeof labels] || role;
  };

  // Forklift status badge
  const getForkliftBadge = (employee: Employee) => {
    if (!employee.can_drive_forklift) return null;
    
    const hasCert = employee.has_forklift_certificate;
    return (
      <Badge variant={hasCert ? 'default' : 'warning'} className="ml-2">
        🔧 지게차 {hasCert ? '✅' : '⚠️'}
      </Badge>
    );
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">인사 관리</h1>
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
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">전체 직원</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.total_employees}명</div>
              <p className="text-xs text-gray-500 mt-1">재직 {statistics.active_employees}명</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">운전직</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.by_role?.DRIVER || 0}명</div>
              <p className="text-xs text-gray-500 mt-1">화물자격증 {statistics.drivers_with_cargo_license}명</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">지게차 가능</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.drivers_with_forklift_ability}명</div>
              <p className="text-xs text-gray-500 mt-1">자격증 {statistics.drivers_with_forklift_certificate}명</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">교육 필요</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-500">{statistics.drivers_needing_training}명</div>
              <p className="text-xs text-gray-500 mt-1">지게차 교육 대상</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Search & Filters */}
      <Card>
        <CardContent className="pt-6">
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
            <Select value={filters.role || 'all'} onValueChange={(v) => setFilters({ ...filters, role: v === 'all' ? undefined : v, page: 1 })}>
              <SelectTrigger>
                <SelectValue placeholder="직급" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체 직급</SelectItem>
                <SelectItem value="MASTER">총괄</SelectItem>
                <SelectItem value="ADMIN">관리자</SelectItem>
                <SelectItem value="MANAGER">현장관리자</SelectItem>
                <SelectItem value="DRIVER">운전직</SelectItem>
              </SelectContent>
            </Select>

            {/* Active Filter */}
            <Select value={filters.is_active === undefined ? 'all' : filters.is_active.toString()} onValueChange={(v) => setFilters({ ...filters, is_active: v === 'all' ? undefined : v === 'true', page: 1 })}>
              <SelectTrigger>
                <SelectValue placeholder="재직 상태" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">전체</SelectItem>
                <SelectItem value="true">재직</SelectItem>
                <SelectItem value="false">퇴사</SelectItem>
              </SelectContent>
            </Select>

            {/* Refresh */}
            <Button onClick={() => { fetchEmployees(); fetchStatistics(); }} variant="outline">
              <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Employee List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users size={20} />
            직원 목록 ({total}명)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="animate-spin" size={40} />
            </div>
          ) : employees.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              검색 결과가 없습니다
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {employees.map((emp) => (
                <Card key={emp.id} className={!emp.is_active ? 'opacity-60' : ''}>
                  <CardContent className="pt-6">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <div className="flex items-center gap-2">
                          <Badge className={getRoleBadgeColor(emp.role)}>
                            {getRoleLabel(emp.role)}
                          </Badge>
                          {!emp.is_active && <Badge variant="destructive">퇴사</Badge>}
                        </div>
                        <h3 className="text-lg font-bold mt-2">{emp.name}</h3>
                        <p className="text-sm text-gray-500">{emp.employee_code}</p>
                      </div>
                    </div>
                    
                    <div className="space-y-1 text-sm">
                      <p>📞 {emp.phone}</p>
                      {emp.license_type && <p>🚗 {emp.license_type}</p>}
                      {emp.has_cargo_license && <Badge variant="secondary">화물자격증 ✓</Badge>}
                      {getForkliftBadge(emp)}
                    </div>

                    <div className="mt-4 flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => toast.info('상세 보기 기능은 곧 추가됩니다')}>
                        <Edit size={16} className="mr-1" />
                        수정
                      </Button>
                      <Button size="sm" variant="destructive" onClick={() => handleDelete(emp.id, emp.name)}>
                        <Trash2 size={16} className="mr-1" />
                        퇴사
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

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
        </CardContent>
      </Card>
    </div>
  );
};

export default EmployeeManagementPage;
