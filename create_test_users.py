"""
테스트 사용자 10명 생성 스크립트
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.core.database import SessionLocal
from app.models.user import User
from app.models.employee import Employee, EmployeeRole, EmploymentType
from passlib.context import CryptContext
from datetime import datetime, date

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_test_users():
    """테스트 사용자 10명 생성"""
    db = SessionLocal()
    
    test_users = [
        {
            "email": "driver1@test.com",
            "full_name": "김운전",
            "password": "test1234",
            "role": "DRIVER",
            "phone": "010-1111-1111",
            "employee_role": EmployeeRole.DRIVER,
            "employee_code": "D101"
        },
        {
            "email": "driver2@test.com",
            "full_name": "이기사",
            "password": "test1234",
            "role": "DRIVER",
            "phone": "010-2222-2222",
            "employee_role": EmployeeRole.DRIVER,
            "employee_code": "D102"
        },
        {
            "email": "driver3@test.com",
            "full_name": "박운송",
            "password": "test1234",
            "role": "DRIVER",
            "phone": "010-3333-3333",
            "employee_role": EmployeeRole.DRIVER,
            "employee_code": "D103"
        },
        {
            "email": "manager1@test.com",
            "full_name": "최관리",
            "password": "test1234",
            "role": "MANAGER",
            "phone": "010-4444-4444",
            "employee_role": EmployeeRole.MANAGER,
            "employee_code": "M101"
        },
        {
            "email": "manager2@test.com",
            "full_name": "정배차",
            "password": "test1234",
            "role": "VEHICLE_MANAGER",
            "phone": "010-5555-5555",
            "employee_role": EmployeeRole.MANAGER,
            "employee_code": "M102"
        },
        {
            "email": "manager3@test.com",
            "full_name": "강운영",
            "password": "test1234",
            "role": "MANAGER",
            "phone": "010-6666-6666",
            "employee_role": EmployeeRole.MANAGER,
            "employee_code": "M103"
        },
        {
            "email": "manager4@test.com",
            "full_name": "신작업",
            "password": "test1234",
            "role": "MANAGER",
            "phone": "010-7777-7777",
            "employee_role": EmployeeRole.MANAGER,
            "employee_code": "M104"
        },
        {
            "email": "admin1@test.com",
            "full_name": "윤관리자",
            "password": "test1234",
            "role": "ADMIN",
            "phone": "010-8888-8888",
            "employee_role": EmployeeRole.ADMIN,
            "employee_code": "A101"
        },
        {
            "email": "driver4@test.com",
            "full_name": "서배송",
            "password": "test1234",
            "role": "DRIVER",
            "phone": "010-9999-9999",
            "employee_role": EmployeeRole.DRIVER,
            "employee_code": "D104"
        },
        {
            "email": "driver5@test.com",
            "full_name": "황택배",
            "password": "test1234",
            "role": "DRIVER",
            "phone": "010-1010-1010",
            "employee_role": EmployeeRole.DRIVER,
            "employee_code": "D105"
        }
    ]
    
    created_count = 0
    skipped_count = 0
    
    try:
        for user_data in test_users:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            
            if existing_user:
                print(f"⏭️  사용자 이미 존재: {user_data['email']} ({user_data['full_name']})")
                skipped_count += 1
                continue
            
            # Create User
            user = User(
                username=user_data["email"].split("@")[0],  # Use email prefix as username
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=hash_password(user_data["password"]),
                role=user_data["role"],
                phone=user_data["phone"],
                is_active=True,
                approval_status="approved"  # Changed from is_approved=True
            )
            db.add(user)
            db.flush()  # Get user.id
            
            # Create Employee (without user_id - field doesn't exist)
            employee = Employee(
                employee_code=user_data["employee_code"],
                name=user_data["full_name"],
                role=user_data["employee_role"],
                email=user_data["email"],
                phone=user_data["phone"],
                hire_date=date.today(),
                employment_type=EmploymentType.FULL_TIME,  # Use enum instead of string
                department="운송팀",
                is_active=True
            )
            db.add(employee)
            db.flush()  # Get employee.id
            
            # Link User to Employee through employee_id
            user.employee_id = employee.id
            
            db.commit()
            print(f"✅ 생성 완료: {user_data['email']} ({user_data['full_name']}) - {user_data['role']}")
            created_count += 1
            
        print(f"\n" + "="*60)
        print(f"📊 결과 요약")
        print(f"="*60)
        print(f"✅ 생성됨: {created_count}명")
        print(f"⏭️  건너뜀: {skipped_count}명 (이미 존재)")
        print(f"📝 총 처리: {created_count + skipped_count}명")
        print(f"\n🔑 로그인 정보")
        print(f"="*60)
        print(f"이메일: driver1@test.com ~ driver5@test.com")
        print(f"이메일: manager1@test.com ~ manager4@test.com")
        print(f"이메일: admin1@test.com")
        print(f"비밀번호: test1234 (모든 계정 공통)")
        print(f"="*60)
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 테스트 사용자 생성 시작...")
    print("="*60)
    create_test_users()
    print("\n✅ 완료!")
