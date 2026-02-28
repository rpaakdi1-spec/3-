#!/usr/bin/env python3
"""
Test script to debug signup 500 error
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import date
from app.schemas.auth import SignupRequest
from app.models.employee import EmployeeRole, EmploymentType
from app.models.user import UserRole

# Test data from the curl request
test_data = {
    "username": "testuser04",
    "password": "test123456",
    "role": "DRIVER",
    "name": "박민수",
    "phone": "010-5555-4444",
    "employee_role": "DRIVER",
    "employment_type": "FULL_TIME",
    "hire_date": "2026-02-28",
    "has_cargo_license": False,
    "can_drive_forklift": False,
    "has_forklift_certificate": False
}

try:
    print("Testing SignupRequest validation...")
    signup_request = SignupRequest(**test_data)
    print("✅ SignupRequest validation passed!")
    print(f"\nParsed data:")
    print(f"  username: {signup_request.username}")
    print(f"  role: {signup_request.role} (type: {type(signup_request.role)})")
    print(f"  employee_role: {signup_request.employee_role} (type: {type(signup_request.employee_role)})")
    print(f"  employment_type: {signup_request.employment_type} (type: {type(signup_request.employment_type)})")
    print(f"  hire_date: {signup_request.hire_date} (type: {type(signup_request.hire_date)})")
    
    print(f"\nEnum values:")
    print(f"  employee_role.value: {signup_request.employee_role.value}")
    print(f"  employment_type.value: {signup_request.employment_type.value}")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
