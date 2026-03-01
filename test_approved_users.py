# Test script to debug approved users query
import sys
sys.path.insert(0, '/home/user/webapp/backend')

from app.database import SessionLocal
from app.models.auth import User, PendingEmployee
from app.models.employee import Employee
from sqlalchemy import and_

db = SessionLocal()

# Check registered user IDs
registered_user_ids = db.query(User.id).join(
    Employee, User.employee_id == Employee.id
).filter(User.employee_id.isnot(None)).all()
registered_ids = [uid[0] for uid in registered_user_ids]
print(f"Registered user IDs (already have employee): {registered_ids}")

# Check approved users
approved_users = db.query(User).filter(
    and_(
        User.approval_status == 'approved',
        User.is_active == True,
        User.id.notin_(registered_ids) if registered_ids else True
    )
).all()

print(f"\nApproved users (not yet employees): {len(approved_users)}")
for user in approved_users:
    print(f"  - ID {user.id}: {user.username} ({user.full_name}), employee_id={user.employee_id}")
    
    # Check pending employee
    pending_emp = db.query(PendingEmployee).filter(
        PendingEmployee.user_id == user.id
    ).first()
    
    if pending_emp:
        print(f"    → Has pending_employee: {pending_emp.employee_code} - {pending_emp.name}")
    else:
        print(f"    → NO pending_employee record!")

db.close()
