/**
 * Employee Management Page - Full Featured
 * 인사관리 페이지 (전체 기능 + 휴지통)
 */
import React, { useState, useEffect } from 'react';
import { Plus, Search, RefreshCw, Edit, Trash2, Users, Upload, Download, AlertTriangle, X, RotateCcw, Archive } from 'lucide-react';
import toast from 'react-hot-toast';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Card from '../components/common/Card';
import Loading from '../components/common/Loading';
import employeeAPI, { Employee, EmployeeCreate, EmployeeUpdate, EmployeeFilterParams, EmployeeStatistics } from '../api/employees';

// Modal Tab Type
type ModalTab = 'basic' | 'work' | 'qualifications' | 'salary';

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

  // Modal States
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showTrashModal, setShowTrashModal] = useState(false);
  const [currentEmployee, setCurrentEmployee] = useState<Employee | null>(null);
  const [currentTab, setCurrentTab] = useState<ModalTab>('basic');

  // Form State
  const [formData, setFormData] = useState<Partial<EmployeeCreate>>({
    employee_code: '',
    name: '',
    phone: '',
    role: 'DRIVER',
    employment_type: 'FULL_TIME',
    hire_date: new Date().toISOString().split('T')[0],
    work_start_time: '09:00',
    work_end_time: '18:00',
    max_work_hours: 8,
    has_cargo_license: false,
    can_drive_forklift: false,
    has_forklift_certificate: false,
    meal_allowance: 0,
    transportation_allowance: 0,
    hazard_allowance: 0,
    is_active: true,
  });

  // Certificate Expiry Alerts
  const [expiringCertificates, setExpiringCertificates] = useState<Employee[]>([]);

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

      // Check for expiring certificates (within 30 days)
      const expiring = response.items.filter(emp => {
        if (emp.days_until_forklift_expiry !== undefined && emp.days_until_forklift_expiry >= 0 && emp.days_until_forklift_expiry <= 30) {
          return true;
        }
        if (emp.cargo_license_expiry_date) {
          const daysUntilExpiry = Math.ceil((new Date(emp.cargo_license_expiry_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
          return daysUntilExpiry >= 0 && daysUntilExpiry <= 30;
        }
        return false;
      });
      setExpiringCertificates(expiring);
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

  // Show expiry alerts on mount
  useEffect(() => {
    if (expiringCertificates.length > 0) {
      toast.custom((t) => (
        <div className="bg-orange-50 border-l-4 border-orange-500 p-4 rounded shadow-lg max-w-md">
          <div className="flex items-start">
            <AlertTriangle className="text-orange-500 mr-3 mt-0.5" size={20} />
            <div className="flex-1">
              <h4 className="font-bold text-orange-900 mb-2">자격증 만료 임박 ({expiringCertificates.length}명)</h4>
              <ul className="text-sm text-orange-800 space-y-1">
                {expiringCertificates.slice(0, 3).map(emp => (
                  <li key={emp.id}>• {emp.name} ({emp.employee_code})</li>
                ))}
                {expiringCertificates.length > 3 && (
                  <li>• 외 {expiringCertificates.length - 3}명</li>
                )}
              </ul>
            </div>
            <button onClick={() => toast.dismiss(t.id)} className="ml-2">
              <X size={16} />
            </button>
          </div>
        </div>
      ), { duration: 8000 });
    }
  }, [expiringCertificates]);

  // Handle search
  const handleSearch = () => {
    setFilters({ ...filters, page: 1 });
    fetchEmployees();
  };

  // Handle delete
  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`${name}님을 퇴사 처리하시겠습니까?\n\n퇴사 처리된 직원은 휴지통에서 복구할 수 있습니다.`)) return;
    
    try {
      await employeeAPI.delete(id);
      toast.success(`${name}님이 휴지통으로 이동되었습니다`);
      fetchEmployees();
      fetchStatistics();
    } catch (error) {
      console.error('Failed to delete employee:', error);
      toast.error('퇴사 처리 실패');
    }
  };

  // Handle restore
  const handleRestore = async (id: number, name: string) => {
    if (!confirm(`${name}님을 복구하시겠습니까?`)) return;
    
    try {
      await employeeAPI.restore(id);
      toast.success(`${name}님이 복구되었습니다`);
      fetchEmployees();
      fetchStatistics();
    } catch (error) {
      console.error('Failed to restore employee:', error);
      toast.error('복구 실패');
    }
  };

  // Open trash modal
  const openTrashModal = () => {
    setShowTrashModal(true);
  };

  // Open create modal
  const openCreateModal = () => {
    setFormData({
      employee_code: `EMP${Date.now().toString().slice(-6)}`,
      name: '',
      phone: '',
      role: 'DRIVER',
      employment_type: 'FULL_TIME',
      hire_date: new Date().toISOString().split('T')[0],
      work_start_time: '09:00',
      work_end_time: '18:00',
      max_work_hours: 8,
      has_cargo_license: false,
      can_drive_forklift: false,
      has_forklift_certificate: false,
      meal_allowance: 0,
      transportation_allowance: 0,
      hazard_allowance: 0,
      is_active: true,
    });
    setCurrentTab('basic');
    setShowCreateModal(true);
  };

  // Open edit modal
  const openEditModal = (employee: Employee) => {
    setCurrentEmployee(employee);
    setFormData(employee);
    setCurrentTab('basic');
    setShowEditModal(true);
  };

  // Handle create
  const handleCreate = async () => {
    try {
      if (!formData.name || !formData.phone || !formData.employee_code) {
        toast.error('필수 정보를 입력해주세요');
        return;
      }

      await employeeAPI.create(formData as EmployeeCreate);
      toast.success('직원이 등록되었습니다');
      setShowCreateModal(false);
      fetchEmployees();
      fetchStatistics();
    } catch (error: any) {
      console.error('Failed to create employee:', error);
      toast.error(error?.response?.data?.detail || '직원 등록 실패');
    }
  };

  // Handle update
  const handleUpdate = async () => {
    if (!currentEmployee) return;

    try {
      await employeeAPI.update(currentEmployee.id, formData as EmployeeUpdate);
      toast.success('직원 정보가 수정되었습니다');
      setShowEditModal(false);
      fetchEmployees();
      fetchStatistics();
    } catch (error: any) {
      console.error('Failed to update employee:', error);
      toast.error(error?.response?.data?.detail || '직원 정보 수정 실패');
    }
  };

  // Handle Excel Upload
  const handleExcelUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // For now, show placeholder message
    toast.info(`엑셀 업로드 기능은 구현 예정입니다\n파일: ${file.name}`);
    
    // TODO: Implement Excel parsing and bulk upload
    // - Use library like xlsx or papaparse
    // - Parse Excel data
    // - Validate each row
    // - Call employeeAPI.create() for each valid employee
    // - Show progress toast
    // - Display summary (success/failed counts)
  };

  // Handle Excel Download
  const handleExcelDownload = () => {
    // Create CSV data
    const headers = [
      '사번', '이름', '영문명', '전화번호', '이메일', '주소', 
      '직급', '고용형태', '부서', '직책',
      '입사일', '근무시작', '근무종료', '최대근무시간',
      '운전면허', '면허번호', '면허발급일',
      '화물자격증', '화물번호', '화물만료일',
      '지게차운전', '지게차자격증', '지게차번호', '지게차발급일', '지게차만료일',
      '기본급', '식대', '교통비', '위험수당',
      '은행', '계좌번호', '예금주', '비고'
    ];

    const rows = employees.map(emp => [
      emp.employee_code,
      emp.name,
      emp.name_en || '',
      emp.phone,
      emp.email || '',
      emp.address || '',
      emp.role,
      emp.employment_type,
      emp.department || '',
      emp.position || '',
      emp.hire_date,
      emp.work_start_time,
      emp.work_end_time,
      emp.max_work_hours,
      emp.license_type || '',
      emp.license_number || '',
      emp.license_issue_date || '',
      emp.has_cargo_license ? 'Y' : 'N',
      emp.cargo_license_number || '',
      emp.cargo_license_expiry_date || '',
      emp.can_drive_forklift ? 'Y' : 'N',
      emp.has_forklift_certificate ? 'Y' : 'N',
      emp.forklift_certificate_number || '',
      emp.forklift_certificate_issue_date || '',
      emp.forklift_certificate_expiry_date || '',
      emp.base_salary || '',
      emp.meal_allowance,
      emp.transportation_allowance,
      emp.hazard_allowance,
      emp.bank_name || '',
      emp.account_number || '',
      emp.account_holder || '',
      emp.notes || ''
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    // Create download link
    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `직원명단_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();

    toast.success('직원 명단이 다운로드되었습니다');
  };

  // Download Excel Template
  const downloadTemplate = () => {
    const headers = [
      '사번*', '이름*', '영문명', '전화번호*', '이메일', '주소',
      '직급*(MASTER/ADMIN/MANAGER/DRIVER)', '고용형태*(FULL_TIME/CONTRACT/PART_TIME/DAILY)', '부서', '직책',
      '입사일*(YYYY-MM-DD)', '근무시작*(HH:MM)', '근무종료*(HH:MM)', '최대근무시간*',
      '운전면허', '면허번호', '면허발급일(YYYY-MM-DD)',
      '화물자격증(Y/N)', '화물번호', '화물만료일(YYYY-MM-DD)',
      '지게차운전(Y/N)', '지게차자격증(Y/N)', '지게차번호', '지게차발급일(YYYY-MM-DD)', '지게차만료일(YYYY-MM-DD)',
      '기본급', '식대', '교통비', '위험수당',
      '은행', '계좌번호', '예금주', '비고'
    ];

    const sampleRows = [
      ['EMP001', '홍길동', 'Hong Gildong', '010-1234-5678', 'hong@example.com', '서울시 강남구',
       'DRIVER', 'FULL_TIME', '운송팀', '운전사',
       '2024-01-01', '09:00', '18:00', '8',
       '1종 보통', '12-345678-90', '2020-01-01',
       'Y', 'CARGO-123', '2026-12-31',
       'Y', 'Y', 'FORK-456', '2023-01-01', '2026-01-01',
       '3000000', '200000', '100000', '50000',
       '국민은행', '123-456-789012', '홍길동', '우수 운전자'],
      ['EMP002', '김철수', 'Kim Cheolsu', '010-9876-5432', '', '',
       'DRIVER', 'CONTRACT', '운송팀', '운전사',
       '2024-06-01', '08:00', '17:00', '9',
       '1종 대형', '98-765432-10', '2019-06-01',
       'Y', 'CARGO-789', '2027-06-30',
       'N', 'N', '', '', '',
       '2800000', '200000', '100000', '0',
       '신한은행', '987-654-321098', '김철수', '']
    ];

    const csvContent = [
      headers.join(','),
      ...sampleRows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `직원등록_템플릿_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();

    toast.success('등록 템플릿이 다운로드되었습니다');
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

  // Employment Type Label
  const getEmploymentTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      FULL_TIME: '정규직',
      CONTRACT: '계약직',
      PART_TIME: '파트타임',
      DAILY: '일용직',
    };
    return labels[type] || type;
  };

  // Render Modal Content based on current tab
  const renderModalContent = () => {
    switch (currentTab) {
      case 'basic':
        return (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">사번 *</label>
                <Input
                  value={formData.employee_code || ''}
                  onChange={(e) => setFormData({ ...formData, employee_code: e.target.value })}
                  placeholder="EMP001"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">이름 *</label>
                <Input
                  value={formData.name || ''}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="홍길동"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">영문명</label>
                <Input
                  value={formData.name_en || ''}
                  onChange={(e) => setFormData({ ...formData, name_en: e.target.value })}
                  placeholder="Hong Gildong"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">전화번호 *</label>
                <Input
                  value={formData.phone || ''}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  placeholder="010-1234-5678"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">이메일</label>
              <Input
                type="email"
                value={formData.email || ''}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="hong@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">주소</label>
              <Input
                value={formData.address || ''}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                placeholder="서울시 강남구..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">긴급 연락처</label>
              <Input
                value={formData.emergency_contact || ''}
                onChange={(e) => setFormData({ ...formData, emergency_contact: e.target.value })}
                placeholder="010-9876-5432"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">직급 *</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={formData.role || 'DRIVER'}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value as any })}
                >
                  <option value="MASTER">총괄</option>
                  <option value="ADMIN">관리자</option>
                  <option value="MANAGER">현장관리자</option>
                  <option value="DRIVER">운전직</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">고용형태 *</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  value={formData.employment_type || 'FULL_TIME'}
                  onChange={(e) => setFormData({ ...formData, employment_type: e.target.value as any })}
                >
                  <option value="FULL_TIME">정규직</option>
                  <option value="CONTRACT">계약직</option>
                  <option value="PART_TIME">파트타임</option>
                  <option value="DAILY">일용직</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">부서</label>
                <Input
                  value={formData.department || ''}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  placeholder="운송팀"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">직책</label>
                <Input
                  value={formData.position || ''}
                  onChange={(e) => setFormData({ ...formData, position: e.target.value })}
                  placeholder="운전사"
                />
              </div>
            </div>
          </div>
        );

      case 'work':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">입사일 *</label>
              <Input
                type="date"
                value={formData.hire_date || ''}
                onChange={(e) => setFormData({ ...formData, hire_date: e.target.value })}
              />
            </div>

            {!formData.is_active && (
              <div>
                <label className="block text-sm font-medium mb-1">퇴사일</label>
                <Input
                  type="date"
                  value={formData.resignation_date || ''}
                  onChange={(e) => setFormData({ ...formData, resignation_date: e.target.value })}
                />
              </div>
            )}

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">근무 시작 *</label>
                <Input
                  type="time"
                  value={formData.work_start_time || '09:00'}
                  onChange={(e) => setFormData({ ...formData, work_start_time: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">근무 종료 *</label>
                <Input
                  type="time"
                  value={formData.work_end_time || '18:00'}
                  onChange={(e) => setFormData({ ...formData, work_end_time: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">최대 근무시간 *</label>
                <Input
                  type="number"
                  value={formData.max_work_hours || 8}
                  onChange={(e) => setFormData({ ...formData, max_work_hours: parseInt(e.target.value) })}
                />
              </div>
            </div>

            <div className="flex items-center gap-2 p-3 bg-gray-50 rounded">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active !== false}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4"
              />
              <label htmlFor="is_active" className="text-sm font-medium cursor-pointer">
                재직 중
              </label>
            </div>
          </div>
        );

      case 'qualifications':
        return (
          <div className="space-y-4">
            {/* Driver License */}
            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-semibold mb-3">🚗 운전면허</h4>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-1">면허 종류</label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    value={formData.license_type || ''}
                    onChange={(e) => setFormData({ ...formData, license_type: e.target.value })}
                  >
                    <option value="">없음</option>
                    <option value="2종 보통">2종 보통</option>
                    <option value="1종 보통">1종 보통</option>
                    <option value="1종 대형">1종 대형</option>
                    <option value="1종 특수">1종 특수</option>
                  </select>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium mb-1">면허 번호</label>
                    <Input
                      value={formData.license_number || ''}
                      onChange={(e) => setFormData({ ...formData, license_number: e.target.value })}
                      placeholder="12-345678-90"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">발급일</label>
                    <Input
                      type="date"
                      value={formData.license_issue_date || ''}
                      onChange={(e) => setFormData({ ...formData, license_issue_date: e.target.value })}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Cargo License */}
            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-semibold mb-3">📦 화물자격증</h4>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="has_cargo_license"
                    checked={formData.has_cargo_license === true}
                    onChange={(e) => setFormData({ ...formData, has_cargo_license: e.target.checked })}
                    className="w-4 h-4"
                  />
                  <label htmlFor="has_cargo_license" className="text-sm font-medium cursor-pointer">
                    화물자격증 보유
                  </label>
                </div>
                {formData.has_cargo_license && (
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium mb-1">자격증 번호</label>
                      <Input
                        value={formData.cargo_license_number || ''}
                        onChange={(e) => setFormData({ ...formData, cargo_license_number: e.target.value })}
                        placeholder="CARGO-123"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1">만료일</label>
                      <Input
                        type="date"
                        value={formData.cargo_license_expiry_date || ''}
                        onChange={(e) => setFormData({ ...formData, cargo_license_expiry_date: e.target.value })}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Forklift */}
            <div className="p-4 border border-orange-200 bg-orange-50 rounded-lg">
              <h4 className="font-semibold mb-3">🔧 지게차 운전능력</h4>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="can_drive_forklift"
                    checked={formData.can_drive_forklift === true}
                    onChange={(e) => setFormData({ ...formData, can_drive_forklift: e.target.checked })}
                    className="w-4 h-4"
                  />
                  <label htmlFor="can_drive_forklift" className="text-sm font-medium cursor-pointer">
                    지게차 운전 가능
                  </label>
                </div>
                {formData.can_drive_forklift && (
                  <>
                    <div className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        id="has_forklift_certificate"
                        checked={formData.has_forklift_certificate === true}
                        onChange={(e) => setFormData({ ...formData, has_forklift_certificate: e.target.checked })}
                        className="w-4 h-4"
                      />
                      <label htmlFor="has_forklift_certificate" className="text-sm font-medium cursor-pointer">
                        지게차 자격증 보유
                      </label>
                    </div>
                    {formData.has_forklift_certificate && (
                      <div className="space-y-3">
                        <div>
                          <label className="block text-sm font-medium mb-1">자격증 번호</label>
                          <Input
                            value={formData.forklift_certificate_number || ''}
                            onChange={(e) => setFormData({ ...formData, forklift_certificate_number: e.target.value })}
                            placeholder="FORK-456"
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <label className="block text-sm font-medium mb-1">발급일</label>
                            <Input
                              type="date"
                              value={formData.forklift_certificate_issue_date || ''}
                              onChange={(e) => setFormData({ ...formData, forklift_certificate_issue_date: e.target.value })}
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium mb-1">만료일</label>
                            <Input
                              type="date"
                              value={formData.forklift_certificate_expiry_date || ''}
                              onChange={(e) => setFormData({ ...formData, forklift_certificate_expiry_date: e.target.value })}
                            />
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        );

      case 'salary':
        return (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">기본급</label>
              <Input
                type="number"
                value={formData.base_salary || ''}
                onChange={(e) => setFormData({ ...formData, base_salary: parseInt(e.target.value) || undefined })}
                placeholder="3000000"
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">식대</label>
                <Input
                  type="number"
                  value={formData.meal_allowance || 0}
                  onChange={(e) => setFormData({ ...formData, meal_allowance: parseInt(e.target.value) || 0 })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">교통비</label>
                <Input
                  type="number"
                  value={formData.transportation_allowance || 0}
                  onChange={(e) => setFormData({ ...formData, transportation_allowance: parseInt(e.target.value) || 0 })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">위험수당</label>
                <Input
                  type="number"
                  value={formData.hazard_allowance || 0}
                  onChange={(e) => setFormData({ ...formData, hazard_allowance: parseInt(e.target.value) || 0 })}
                />
              </div>
            </div>

            <div className="p-3 bg-blue-50 rounded text-sm">
              <p className="font-semibold mb-1">예상 월급</p>
              <p className="text-2xl font-bold text-blue-600">
                {((formData.base_salary || 0) + (formData.meal_allowance || 0) + (formData.transportation_allowance || 0) + (formData.hazard_allowance || 0)).toLocaleString()}원
              </p>
            </div>

            <div className="border-t pt-4">
              <h4 className="font-semibold mb-3">계좌 정보</h4>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-1">은행명</label>
                  <Input
                    value={formData.bank_name || ''}
                    onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                    placeholder="국민은행"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">계좌번호</label>
                  <Input
                    value={formData.account_number || ''}
                    onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                    placeholder="123-456-789012"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">예금주</label>
                  <Input
                    value={formData.account_holder || ''}
                    onChange={(e) => setFormData({ ...formData, account_holder: e.target.value })}
                    placeholder="홍길동"
                  />
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">비고</label>
              <textarea
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                rows={4}
                value={formData.notes || ''}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                placeholder="기타 특이사항..."
              />
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">인사 관리</h1>
          <p className="text-gray-500 mt-1">직원 정보 조회 및 관리</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={openTrashModal} variant="outline" className="flex items-center gap-2">
            <Archive size={20} />
            휴지통
          </Button>
          <label className="cursor-pointer">
            <input
              type="file"
              accept=".xlsx,.xls,.csv"
              onChange={handleExcelUpload}
              className="hidden"
            />
            <Button variant="outline" className="flex items-center gap-2">
              <Upload size={20} />
              엑셀 업로드
            </Button>
          </label>
          <Button onClick={handleExcelDownload} variant="outline" className="flex items-center gap-2">
            <Download size={20} />
            엑셀 다운로드
          </Button>
          <Button onClick={downloadTemplate} variant="outline" className="flex items-center gap-2">
            <Download size={20} />
            템플릿
          </Button>
          <Button onClick={openCreateModal} className="flex items-center gap-2">
            <Plus size={20} />
            신규 등록
          </Button>
        </div>
      </div>

      {/* Certificate Expiry Alert Banner */}
      {expiringCertificates.length > 0 && (
        <div className="bg-orange-50 border-l-4 border-orange-500 p-4 rounded">
          <div className="flex items-start">
            <AlertTriangle className="text-orange-500 mr-3 mt-0.5" size={20} />
            <div className="flex-1">
              <h4 className="font-bold text-orange-900 mb-2">⚠️ 자격증 만료 임박 ({expiringCertificates.length}명)</h4>
              <p className="text-sm text-orange-800">
                30일 이내에 만료되는 자격증이 있습니다. 갱신이 필요한 직원을 확인해주세요.
              </p>
            </div>
          </div>
        </div>
      )}

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
                          <div className="flex items-center gap-2 mb-2 flex-wrap">
                            <span className={`px-2 py-1 rounded text-xs font-semibold ${getRoleColor(emp.role)}`}>
                              {getRoleLabel(emp.role)}
                            </span>
                            <span className="px-2 py-1 rounded text-xs font-semibold bg-gray-100 text-gray-700">
                              {getEmploymentTypeLabel(emp.employment_type)}
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
                        {emp.department && <p className="flex items-center gap-1">🏢 {emp.department}</p>}
                        {emp.position && <p className="flex items-center gap-1">💼 {emp.position}</p>}
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
                          {emp.days_until_forklift_expiry !== undefined && emp.days_until_forklift_expiry <= 30 && emp.days_until_forklift_expiry >= 0 && (
                            <span className="px-2 py-1 rounded text-xs bg-red-100 text-red-800">
                              ⏰ {emp.days_until_forklift_expiry}일 남음
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="flex gap-2">
                        <Button 
                          size="sm" 
                          variant="outline" 
                          onClick={() => openEditModal(emp)}
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

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] flex flex-col">
            <div className="p-6 border-b flex justify-between items-center">
              <h2 className="text-2xl font-bold">신규 직원 등록</h2>
              <button onClick={() => setShowCreateModal(false)} className="text-gray-500 hover:text-gray-700">
                <X size={24} />
              </button>
            </div>

            {/* Tabs */}
            <div className="flex border-b">
              <button
                className={`px-6 py-3 font-medium ${currentTab === 'basic' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
                onClick={() => setCurrentTab('basic')}
              >
                기본 정보
              </button>
              <button
                className={`px-6 py-3 font-medium ${currentTab === 'work' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
                onClick={() => setCurrentTab('work')}
              >
                근무 정보
              </button>
              <button
                className={`px-6 py-3 font-medium ${currentTab === 'qualifications' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
                onClick={() => setCurrentTab('qualifications')}
              >
                자격증
              </button>
              <button
                className={`px-6 py-3 font-medium ${currentTab === 'salary' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
                onClick={() => setCurrentTab('salary')}
              >
                급여/계좌
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {renderModalContent()}
            </div>

            {/* Modal Actions */}
            <div className="p-6 border-t flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                취소
              </Button>
              <Button onClick={handleCreate}>
                등록
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {showEditModal && currentEmployee && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] flex flex-col">
            <div className="p-6 border-b flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold">직원 정보 수정</h2>
                <p className="text-sm text-gray-500 mt-1">{currentEmployee.name} ({currentEmployee.employee_code})</p>
              </div>
              <button onClick={() => setShowEditModal(false)} className="text-gray-500 hover:text-gray-700">
                <X size={24} />
              </button>
            </div>

            {/* Tabs */}
            <div className="flex border-b">
              <button
                className={`px-6 py-3 font-medium ${currentTab === 'basic' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
                onClick={() => setCurrentTab('basic')}
              >
                기본 정보
              </button>
              <button
                className={`px-6 py-3 font-medium ${currentTab === 'work' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
                onClick={() => setCurrentTab('work')}
              >
                근무 정보
              </button>
              <button
                className={`px-6 py-3 font-medium ${currentTab === 'qualifications' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
                onClick={() => setCurrentTab('qualifications')}
              >
                자격증
              </button>
              <button
                className={`px-6 py-3 font-medium ${currentTab === 'salary' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
                onClick={() => setCurrentTab('salary')}
              >
                급여/계좌
              </button>
            </div>

            {/* Modal Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {renderModalContent()}
            </div>

            {/* Modal Actions */}
            <div className="p-6 border-t flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowEditModal(false)}>
                취소
              </Button>
              <Button onClick={handleUpdate}>
                저장
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Trash Modal (Resigned Employees) */}
      {showTrashModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
            <div className="p-6 border-b flex justify-between items-center">
              <div className="flex items-center gap-3">
                <Archive className="text-gray-600" size={28} />
                <div>
                  <h2 className="text-2xl font-bold">휴지통 (퇴사자)</h2>
                  <p className="text-sm text-gray-500 mt-1">퇴사 처리된 직원 목록 - 복구 가능</p>
                </div>
              </div>
              <button onClick={() => setShowTrashModal(false)} className="text-gray-500 hover:text-gray-700">
                <X size={24} />
              </button>
            </div>

            {/* Trash Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {employees.filter(emp => !emp.is_active).length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                  <Archive size={48} className="mx-auto mb-4 text-gray-400" />
                  <p className="text-lg font-medium">휴지통이 비어있습니다</p>
                  <p className="text-sm mt-2">퇴사 처리된 직원이 없습니다</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {employees.filter(emp => !emp.is_active).map((emp) => (
                    <Card key={emp.id} className="bg-gray-50">
                      <div className="p-4">
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <div className="flex items-center gap-2 mb-2 flex-wrap">
                              <span className={`px-2 py-1 rounded text-xs font-semibold ${getRoleColor(emp.role)}`}>
                                {getRoleLabel(emp.role)}
                              </span>
                              <span className="px-2 py-1 rounded text-xs font-semibold bg-gray-100 text-gray-700">
                                {getEmploymentTypeLabel(emp.employment_type)}
                              </span>
                              <span className="px-2 py-1 rounded text-xs font-semibold bg-red-100 text-red-800">
                                퇴사
                              </span>
                            </div>
                            <h3 className="text-lg font-bold text-gray-900">{emp.name}</h3>
                            <p className="text-sm text-gray-500">{emp.employee_code}</p>
                          </div>
                        </div>
                        
                        <div className="space-y-1 text-sm mb-4 text-gray-600">
                          <p className="flex items-center gap-1">📞 {emp.phone}</p>
                          {emp.department && <p className="flex items-center gap-1">🏢 {emp.department}</p>}
                          {emp.resignation_date && (
                            <p className="flex items-center gap-1 text-red-600">
                              📅 퇴사일: {emp.resignation_date}
                            </p>
                          )}
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
                            onClick={() => handleRestore(emp.id, emp.name)}
                            className="flex-1 flex items-center justify-center gap-1"
                          >
                            <RotateCcw size={16} />
                            복구
                          </Button>
                          <Button 
                            size="sm" 
                            variant="outline" 
                            onClick={() => openEditModal(emp)}
                            className="flex-1 flex items-center justify-center gap-1"
                          >
                            <Edit size={16} />
                            보기
                          </Button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>

            {/* Modal Actions */}
            <div className="p-6 border-t flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowTrashModal(false)}>
                닫기
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmployeeManagementPage;
