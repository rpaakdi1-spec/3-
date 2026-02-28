#!/bin/bash
cd /root/uvis

# Create enhanced UserManagementTab component with pending approvals
cat > enhance_user_management.py << 'PYTHON_EOF'
import re

# Read the current file
with open('frontend/src/components/settings/UserManagementTab.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add approval_status to UserAccount interface
interface_pattern = r'(interface UserAccount \{[^}]+?)(\n  created_at: string;\n\})'
interface_replacement = r'\1\n  approval_status?: string;\n  approved_by?: number;\n  approved_at?: string;\2'
content = re.sub(interface_pattern, interface_replacement, content, flags=re.DOTALL)

# 2. Add pendingUsers state
state_pattern = r'(const \[users, setUsers\] = useState<UserAccount\[\]>\(\[\]\);)'
state_addition = r'\1\n  const [pendingUsers, setPendingUsers] = useState<UserAccount[]>([]);'
content = re.sub(state_pattern, state_addition, content)

# 3. Add loadPendingUsers function after loadUsers
load_users_pattern = r'(const loadUsers = async \(\) => \{[^}]+\}\);)'
load_pending_addition = r'''\1

  const loadPendingUsers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/auth/users/pending');
      // Handle both array and object response
      const data = Array.isArray(response.data) ? response.data : response.data.items || [];
      setPendingUsers(data);
    } catch (error) {
      console.error('Failed to load pending users:', error);
    } finally {
      setLoading(false);
    }
  };'''
content = re.sub(load_users_pattern, load_pending_addition, content, flags=re.DOTALL)

# 4. Update useEffect to load both lists
useeffect_pattern = r'(useEffect\(\(\) => \{\s+loadUsers\(\);\s+\}, \[\]\);)'
useeffect_replacement = r'''useEffect(() => {
    loadUsers();
    loadPendingUsers();
  }, []);'''
content = re.sub(useeffect_pattern, useeffect_replacement, content)

# 5. Add approval handlers before handleCreateUser
create_user_pattern = r'(const handleCreateUser = async)'
approval_handlers = r'''const handleApprove = async (userId: number) => {
    if (!confirm('이 사용자를 승인하시겠습니까?')) {
      return;
    }

    try {
      await api.post(`/auth/users/${userId}/approve`);
      toast.success('사용자가 승인되었습니다');
      loadPendingUsers();
      loadUsers();
    } catch (error) {
      console.error('Approval error:', error);
      toast.error('승인 처리에 실패했습니다');
    }
  };

  const handleReject = async (userId: number) => {
    const reason = prompt('거부 사유를 입력하세요 (선택사항):');
    
    if (!confirm('이 사용자 가입을 거부하시겠습니까?')) {
      return;
    }

    try {
      await api.post(`/auth/users/${userId}/reject`, { rejection_reason: reason });
      toast.success('사용자 가입이 거부되었습니다');
      loadPendingUsers();
    } catch (error) {
      console.error('Rejection error:', error);
      toast.error('거부 처리에 실패했습니다');
    }
  };

  \1'''
content = re.sub(create_user_pattern, approval_handlers, content)

# 6. Add pending users section before the main users table
# Find the main return statement and add pending section
main_table_pattern = r'(<Card className="p-6">\s+<div className="flex justify-between items-center mb-6">)'
pending_section = r'''<Card className="p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <span className="bg-yellow-100 text-yellow-800 px-2 py-1 rounded text-sm mr-2">
            {pendingUsers.length}
          </span>
          승인 대기 중인 사용자
        </h3>
        
        {pendingUsers.length === 0 ? (
          <p className="text-gray-500 text-center py-4">승인 대기 중인 사용자가 없습니다</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3">사용자명</th>
                  <th className="text-left p-3">이름</th>
                  <th className="text-left p-3">이메일</th>
                  <th className="text-left p-3">전화번호</th>
                  <th className="text-left p-3">권한</th>
                  <th className="text-left p-3">직원번호</th>
                  <th className="text-left p-3">신청일</th>
                  <th className="text-center p-3">작업</th>
                </tr>
              </thead>
              <tbody>
                {pendingUsers.map((user) => (
                  <tr key={user.id} className="border-b hover:bg-gray-50">
                    <td className="p-3">{user.username}</td>
                    <td className="p-3">{user.full_name}</td>
                    <td className="p-3">{user.email}</td>
                    <td className="p-3">{user.phone || '-'}</td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        user.role === 'MASTER' ? 'bg-purple-100 text-purple-800' :
                        user.role === 'ADMIN' ? 'bg-blue-100 text-blue-800' :
                        user.role === 'VEHICLE_MANAGER' ? 'bg-green-100 text-green-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {user.role === 'MASTER' ? '총괄관리자' :
                         user.role === 'ADMIN' ? '운영부' :
                         user.role === 'VEHICLE_MANAGER' ? '차량관리부' :
                         user.role === 'DRIVER' ? '운전사원' : '조회자'}
                      </span>
                    </td>
                    <td className="p-3">
                      {user.employee?.employee_code || '-'}
                    </td>
                    <td className="p-3 text-sm text-gray-500">
                      {new Date(user.created_at).toLocaleDateString('ko-KR')}
                    </td>
                    <td className="p-3">
                      <div className="flex justify-center gap-2">
                        <Button
                          size="sm"
                          variant="primary"
                          onClick={() => handleApprove(user.id)}
                        >
                          승인
                        </Button>
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => handleReject(user.id)}
                        >
                          거부
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      \1'''
content = re.sub(main_table_pattern, pending_section, content)

# Write the enhanced file
with open('frontend/src/components/settings/UserManagementTab.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ UserManagementTab.tsx enhanced with pending approvals")
PYTHON_EOF

# Run the Python script
python3 enhance_user_management.py

# Verify changes
echo "====== Verifying changes ======"
grep -n "pendingUsers" frontend/src/components/settings/UserManagementTab.tsx | head -5
grep -n "handleApprove\|handleReject" frontend/src/components/settings/UserManagementTab.tsx | head -5
grep -n "승인 대기 중인 사용자" frontend/src/components/settings/UserManagementTab.tsx

wc -l frontend/src/components/settings/UserManagementTab.tsx
