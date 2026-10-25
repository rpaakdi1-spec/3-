"""
Authentication API endpoints
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User, UserRole
from app.services.auth_service import AuthService
from app.schemas.auth import (
    Token, TokenData, UserCreate, UserResponse, UserUpdate,
    UserListResponse, ChangePassword, SignupRequest, ApprovalRequest,
    UserResponseWithPending, PendingEmployeeData, UserStatusUpdate
)
from app.models.employee import Employee, EmployeeRole, EmploymentType
from app.models.pending_employee import PendingEmployee
from loguru import logger


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """현재 로그인한 사용자 조회 (Redis 캐시 300초)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = AuthService.decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    # Redis 캐시에서 유저 정보 조회 (DB 쿼리 절약)
    import hashlib, json
    token_hash = hashlib.md5(token.encode()).hexdigest()[:16]
    user_cache_key = f"auth:user:{token_hash}"
    cached_user_id = None

    try:
        from app.services.cache_service import cache_service
        cached_user_id = cache_service.get(user_cache_key)
    except Exception:
        pass

    if cached_user_id:
        user = db.query(User).filter(User.id == cached_user_id).first()
    else:
        user = db.query(User).filter(User.username == username).first()
        # 캐시에 유저 ID 저장 (5분)
        try:
            from app.services.cache_service import cache_service
            if user:
                cache_service.set(user_cache_key, user.id, ttl=300)
        except Exception:
            pass

    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 사용자입니다"
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """현재 활성 사용자"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="비활성화된 사용자입니다")
    return current_user


def require_role(required_role: UserRole):
    """역할 기반 권한 확인 데코레이터"""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if not AuthService.has_permission(current_user, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 부족합니다"
            )
        return current_user
    return role_checker


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """로그인"""
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자명 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthService.create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    db: Session = Depends(get_db)
):
    """공개 회원가입 (인사카드 양식으로 전체 정보 입력)"""
    # Check if user exists
    existing_user = db.query(User).filter(
        User.username == signup_data.username
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자명입니다"
        )
    
    # Generate unique employee_code (format: PENDING_YYYYMMDD_XXX)
    from datetime import datetime
    today = datetime.now().strftime("%Y%m%d")
    # Count pending employees today
    pending_count = db.query(PendingEmployee).filter(
        PendingEmployee.employee_code.like(f"PENDING_{today}_%")
    ).count()
    employee_code = f"PENDING_{today}_{str(pending_count + 1).zfill(3)}"
    
    # Create user in pending status
    new_user = User(
        username=signup_data.username,
        email=signup_data.email,  # Optional, can be None
        hashed_password=AuthService.get_password_hash(signup_data.password),
        full_name=signup_data.name,
        phone=signup_data.phone,
        role=signup_data.role,
        employee_id=None,  # Will be set after approval
        is_active=False,
        approval_status="pending",
        is_superuser=False
    )
    
    db.add(new_user)
    db.flush()  # Get user.id without committing
    
    # Store pending employee data
    pending_employee = PendingEmployee(
        user_id=new_user.id,
        employee_code=employee_code,  # Auto-generated
        name=signup_data.name,
        name_en=signup_data.name_en,
        phone=signup_data.phone,
        email=signup_data.email or new_user.email,
        address=signup_data.address,
        emergency_contact=signup_data.emergency_contact,
        role=signup_data.role.value,
        employment_type=signup_data.employment_type.value,
        department=signup_data.department,
        position=signup_data.position,
        hire_date=signup_data.hire_date,
        license_type=signup_data.license_type,
        license_number=signup_data.license_number,
        license_issue_date=signup_data.license_issue_date,
        has_cargo_license=signup_data.has_cargo_license,
        cargo_license_number=signup_data.cargo_license_number,
        cargo_license_issue_date=signup_data.cargo_license_issue_date,
        cargo_license_expiry_date=signup_data.cargo_license_expiry_date,
        can_drive_forklift=signup_data.can_drive_forklift,
        has_forklift_certificate=signup_data.has_forklift_certificate,
        forklift_certificate_number=signup_data.forklift_certificate_number,
        forklift_certificate_issue_date=signup_data.forklift_certificate_issue_date,
        forklift_certificate_expiry_date=signup_data.forklift_certificate_expiry_date
    )
    
    db.add(pending_employee)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New signup pending approval: {new_user.username} ({employee_code})")
    return new_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))  # Admin only
):
    """사용자 등록 (Admin만 가능)"""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자명 또는 이메일입니다"
        )
    
    user = AuthService.create_user(
        db=db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        role=user_data.role,
        is_superuser=user_data.is_superuser
    )
    
    return user


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """현재 사용자 정보 조회"""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """현재 사용자 정보 수정"""
    update_data = user_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"User updated: {current_user.username}")
    return current_user


@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """비밀번호 변경"""
    # Verify old password
    if not AuthService.verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 올바르지 않습니다"
        )
    
    # Update password
    current_user.hashed_password = AuthService.get_password_hash(password_data.new_password)
    db.commit()
    
    logger.info(f"Password changed for user: {current_user.username}")
    return {"message": "비밀번호가 변경되었습니다"}


@router.get("/users", response_model=UserListResponse)
async def get_users(
    skip: int = 0,
    limit: int = 100,
    show_inactive: bool = False,  # 비활성 사용자 포함 여부
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))  # Admin only
):
    """사용자 목록 조회 (Admin만 가능)"""
    query = db.query(User)
    
    # 기본적으로 활성 사용자만 표시
    if not show_inactive:
        query = query.filter(User.is_active == True)
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    return UserListResponse(total=total, items=users)


@router.get("/users/pending")
async def get_pending_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """승인 대기 중인 사용자 목록 조회 with PendingEmployee (MASTER, ADMIN만 가능)"""
    # Only MASTER and ADMIN can view pending users
    if current_user.role not in [UserRole.MASTER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 부족합니다"
        )
    
    total = db.query(User).filter(User.approval_status == "pending").count()
    users = db.query(User).filter(User.approval_status == "pending").offset(skip).limit(limit).all()
    
    # Manually load pending_employee for each user
    items = []
    for user in users:
        pending_emp = db.query(PendingEmployee).filter(PendingEmployee.user_id == user.id).first()
        user_dict = UserResponse.model_validate(user).model_dump()
        if pending_emp:
            user_dict['pending_employee'] = PendingEmployeeData.model_validate(pending_emp).model_dump()
        else:
            user_dict['pending_employee'] = None
        items.append(user_dict)
    
    return {"total": total, "items": items}


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))  # Admin only
):
    """사용자 상세 정보 조회 (Admin만 가능)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))  # Admin only
):
    """사용자 정보 수정 (Admin만 가능)"""
    logger.info(f"🔄 User update request for user_id={user_id} by {current_user.username}")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    update_data = user_update.model_dump(exclude_unset=True)
    logger.info(f"📋 Update data received: {len(update_data)} fields")
    logger.info(f"📝 Fields to update: {list(update_data.keys())}")
    
    # username 중복 체크 (username 변경 시)
    if 'username' in update_data and update_data['username'] != user.username:
        existing_user = db.query(User).filter(User.username == update_data['username']).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 사용자명입니다"
            )
    
    # User 테이블 업데이트 (기본 필드만)
    user_fields = ['username', 'email', 'full_name', 'phone', 'role']  # username 추가
    updated_user_fields = []
    for field in user_fields:
        if field in update_data:
            old_value = getattr(user, field)
            new_value = update_data[field]
            setattr(user, field, new_value)
            updated_user_fields.append(f"{field}: {old_value} → {new_value}")
    
    if updated_user_fields:
        logger.info(f"✅ User table updated: {', '.join(updated_user_fields)}")
    
    # PendingEmployee 테이블 업데이트 (추가 필드들)
    pending_employee = db.query(PendingEmployee).filter(PendingEmployee.user_id == user_id).first()
    if pending_employee:
        logger.info(f"📄 PendingEmployee found for user_id={user_id}")
        
        pending_fields = [
            'name_en', 'address', 'emergency_contact', 'employment_type',
            'department', 'position', 'hire_date', 'license_type', 'license_number',
            'license_issue_date', 'has_cargo_license', 'cargo_license_number',
            'cargo_license_issue_date', 'cargo_license_expiry_date',
            'can_drive_forklift', 'has_forklift_certificate',
            'forklift_certificate_number', 'forklift_certificate_issue_date',
            'forklift_certificate_expiry_date', 'role'  # role 필드 추가
        ]
        
        updated_pending_fields = []
        for field in pending_fields:
            if field in update_data:
                old_value = getattr(pending_employee, field)
                new_value = update_data[field]
                setattr(pending_employee, field, new_value)
                updated_pending_fields.append(f"{field}: {old_value} → {new_value}")
        
        # full_name → PendingEmployee.name 매핑
        if 'full_name' in update_data:
            old_name = pending_employee.name
            pending_employee.name = update_data['full_name']
            updated_pending_fields.append(f"name: {old_name} → {update_data['full_name']}")
        
        # phone도 pending_employee에 업데이트
        if 'phone' in update_data:
            old_phone = pending_employee.phone
            pending_employee.phone = update_data['phone']
            updated_pending_fields.append(f"phone: {old_phone} → {update_data['phone']}")
        
        # email도 pending_employee에 업데이트
        if 'email' in update_data:
            old_email = pending_employee.email
            pending_employee.email = update_data['email']
            updated_pending_fields.append(f"email: {old_email} → {update_data['email']}")
        
        if updated_pending_fields:
            logger.info(f"✅ PendingEmployee table updated ({len(updated_pending_fields)} fields):")
            for field_update in updated_pending_fields:
                logger.info(f"   - {field_update}")
    else:
        logger.warning(f"⚠️ No PendingEmployee found for user_id={user_id}")
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"✅ User update completed successfully: {user.username}")
    return user


@router.put("/users/{user_id}/status")
async def update_user_status(
    user_id: int,
    status_data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))  # Admin only
):
    """사용자 활성화/비활성화 (Admin만 가능)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    # Cannot deactivate self
    if user.id == current_user.id and not status_data.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신을 비활성화할 수 없습니다"
        )
    
    user.is_active = status_data.is_active
    db.commit()
    
    status_text = "활성화" if status_data.is_active else "비활성화"
    logger.info(f"User {status_text}: {user.username}")
    return {"message": f"사용자가 {status_text}되었습니다", "is_active": status_data.is_active}


@router.put("/users/{user_id}/password")
async def reset_user_password(
    user_id: int,
    password_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))  # Admin only
):
    """
    관리자가 사용자 비밀번호 재설정 (Admin만 가능)
    
    Request body:
    {
        "new_password": "새비밀번호"
    }
    """
    logger.info(f"🔄 Password reset request for user_id={user_id} by admin {current_user.username}")
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        logger.error(f"❌ User not found: user_id={user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    new_password = password_data.get('new_password')
    if not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="새 비밀번호를 입력해주세요"
        )
    
    if len(new_password) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호는 최소 4자 이상이어야 합니다"
        )
    
    # Update password
    user.hashed_password = AuthService.get_password_hash(new_password)
    db.commit()
    
    logger.info(f"✅ Password reset completed for user: {user.username} by admin {current_user.username}")
    return {"message": f"{user.username}님의 비밀번호가 재설정되었습니다"}
    """사용자 활성화/비활성화 (Admin만 가능)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    # Cannot deactivate self
    if user.id == current_user.id and not status_data.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신을 비활성화할 수 없습니다"
        )
    
    user.is_active = status_data.is_active
    db.commit()
    
    status_text = "활성화" if status_data.is_active else "비활성화"
    logger.info(f"User {status_text}: {user.username}")
    return {"message": f"사용자가 {status_text}되었습니다", "is_active": status_data.is_active}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    permanent: bool = False,  # True면 완전 삭제, False면 비활성화
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN))  # Admin only
):
    """사용자 삭제 (Admin만 가능)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    # Cannot delete self
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자기 자신을 삭제할 수 없습니다"
        )
    
    if permanent:
        # 완전 삭제: 관련 데이터 먼저 삭제
        # PendingEmployee 삭제
        db.query(PendingEmployee).filter(PendingEmployee.user_id == user_id).delete()
        
        # TODO: 다른 관련 데이터도 삭제 필요 (Dispatch, Orders 등)
        # 외래키 제약조건 확인 필요
        
        # 사용자 삭제
        db.delete(user)
        db.commit()
        logger.info(f"User permanently deleted: {user.username}")
        return {"message": "사용자가 완전히 삭제되었습니다"}
    else:
        # 소프트 삭제: 비활성화만
        user.is_active = False
        db.commit()
        logger.info(f"User deactivated: {user.username}")
        return {"message": "사용자가 비활성화되었습니다"}


@router.post("/users/{user_id}/approve")
async def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자 승인 및 인사카드 생성 (MASTER, ADMIN만 가능)"""
    try:
        logger.info(f"🔄 Approval request for user_id={user_id} by {current_user.username}")
        
        # Only MASTER and ADMIN can approve users
        if current_user.role not in [UserRole.MASTER, UserRole.ADMIN]:
            logger.warning(f"❌ Insufficient permission: {current_user.role}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 부족합니다"
            )
        
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.error(f"❌ User not found: user_id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        
        logger.info(f"📋 User found: {user.username}, status={user.approval_status}")
        
        if user.approval_status != "pending":
            logger.warning(f"❌ User not pending: status={user.approval_status}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="대기 중인 사용자만 승인할 수 있습니다"
            )
        
        # Get pending employee data
        pending_emp = db.query(PendingEmployee).filter(PendingEmployee.user_id == user_id).first()
        
        if not pending_emp:
            logger.error(f"❌ PendingEmployee not found for user_id={user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="인사카드 정보를 찾을 수 없습니다"
            )
        
        logger.info(f"📄 PendingEmployee found: {pending_emp.name}, code={pending_emp.employee_code}")
        
        # Role mapping: Map User roles to Employee roles
        # UserRole: DRIVER, ADMIN, OPERATOR, VEHICLE_MANAGER
        # EmployeeRole: DRIVER, ADMIN, MANAGER, MASTER
        user_to_employee_role_map = {
            'DRIVER': 'DRIVER',
            'ADMIN': 'ADMIN',
            'OPERATOR': 'ADMIN',  # OPERATOR → ADMIN
            'VEHICLE_MANAGER': 'MANAGER',  # VEHICLE_MANAGER → MANAGER
            'MANAGER': 'MANAGER',
            'MASTER': 'MASTER'
        }
        
        mapped_role = user_to_employee_role_map.get(pending_emp.role, 'DRIVER')  # Default: DRIVER
        logger.info(f"🔄 Role mapping: {pending_emp.role} → {mapped_role}")
        
        # Generate unique employee code based on role
        # Format: D001 (Driver), M001 (Manager), A001 (Admin), S001 (Staff)
        role_prefix_map = {
            'DRIVER': 'D',
            'MANAGER': 'M',
            'ADMIN': 'A',
            'MASTER': 'M'
        }
        role_prefix = role_prefix_map.get(mapped_role, 'S')  # Default: S (Staff)
        
        # Find the next available employee code
        existing_codes = db.query(Employee.employee_code).filter(
            Employee.employee_code.like(f"{role_prefix}%")
        ).all()
        
        if existing_codes:
            # Extract numbers and find max
            code_numbers = []
            for (code,) in existing_codes:
                try:
                    num = int(code[1:])  # Remove prefix letter
                    code_numbers.append(num)
                except ValueError:
                    continue
            next_number = max(code_numbers) + 1 if code_numbers else 1
        else:
            next_number = 1
        
        final_employee_code = f"{role_prefix}{str(next_number).zfill(3)}"
        logger.info(f"🔢 Generated new employee code: {final_employee_code} (original role: {pending_emp.role}, mapped role: {mapped_role})")
        
        # Create Employee record from pending data
        new_employee = Employee(
            employee_code=final_employee_code,  # Use generated code instead of pending code
            name=pending_emp.name,
            name_en=pending_emp.name_en,
            phone=pending_emp.phone,
            email=pending_emp.email,
            address=pending_emp.address,
            emergency_contact=pending_emp.emergency_contact,
            role=EmployeeRole(mapped_role),  # Use mapped role instead of pending_emp.role
            employment_type=EmploymentType(pending_emp.employment_type),
            department=pending_emp.department,
            position=pending_emp.position,
            hire_date=pending_emp.hire_date,
            license_type=pending_emp.license_type,
            license_number=pending_emp.license_number,
            license_issue_date=pending_emp.license_issue_date,
            has_cargo_license=pending_emp.has_cargo_license,
            cargo_license_number=pending_emp.cargo_license_number,
            cargo_license_issue_date=pending_emp.cargo_license_issue_date,
            cargo_license_expiry_date=pending_emp.cargo_license_expiry_date,
            can_drive_forklift=pending_emp.can_drive_forklift,
            has_forklift_certificate=pending_emp.has_forklift_certificate,
            forklift_certificate_number=pending_emp.forklift_certificate_number,
            forklift_certificate_issue_date=pending_emp.forklift_certificate_issue_date,
            forklift_certificate_expiry_date=pending_emp.forklift_certificate_expiry_date
        )
        
        logger.info(f"✅ Creating Employee record...")
        db.add(new_employee)
        db.flush()  # Get employee.id
        logger.info(f"✅ Employee created with id={new_employee.id}")
        
        # Update user
        user.employee_id = new_employee.id
        user.approval_status = "approved"
        user.approved_by = current_user.id
        user.approved_at = datetime.utcnow()
        user.is_active = True
        
        # Delete pending employee data (no longer needed)
        db.delete(pending_emp)
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"✅ User approved successfully: {user.username}, employee_id={new_employee.id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Approval failed for user_id={user_id}: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"승인 처리 중 오류가 발생했습니다: {str(e)}"
        )
    db.refresh(new_employee)
    
    logger.info(f"User approved & Employee created: {user.username} ({new_employee.employee_code}) by {current_user.username}")
    return {"message": "사용자가 승인되고 인사카드가 생성되었습니다", "user": UserResponse.model_validate(user)}


@router.post("/users/{user_id}/reject")
async def reject_user(
    user_id: int,
    rejection_reason: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """사용자 거부 (MASTER, ADMIN만 가능)"""
    # Only MASTER and ADMIN can reject users
    if current_user.role not in [UserRole.MASTER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 부족합니다"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다"
        )
    
    if user.approval_status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="대기 중인 사용자만 거부할 수 있습니다"
        )
    
    # Delete pending employee data
    pending_emp = db.query(PendingEmployee).filter(PendingEmployee.user_id == user_id).first()
    if pending_emp:
        db.delete(pending_emp)
    
    user.approval_status = "rejected"
    user.approved_by = current_user.id
    user.approved_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    logger.info(f"User rejected: {user.username} by {current_user.username}")
    return {"message": f"사용자 가입이 거부되었습니다{f': {rejection_reason}' if rejection_reason else ''}", "user": UserResponse.model_validate(user)}
    return {"message": f"사용자 가입이 거부되었습니다{f': {rejection_reason}' if rejection_reason else ''}", "user": UserResponse.model_validate(user)}


async def get_current_user_websocket(
    token: str,
    db: Session
) -> Optional[User]:
    """
    WebSocket용 사용자 인증
    
    Args:
        token: JWT 토큰
        db: 데이터베이스 세션
        
    Returns:
        인증된 사용자 또는 None
    """
    try:
        payload = AuthService.decode_token(token)
        
        if payload is None:
            return None
        
        username: str = payload.get("sub")
        if username is None:
            return None
        
        user = db.query(User).filter(User.username == username).first()
        if user is None or not user.is_active:
            return None
        
        return user
    except Exception as e:
        logger.error(f"WebSocket authentication failed: {e}")
        return None
