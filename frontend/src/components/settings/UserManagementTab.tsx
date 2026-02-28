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
  role: string;
  is_active: boolean;
  employee_id?: number;
  employee?: {
    employee_code: string;
    name: string;
    phone: string;
    department?: string;
    position?: string;
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
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showNewUserModal, setShowNewUserModal] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

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
  }, []);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to load users:', error);
      toast.error('사용자 목록 조회에 실패했습니다');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newUser.username || !newUser.password || !newUser.email) {
      toast.error('필수 정보를 입력해주세요');
      return;
    }

    if (newUser.createEmployee && !newUser.employee.name) {
      toast.error('직원 이름을 입력해주세요');
      return;
    }

    setLoading(true);
    try {
      await api.post('/users/register', {
        ...newUser,
        employee: newUser.createEmployee ? newUser.employee : undefined
      });
      
      toast.success('사용자가 등록되었습니다');
      setShowNewUserModal(false);
      resetNewUserForm();
      loadUsers();
    } catch (error: any) {
      const message = error.response?.data?.detail || '사용자 등록에 실패했습니다';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (userId: number, currentStatus: boolean) => {
    try {
      await api.put(`/users/${userId}/status`, { is_active: !currentStatus });
      toast.success(currentStatus ? '사용자가 비활성화되었습니다' : '사용자가 활성화되었습니다');
      loadUsers();
    } catch (error) {
      toast.error('상태 변경에 실패했습니다');
    }
  };

  const handleDeleteUser = async (userId: number) => {
    if (!window.confirm('정말 이 사용자를 삭제하시겠습니까?')) {
      return;
    }

    try {
      await api.delete(`/users/${userId}`);
      toast.success('사용자가 삭제되었습니다');
      loadUsers();
    } catch (error) {
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

      {/* Users Table */}
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
                      label="이메일 *"
                      type="email"
                      value={newUser.email}
                      onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                      required
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
                      label="이름"
                      value={newUser.full_name}
                      onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
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
                        <option value="driver">운전자</option>
                        <option value="manager">관리자</option>
                        <option value="admin">시스템 관리자</option>
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
                          label="이름 *"
                          value={newUser.employee.name}
                          onChange={(e) => setNewUser({
                            ...newUser,
                            employee: { ...newUser.employee, name: e.target.value }
                          })}
                          required={newUser.createEmployee}
                        />
                        <Input
                          label="전화번호 *"
                          value={newUser.employee.phone}
                          onChange={(e) => setNewUser({
                            ...newUser,
                            employee: { ...newUser.employee, phone: e.target.value }
                          })}
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
    </div>
  );
};

export default UserManagementTab;
