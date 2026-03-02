import React, { useState, useEffect } from 'react';
import { UserPlus, Search, Edit2, Trash2, Eye, EyeOff } from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';
import Input from '../common/Input';
import api from '../../api/client';
import { toast } from 'react-hot-toast';

interface UserAccount {
  id: number;
  username: string;
  email: string;
  full_name: string;
  phone?: string;
  role: string;
  is_active: boolean;
  approval_status?: string;
  employee_id?: number;
  
  // 기본 인적사항 (전체 필드)
  name_en?: string;
  address?: string;
  emergency_contact?: string;
  
  // 조직 정보
  employment_type?: string;
  department?: string;
  position?: string;
  
  // 근무 정보
  hire_date?: string;
  
  // 운전면허
  license_type?: string;
  license_number?: string;
  license_issue_date?: string;
  
  // 화물운송자격증
  has_cargo_license?: boolean;
  cargo_license_number?: string;
  cargo_license_issue_date?: string;
  cargo_license_expiry_date?: string;
  
  // 지게차 자격
  can_drive_forklift?: boolean;
  has_forklift_certificate?: boolean;
  forklift_certificate_number?: string;
  forklift_certificate_issue_date?: string;
  forklift_certificate_expiry_date?: string;
  
  employee?: {
    employee_code: string;
    name: string;
    phone: string;
    department?: string;
    position?: string;
  };
  pending_employee?: {
    employee_code: string;
    name: string;
    name_en?: string;
    phone: string;
    email?: string;
    address?: string;
    emergency_contact?: string;
    role: string;
    employment_type: string;
    department?: string;
    position?: string;
    hire_date: string;
    license_type?: string;
    license_number?: string;
    license_issue_date?: string;
    has_cargo_license: boolean;
    cargo_license_number?: string;
    cargo_license_issue_date?: string;
    cargo_license_expiry_date?: string;
    can_drive_forklift: boolean;
    has_forklift_certificate: boolean;
    forklift_certificate_number?: string;
    forklift_certificate_issue_date?: string;
    forklift_certificate_expiry_date?: string;
  };
  created_at: string;
}

interface NewUserForm {
  username: string;
  email: string;
  password: string;
  full_name: string;
  role: string;
  employee_id?: number;
  
  // 인사카드 정보 (신규 직원 생성 시)
  createEmployee: boolean;
  employee: {
    employee_code: string;
    name: string;
    phone: string;
    email?: string;
    address?: string;
    emergency_contact?: string;
    role: string;
    employment_type: string;
    department?: string;
    position?: string;
    hire_date: string;
    license_type?: string;
    license_number?: string;
    license_issue_date?: string;
    has_cargo_license: boolean;
    cargo_license_number?: string;
    can_drive_forklift: boolean;
    has_forklift_certificate: boolean;
  };
}

const UserManagementTab: React.FC = () => {
  const [users, setUsers] = useState<UserAccount[]>([]);
  const [pendingUsers, setPendingUsers] = useState<UserAccount[]>([]);
  const [activeTab, setActiveTab] = useState<'users' | 'pending'>('users');
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showNewUserModal, setShowNewUserModal] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editStep, setEditStep] = useState(1);
  const [editingUser, setEditingUser] = useState<UserAccount | null>(null);

  const [newUser, setNewUser] = useState<NewUserForm>({
    username: '',
    email: '',
    password: '',
    full_name: '',
    role: 'driver',
    createEmployee: true,
    employee: {
      employee_code: '',
      name: '',
      phone: '',
      email: '',
      role: 'DRIVER',
      employment_type: 'FULL_TIME',
      hire_date: new Date().toISOString().split('T')[0],
      has_cargo_license: false,
      can_drive_forklift: false,
      has_forklift_certificate: false,
    }
  });

  useEffect(() => {
    loadUsers();
    loadPendingUsers();
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      // 활성 사용자만 조회 (approval_status='approved')
      const response = await api.get('/auth/users?show_inactive=false');
      setUsers(response.data.items || response.data);
    } catch (error) {
      console.error('Failed to load users:', error);
      toast.error('사용자 목록 조회에 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const loadPendingUsers = async () => {
    try {
      const response = await api.get('/auth/users/pending');
      setPendingUsers(response.data.items || response.data);
    } catch (error) {
      console.error('Failed to load pending users:', error);
    }
  };

  const handleApproveUser = async (userId: number, username: string) => {
    if (!confirm(`${username}님을 승인하시겠습니까?`)) return;
    
    try {
      setLoading(true);
      // Backend doesn't need employee_code in request body - it gets it from PendingEmployee
      await api.post(`/auth/users/${userId}/approve`);
      toast.success(`${username}님이 승인되었습니다`);
      loadUsers();
      loadPendingUsers();
    } catch (error: any) {
      console.error('Failed to approve user:', error);
      const errorMsg = error.response?.data?.detail || '승인에 실패했습니다';
      console.error('Approval error details:', errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    if (!newUser.username || !newUser.password || !newUser.full_name) {
      toast.error('필수 정보를 입력해주세요 (아이디, 비밀번호, 이름)');
      return;
    }

    if (newUser.createEmployee && !newUser.employee.phone) {
      toast.error('전화번호를 입력해주세요');
      return;
    }

    setLoading(true);
    try {
      // Map frontend role to backend UserRole
      const roleMap: {[key: string]: string} = {
        'operator': 'ADMIN',
        'vehicle_manager': 'ADMIN', 
        'driver': 'VIEWER'
      };

      // Prepare payload matching backend UserCreate schema
      const payload = {
        username: newUser.username,
        email: newUser.email || `${newUser.username}@example.com`, // Use dummy email if not provided
        password: newUser.password,
        full_name: newUser.full_name,
        role: roleMap[newUser.role] || 'VIEWER',
        is_superuser: false
      };

      console.log('Sending registration payload:', payload);
      await api.post('/auth/register', payload);
      
      toast.success('사용자가 등록되었습니다');
      setShowNewUserModal(false);
      resetNewUserForm();
      loadUsers();
    } catch (error: any) {
      console.error('Registration error:', error);
      
      // Handle validation errors properly
      let message = '사용자 등록에 실패했습니다';
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        
        // If detail is an array of validation errors
        if (Array.isArray(detail)) {
          message = detail.map((err: any) => 
            `${err.loc?.join('.') || 'Error'}: ${err.msg}`
          ).join(', ');
        } 
        // If detail is a string
        else if (typeof detail === 'string') {
          message = detail;
        }
        // If detail is an object
        else {
          message = JSON.stringify(detail);
        }
      }
      
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (userId: number, currentStatus: boolean) => {
    try {
      await api.put(`/auth/users/${userId}/status`, { is_active: !currentStatus });
      toast.success(currentStatus ? '사용자가 비활성화되었습니다' : '사용자가 활성화되었습니다');
      loadUsers();
    } catch (error) {
      toast.error('상태 변경에 실패했습니다');
    }
  };

  const handleEditUser = async (userId: number) => {
    try {
      const response = await api.get(`/auth/users/${userId}`);
      const userData = response.data;
      
      // pending_employee 정보가 있으면 메인 필드로 병합
      if (userData.pending_employee) {
        const pe = userData.pending_employee;
        const merged = {
          ...userData,
          name_en: pe.name_en || '',
          address: pe.address || '',
          emergency_contact: pe.emergency_contact || '',
          employment_type: pe.employment_type || 'FULL_TIME',
          department: pe.department || '',
          position: pe.position || '',
          hire_date: pe.hire_date || '',
          license_type: pe.license_type || '',
          license_number: pe.license_number || '',
          license_issue_date: pe.license_issue_date || '',
          has_cargo_license: pe.has_cargo_license || false,
          cargo_license_number: pe.cargo_license_number || '',
          cargo_license_issue_date: pe.cargo_license_issue_date || '',
          cargo_license_expiry_date: pe.cargo_license_expiry_date || '',
          can_drive_forklift: pe.can_drive_forklift || false,
          has_forklift_certificate: pe.has_forklift_certificate || false,
          forklift_certificate_number: pe.forklift_certificate_number || '',
          forklift_certificate_issue_date: pe.forklift_certificate_issue_date || '',
          forklift_certificate_expiry_date: pe.forklift_certificate_expiry_date || '',
        };
        setEditingUser(merged);
      } else {
        // pending_employee가 없으면 기본값 설정
        const withDefaults = {
          ...userData,
          name_en: userData.name_en || '',
          address: userData.address || '',
          emergency_contact: userData.emergency_contact || '',
          employment_type: userData.employment_type || 'FULL_TIME',
          department: userData.department || '',
          position: userData.position || '',
          hire_date: userData.hire_date || '',
          license_type: userData.license_type || '',
          license_number: userData.license_number || '',
          license_issue_date: userData.license_issue_date || '',
          has_cargo_license: userData.has_cargo_license || false,
          cargo_license_number: userData.cargo_license_number || '',
          cargo_license_issue_date: userData.cargo_license_issue_date || '',
          cargo_license_expiry_date: userData.cargo_license_expiry_date || '',
          can_drive_forklift: userData.can_drive_forklift || false,
          has_forklift_certificate: userData.has_forklift_certificate || false,
          forklift_certificate_number: userData.forklift_certificate_number || '',
          forklift_certificate_issue_date: userData.forklift_certificate_issue_date || '',
          forklift_certificate_expiry_date: userData.forklift_certificate_expiry_date || '',
        };
        setEditingUser(withDefaults);
      }
      
      setEditStep(1);
      setShowEditModal(true);
    } catch (error) {
      toast.error('사용자 정보를 불러오는데 실패했습니다');
    }
  };

  const handleUpdateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // 🚫 Step 4가 아니면 제출 차단
    if (editStep !== 4) {
      console.log('Form submission blocked - current editStep:', editStep);
      return;
    }
    
    if (!editingUser) return;

    try {
      setLoading(true);
      
      console.log('✅ Updating user at editStep 4:', editingUser);
      
      // 전체 필드를 전송 (빈 문자열 날짜 필드는 undefined로 변환)
      const updateData: any = {
        email: editingUser.email || undefined,
        full_name: editingUser.full_name,
        phone: editingUser.phone || undefined,
        role: editingUser.role,
        
        // 기본 인적사항
        name_en: editingUser.name_en || undefined,
        address: editingUser.address || undefined,
        emergency_contact: editingUser.emergency_contact || undefined,
        
        // 조직 정보
        employment_type: editingUser.employment_type || undefined,
        department: editingUser.department || undefined,
        position: editingUser.position || undefined,
        
        // 근무 정보
        hire_date: editingUser.hire_date || undefined,
        
        // 운전면허
        license_type: editingUser.license_type || undefined,
        license_number: editingUser.license_number || undefined,
        license_issue_date: editingUser.license_issue_date || undefined,
        
        // 화물운송자격증
        has_cargo_license: editingUser.has_cargo_license,
        cargo_license_number: editingUser.cargo_license_number || undefined,
        cargo_license_issue_date: editingUser.cargo_license_issue_date || undefined,
        cargo_license_expiry_date: editingUser.cargo_license_expiry_date || undefined,
        
        // 지게차 자격
        can_drive_forklift: editingUser.can_drive_forklift,
        has_forklift_certificate: editingUser.has_forklift_certificate,
        forklift_certificate_number: editingUser.forklift_certificate_number || undefined,
        forklift_certificate_issue_date: editingUser.forklift_certificate_issue_date || undefined,
        forklift_certificate_expiry_date: editingUser.forklift_certificate_expiry_date || undefined,
      };
      
      await api.put(`/auth/users/${editingUser.id}`, updateData);
      toast.success('사용자 정보가 수정되었습니다');
      setShowEditModal(false);
      setEditingUser(null);
      setEditStep(1);
      loadUsers();
    } catch (error) {
      console.error('❌ Update error:', error);
      toast.error('수정에 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!window.confirm('정말 이 사용자를 삭제하시겠습니까?\n\n⚠️ 이 작업은 되돌릴 수 없습니다.')) {
      return;
    }

    try {
      // permanent=true로 완전 삭제
      await api.delete(`/auth/users/${userId}?permanent=true`);
      toast.success('사용자가 삭제되었습니다');
      loadUsers();
    } catch (error) {
      console.error('Delete error:', error);
      toast.error('사용자 삭제에 실패했습니다');
    }
  };

  const resetNewUserForm = () => {
    setNewUser({
      username: '',
      email: '',
      password: '',
      full_name: '',
      role: 'driver',
      createEmployee: true,
      employee: {
        employee_code: '',
        name: '',
        phone: '',
        email: '',
        role: 'DRIVER',
        employment_type: 'FULL_TIME',
        hire_date: new Date().toISOString().split('T')[0],
        has_cargo_license: false,
        can_drive_forklift: false,
        has_forklift_certificate: false,
      }
    });
  };

  const filteredUsers = users.filter(user =>
    user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.full_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-gray-800">회원 관리</h2>
          <Button onClick={() => setShowNewUserModal(true)}>
            <UserPlus size={20} className="mr-2" />
            신규 회원 등록
          </Button>
        </div>

        {/* Tabs */}
        <div className="flex border-b mb-4">
          <button
            onClick={() => setActiveTab('users')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'users'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            활성 사용자 ({users.length})
          </button>
          <button
            onClick={() => setActiveTab('pending')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'pending'
                ? 'border-b-2 border-orange-500 text-orange-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            승인 대기 ({pendingUsers.length})
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="사용자명, 이메일, 이름으로 검색..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </Card>

      {/* Active Users Table */}
      {activeTab === 'users' && (
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-700">사용자명</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">이메일</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">이름</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">직원정보</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">권한</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">상태</th>
                  <th className="text-center py-3 px-4 font-medium text-gray-700">작업</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">{user.username}</td>
                    <td className="py-3 px-4">{user.email}</td>
                    <td className="py-3 px-4">{user.full_name}</td>
                    <td className="py-3 px-4">
                      {user.employee ? (
                        <div className="text-sm">
                          <div className="font-medium">{user.employee.employee_code}</div>
                        <div className="text-gray-600">{user.employee.name}</div>
                        {user.employee.department && (
                          <div className="text-gray-500">{user.employee.department}</div>
                        )}
                      </div>
                    ) : (
                      <span className="text-gray-400">미연결</span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 text-xs rounded ${
                      user.role === 'admin' ? 'bg-purple-100 text-purple-700' :
                      user.role === 'manager' ? 'bg-blue-100 text-blue-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <button
                      onClick={() => handleToggleActive(user.id, user.is_active)}
                      className={`px-3 py-1 rounded text-sm font-medium ${
                        user.is_active
                          ? 'bg-green-100 text-green-700'
                          : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {user.is_active ? '활성' : '비활성'}
                    </button>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex justify-center space-x-2">
                      <button
                        onClick={() => handleEditUser(user.id)}
                        className="text-blue-600 hover:text-blue-700"
                        title="수정"
                      >
                        <Edit2 size={18} />
                      </button>
                      <button
                        onClick={() => handleDeleteUser(user.id)}
                        className="text-red-600 hover:text-red-700"
                        title="삭제"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {filteredUsers.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              {searchTerm ? '검색 결과가 없습니다' : '등록된 사용자가 없습니다'}
            </div>
          )}
        </div>
      </Card>
      )}

      {/* Pending Users Table */}
      {activeTab === 'pending' && (
        <Card>
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-gray-800">승인 대기 중인 사용자</h3>
            <p className="text-sm text-gray-500 mt-1">회원가입 후 승인을 기다리는 사용자 목록입니다</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-700">사용자명</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">이름</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">전화번호</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">사원번호</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">가입일시</th>
                  <th className="text-center py-3 px-4 font-medium text-gray-700">작업</th>
                </tr>
              </thead>
              <tbody>
                {pendingUsers.filter(user => 
                  user.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  user.full_name?.toLowerCase().includes(searchTerm.toLowerCase())
                ).map((user) => (
                  <tr key={user.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="font-medium">{user.username}</div>
                      {user.email && <div className="text-sm text-gray-500">{user.email}</div>}
                    </td>
                    <td className="py-3 px-4">{user.full_name}</td>
                    <td className="py-3 px-4">{user.phone || '-'}</td>
                    <td className="py-3 px-4">
                      {user.pending_employee ? (
                        <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs font-medium">
                          {user.pending_employee.employee_code}
                        </span>
                      ) : '-'}
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {new Date(user.created_at).toLocaleString('ko-KR')}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex gap-2 justify-center">
                        <Button
                          size="sm"
                          onClick={() => handleApproveUser(user.id, user.username)}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          승인
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEditUser(user.id)}
                        >
                          <Edit2 size={16} />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleDeleteUser(user.id)}
                          className="text-red-600 hover:bg-red-50"
                        >
                          <Trash2 size={16} />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {pendingUsers.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                승인 대기 중인 사용자가 없습니다
              </div>
            )}
          </div>
        </Card>
      )}

      {/* New User Modal */}
      {showNewUserModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">신규 회원 등록</h3>
              
              <form onSubmit={handleCreateUser} className="space-y-6">
                {/* 계정 정보 */}
                <div className="border-b pb-4">
                  <h4 className="text-lg font-semibold text-gray-700 mb-4">계정 정보</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Input
                      label="사용자명 *"
                      value={newUser.username}
                      onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                      required
                    />
                    <Input
                      label="이메일 (선택)"
                      type="email"
                      value={newUser.email}
                      onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                    />
                    <div className="relative">
                      <Input
                        label="비밀번호 *"
                        type={showPassword ? "text" : "password"}
                        value={newUser.password}
                        onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-9 text-gray-500"
                      >
                        {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                      </button>
                    </div>
                    <Input
                      label="이름 *"
                      value={newUser.full_name}
                      onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
                      required
                    />
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        권한 *
                      </label>
                      <select
                        value={newUser.role}
                        onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        required
                      >
                        <option value="driver">운전직</option>
                        <option value="vehicle_manager">차량관리</option>
                        <option value="operator">운영</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* 직원 정보 생성 옵션 */}
                <div className="border-b pb-4">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={newUser.createEmployee}
                      onChange={(e) => setNewUser({ ...newUser, createEmployee: e.target.checked })}
                      className="w-4 h-4 text-blue-600"
                    />
                    <span className="text-sm font-medium text-gray-700">
                      직원 정보도 함께 생성 (인사카드 연동)
                    </span>
                  </label>
                </div>

                {/* 직원 기본 정보 */}
                {newUser.createEmployee && (
                  <>
                    <div className="border-b pb-4">
                      <h4 className="text-lg font-semibold text-gray-700 mb-4">직원 기본 정보</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Input
                          label="사원번호 *"
                          value={newUser.employee.employee_code}
                          onChange={(e) => setNewUser({
                            ...newUser,
                            employee: { ...newUser.employee, employee_code: e.target.value }
                          })}
                          placeholder="예: D001, A001"
                          required={newUser.createEmployee}
                        />

                        <Input
                          label="전화번호 *"
                          value={newUser.employee.phone}
                          onChange={(e) => setNewUser({
                            ...newUser,
                            employee: { ...newUser.employee, phone: e.target.value }
                          })}
                          placeholder="010-1234-5678"
                          required={newUser.createEmployee}
                        />
                        <Input
                          label="이메일"
                          type="email"
                          value={newUser.employee.email || ''}
                          onChange={(e) => setNewUser({
                            ...newUser,
                            employee: { ...newUser.employee, email: e.target.value }
                          })}
                        />
                        <Input
                          label="비상연락처"
                          value={newUser.employee.emergency_contact || ''}
                          onChange={(e) => setNewUser({
                            ...newUser,
                            employee: { ...newUser.employee, emergency_contact: e.target.value }
                          })}
                        />
                        <Input
                          label="입사일 *"
                          type="date"
                          value={newUser.employee.hire_date}
                          onChange={(e) => setNewUser({
                            ...newUser,
                            employee: { ...newUser.employee, hire_date: e.target.value }
                          })}
                          required={newUser.createEmployee}
                        />
                      </div>
                      <div className="mt-4">
                        <Input
                          label="주소"
                          value={newUser.employee.address || ''}
                          onChange={(e) => setNewUser({
                            ...newUser,
                            employee: { ...newUser.employee, address: e.target.value }
                          })}
                        />
                      </div>
                    </div>

                    {/* 조직 정보 */}
                    <div className="border-b pb-4">
                      <h4 className="text-lg font-semibold text-gray-700 mb-4">조직 정보</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            직급 *
                          </label>
                          <select
                            value={newUser.employee.role}
                            onChange={(e) => setNewUser({
                              ...newUser,
                              employee: { ...newUser.employee, role: e.target.value }
                            })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            required={newUser.createEmployee}
                          >
                            <option value="DRIVER">운전직</option>
                            <option value="MANAGER">현장관리자</option>
                            <option value="ADMIN">관리자</option>
                            <option value="MASTER">총괄</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            고용 형태 *
                          </label>
                          <select
                            value={newUser.employee.employment_type}
                            onChange={(e) => setNewUser({
                              ...newUser,
                              employee: { ...newUser.employee, employment_type: e.target.value }
                            })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                            required={newUser.createEmployee}
                          >
                            <option value="FULL_TIME">정규직</option>
                            <option value="CONTRACT">계약직</option>
                            <option value="PART_TIME">파트타임</option>
                            <option value="DAILY">일용직</option>
                          </select>
                        </div>
                        <Input
                          label="부서"
                          value={newUser.employee.department || ''}
                          onChange={(e) => setNewUser({
                            ...newUser,
                            employee: { ...newUser.employee, department: e.target.value }
                          })}
                        />
                        <Input
                          label="직책"
                          value={newUser.employee.position || ''}
                          onChange={(e) => setNewUser({
                            ...newUser,
                            employee: { ...newUser.employee, position: e.target.value }
                          })}
                        />
                      </div>
                    </div>

                    {/* 운전면허 및 자격증 */}
                    <div>
                      <h4 className="text-lg font-semibold text-gray-700 mb-4">운전면허 및 자격증</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            운전면허 종류
                          </label>
                          <select
                            value={newUser.employee.license_type || ''}
                            onChange={(e) => setNewUser({
                              ...newUser,
                              employee: { ...newUser.employee, license_type: e.target.value }
                            })}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          >
                            <option value="">선택 안함</option>
                            <option value="1종 대형">1종 대형</option>
                            <option value="1종 보통">1종 보통</option>
                            <option value="2종 보통">2종 보통</option>
                          </select>
                        </div>
                        <Input
                          label="운전면허 번호"
                          value={newUser.employee.license_number || ''}
                          onChange={(e) => setNewUser({
                            ...newUser,
                            employee: { ...newUser.employee, license_number: e.target.value }
                          })}
                        />
                        <Input
                          label="운전면허 발급일"
                          type="date"
                          value={newUser.employee.license_issue_date || ''}
                          onChange={(e) => setNewUser({
                            ...newUser,
                            employee: { ...newUser.employee, license_issue_date: e.target.value }
                          })}
                        />
                      </div>
                      
                      <div className="mt-4 space-y-3">
                        <label className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={newUser.employee.has_cargo_license}
                            onChange={(e) => setNewUser({
                              ...newUser,
                              employee: { ...newUser.employee, has_cargo_license: e.target.checked }
                            })}
                            className="w-4 h-4 text-blue-600"
                          />
                          <span className="text-sm text-gray-700">화물운송자격증 보유</span>
                        </label>
                        
                        {newUser.employee.has_cargo_license && (
                          <Input
                            label="화물운송자격증 번호"
                            value={newUser.employee.cargo_license_number || ''}
                            onChange={(e) => setNewUser({
                              ...newUser,
                              employee: { ...newUser.employee, cargo_license_number: e.target.value }
                            })}
                          />
                        )}
                        
                        <label className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={newUser.employee.can_drive_forklift}
                            onChange={(e) => setNewUser({
                              ...newUser,
                              employee: { ...newUser.employee, can_drive_forklift: e.target.checked }
                            })}
                            className="w-4 h-4 text-blue-600"
                          />
                          <span className="text-sm text-gray-700">지게차 운전 가능</span>
                        </label>
                        
                        <label className="flex items-center space-x-2">
                          <input
                            type="checkbox"
                            checked={newUser.employee.has_forklift_certificate}
                            onChange={(e) => setNewUser({
                              ...newUser,
                              employee: { ...newUser.employee, has_forklift_certificate: e.target.checked }
                            })}
                            className="w-4 h-4 text-blue-600"
                          />
                          <span className="text-sm text-gray-700">지게차운전기능사 자격증 보유</span>
                        </label>
                      </div>
                    </div>
                  </>
                )}

                {/* Buttons */}
                <div className="flex justify-end space-x-3 pt-4 border-t">
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => {
                      setShowNewUserModal(false);
                      resetNewUserForm();
                    }}
                  >
                    취소
                  </Button>
                  <Button type="submit" loading={loading}>
                    등록
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Edit User Modal */}
      {showEditModal && editingUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h3 className="text-2xl font-bold text-gray-800 mb-6">사용자 정보 수정</h3>
              
              {/* Step Indicator */}
              <div className="flex items-center justify-center mb-8">
                <div className="flex items-center space-x-4">
                  {[1, 2, 3, 4].map((step) => (
                    <React.Fragment key={step}>
                      <div className={`flex items-center justify-center w-10 h-10 rounded-full ${
                        editStep === step ? 'bg-blue-600 text-white' : 
                        editStep > step ? 'bg-green-500 text-white' : 'bg-gray-300 text-gray-600'
                      }`}>
                        {step}
                      </div>
                      {step < 4 && (
                        <div className={`w-16 h-1 ${
                          editStep > step ? 'bg-green-500' : 'bg-gray-300'
                        }`} />
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>

              <form 
                onSubmit={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  
                  // 🔥 추가 보호: editStep이 4가 아니면 아무것도 하지 않음
                  if (editStep !== 4) {
                    console.warn('⚠️ Form submit attempted at editStep:', editStep, '- BLOCKED');
                    return false;
                  }
                  
                  console.log('✅ Form submit allowed at editStep 4');
                  handleUpdateUser(e);
                }} 
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    
                    // Enter 키로 제출 시도 감지
                    if (editStep !== 4) {
                      console.warn('⚠️ Enter key pressed at editStep:', editStep, '- Moving to next step instead');
                      // Step 4가 아니면 다음 단계로 이동
                      if (editStep < 4) {
                        setEditStep(editStep + 1);
                      }
                      return false;
                    }
                  }
                }}
                className="space-y-6"
              >
                {/* Step 1: 계정 정보 */}
                {editStep === 1 && (
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-gray-700 mb-4">1. 계정 정보</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Input
                        label="사용자명 *"
                        value={editingUser.username}
                        disabled
                      />
                      <Input
                        label="이메일"
                        type="email"
                        value={editingUser.email || ''}
                        onChange={(e) => setEditingUser({...editingUser, email: e.target.value})}
                      />
                      <Input
                        label="이름 *"
                        value={editingUser.full_name}
                        onChange={(e) => setEditingUser({...editingUser, full_name: e.target.value})}
                        required
                      />
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          시스템 권한 *
                        </label>
                        <select
                          value={editingUser.role}
                          onChange={(e) => setEditingUser({...editingUser, role: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          required
                        >
                          <option value="DRIVER">운전직</option>
                          <option value="ADMIN">관리자</option>
                          <option value="OPERATOR">운영</option>
                          <option value="VEHICLE_MANAGER">차량관리</option>
                        </select>
                      </div>
                    </div>
                  </div>
                )}

                {/* Step 2: 기본 인적사항 */}
                {editStep === 2 && (
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-gray-700 mb-4">2. 기본 인적사항</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Input
                        label="이름 (한글) *"
                        value={editingUser.full_name}
                        onChange={(e) => setEditingUser({...editingUser, full_name: e.target.value})}
                        required
                      />
                      <Input
                        label="영문명"
                        value={editingUser.name_en || ''}
                        onChange={(e) => setEditingUser({...editingUser, name_en: e.target.value})}
                      />
                      <Input
                        label="전화번호 *"
                        value={editingUser.phone || ''}
                        onChange={(e) => setEditingUser({...editingUser, phone: e.target.value})}
                        placeholder="010-0000-0000"
                        required
                      />
                      <Input
                        label="비상연락처"
                        value={editingUser.emergency_contact || ''}
                        onChange={(e) => setEditingUser({...editingUser, emergency_contact: e.target.value})}
                        placeholder="010-0000-0000"
                      />
                      <div className="md:col-span-2">
                        <Input
                          label="주소"
                          value={editingUser.address || ''}
                          onChange={(e) => setEditingUser({...editingUser, address: e.target.value})}
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* Step 3: 조직 및 근무 정보 */}
                {editStep === 3 && (
                  <div className="space-y-4">
                    <h4 className="text-lg font-semibold text-gray-700 mb-4">3. 조직 및 근무 정보</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          고용 형태 *
                        </label>
                        <select
                          value={editingUser.employment_type || 'FULL_TIME'}
                          onChange={(e) => setEditingUser({...editingUser, employment_type: e.target.value})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          required
                        >
                          <option value="FULL_TIME">정규직</option>
                          <option value="CONTRACT">계약직</option>
                          <option value="PART_TIME">파트타임</option>
                        </select>
                      </div>
                      <Input
                        label="입사일 *"
                        type="date"
                        value={editingUser.hire_date || ''}
                        onChange={(e) => setEditingUser({...editingUser, hire_date: e.target.value})}
                        required
                      />
                      <Input
                        label="부서"
                        value={editingUser.department || ''}
                        onChange={(e) => setEditingUser({...editingUser, department: e.target.value})}
                      />
                      <Input
                        label="직책"
                        value={editingUser.position || ''}
                        onChange={(e) => setEditingUser({...editingUser, position: e.target.value})}
                      />
                    </div>
                  </div>
                )}

                {/* Step 4: 자격증 정보 */}
                {editStep === 4 && (
                  <div className="space-y-6">
                    <h4 className="text-lg font-semibold text-gray-700 mb-4">4. 자격증 정보</h4>
                    
                    {/* 운전면허 */}
                    <div className="border-b pb-4">
                      <h5 className="font-medium text-gray-700 mb-3">운전면허</h5>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Input
                          label="면허 종류"
                          value={editingUser.license_type || ''}
                          onChange={(e) => setEditingUser({...editingUser, license_type: e.target.value})}
                          placeholder="1종 보통"
                        />
                        <Input
                          label="면허 번호"
                          value={editingUser.license_number || ''}
                          onChange={(e) => setEditingUser({...editingUser, license_number: e.target.value})}
                        />
                        <Input
                          label="발급일"
                          type="date"
                          value={editingUser.license_issue_date || ''}
                          onChange={(e) => setEditingUser({...editingUser, license_issue_date: e.target.value})}
                        />
                      </div>
                    </div>

                    {/* 화물운송자격증 */}
                    <div className="border-b pb-4">
                      <h5 className="font-medium text-gray-700 mb-3">화물운송자격증</h5>
                      <div className="mb-3">
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={editingUser.has_cargo_license || false}
                            onChange={(e) => setEditingUser({...editingUser, has_cargo_license: e.target.checked})}
                            className="mr-2"
                          />
                          <span className="text-sm text-gray-700">화물운송자격증 보유</span>
                        </label>
                      </div>
                      {editingUser.has_cargo_license && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <Input
                            label="자격증 번호"
                            value={editingUser.cargo_license_number || ''}
                            onChange={(e) => setEditingUser({...editingUser, cargo_license_number: e.target.value})}
                          />
                          <Input
                            label="발급일"
                            type="date"
                            value={editingUser.cargo_license_issue_date || ''}
                            onChange={(e) => setEditingUser({...editingUser, cargo_license_issue_date: e.target.value})}
                          />
                          <Input
                            label="만료일"
                            type="date"
                            value={editingUser.cargo_license_expiry_date || ''}
                            onChange={(e) => setEditingUser({...editingUser, cargo_license_expiry_date: e.target.value})}
                          />
                        </div>
                      )}
                    </div>

                    {/* 지게차 자격 */}
                    <div>
                      <h5 className="font-medium text-gray-700 mb-3">지게차 자격</h5>
                      <div className="space-y-3 mb-3">
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={editingUser.can_drive_forklift || false}
                            onChange={(e) => setEditingUser({...editingUser, can_drive_forklift: e.target.checked})}
                            className="mr-2"
                          />
                          <span className="text-sm text-gray-700">지게차 운전 가능</span>
                        </label>
                        <label className="flex items-center">
                          <input
                            type="checkbox"
                            checked={editingUser.has_forklift_certificate || false}
                            onChange={(e) => setEditingUser({...editingUser, has_forklift_certificate: e.target.checked})}
                            className="mr-2"
                          />
                          <span className="text-sm text-gray-700">지게차 자격증 보유</span>
                        </label>
                      </div>
                      {editingUser.has_forklift_certificate && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <Input
                            label="자격증 번호"
                            value={editingUser.forklift_certificate_number || ''}
                            onChange={(e) => setEditingUser({...editingUser, forklift_certificate_number: e.target.value})}
                          />
                          <Input
                            label="발급일"
                            type="date"
                            value={editingUser.forklift_certificate_issue_date || ''}
                            onChange={(e) => setEditingUser({...editingUser, forklift_certificate_issue_date: e.target.value})}
                          />
                          <Input
                            label="만료일"
                            type="date"
                            value={editingUser.forklift_certificate_expiry_date || ''}
                            onChange={(e) => setEditingUser({...editingUser, forklift_certificate_expiry_date: e.target.value})}
                          />
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Navigation Buttons */}
                <div className="flex justify-between items-center pt-6 border-t">
                  <div>
                    {editStep > 1 && (
                      <Button
                        type="button"
                        variant="secondary"
                        onClick={() => setEditStep(editStep - 1)}
                      >
                        이전
                      </Button>
                    )}
                  </div>
                  
                  <div className="flex gap-3">
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={() => {
                        setShowEditModal(false);
                        setEditingUser(null);
                        setEditStep(1);
                      }}
                    >
                      취소
                    </Button>
                    
                    {editStep < 4 ? (
                      <Button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          console.log(`📍 "다음" button clicked at editStep ${editStep} → moving to ${editStep + 1}`);
                          setEditStep(editStep + 1);
                        }}
                      >
                        다음
                      </Button>
                    ) : (
                      <Button 
                        type="submit" 
                        loading={loading}
                        onClick={() => {
                          console.log('💾 "저장" button clicked at editStep 4 - submitting form');
                        }}
                      >
                        저장
                      </Button>
                    )}
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserManagementTab;
