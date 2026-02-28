import re

# Read the current file
with open('frontend/src/components/settings/UserManagementTab.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Add pending_employee to UserAccount interface
interface_pattern = r'(interface UserAccount \{[^}]+?created_at: string;)'
interface_add = r'''\1
  pending_employee?: {
    employee_code: string;
    name: string;
    phone: string;
    email?: string;
    role: string;
    employment_type: string;
    department?: string;
    position?: string;
    hire_date: string;
    license_type?: string;
    has_cargo_license: boolean;
    can_drive_forklift: boolean;
    has_forklift_certificate: boolean;
  };'''

content = re.sub(interface_pattern, interface_add, content, flags=re.DOTALL)

# Find the pending users table and update it to show more info
# Replace the table body section with expanded information
table_pattern = r'(<tbody>\s+\{pendingUsers\.map\(\(user\) => \(\s+<tr[^>]+>[^<]+<td className="p-3">\{user\.username\}</td>\s+<td className="p-3">\{user\.full_name\}</td>\s+<td className="p-3">\{user\.email\}</td>\s+<td className="p-3">\{user\.phone \|\| \'-\'\}</td>)'

table_replace = r'''<tbody>
                {pendingUsers.map((user) => (
                  <tr key={user.id} className="border-b hover:bg-gray-50">
                    <td className="p-3">{user.username}</td>
                    <td className="p-3">
                      {user.pending_employee?.name || user.full_name}
                      {user.pending_employee?.name_en && (
                        <div className="text-xs text-gray-500">({user.pending_employee.name_en})</div>
                      )}
                    </td>
                    <td className="p-3">{user.email}</td>
                    <td className="p-3">
                      {user.pending_employee?.phone || user.phone || '-'}
                      {user.pending_employee?.emergency_contact && (
                        <div className="text-xs text-gray-500">비상: {user.pending_employee.emergency_contact}</div>
                      )}
                    </td>'''

content = re.sub(table_pattern, table_replace, content, flags=re.DOTALL)

# Update the table to show employee info column
emp_info_pattern = r'(<td className="p-3">\s+\{user\.employee\?\.employee_code \|\| \'-\'\}\s+</td>)'
emp_info_replace = r'''<td className="p-3">
                      {user.pending_employee ? (
                        <div>
                          <div className="font-medium">{user.pending_employee.employee_code}</div>
                          <div className="text-xs text-gray-500">
                            {user.pending_employee.department && `${user.pending_employee.department} · `}
                            {user.pending_employee.position || '직책 미정'}
                          </div>
                          <div className="text-xs text-gray-400">
                            입사일: {new Date(user.pending_employee.hire_date).toLocaleDateString('ko-KR')}
                          </div>
                        </div>
                      ) : (
                        user.employee?.employee_code || '-'
                      )}
                    </td>'''

content = re.sub(emp_info_pattern, emp_info_replace, content, flags=re.DOTALL)

# Write the updated file
with open('frontend/src/components/settings/UserManagementTab.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ UserManagementTab updated with PendingEmployee display")
