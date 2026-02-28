"""Add employee model with forklift ability fields

Revision ID: e001_employee_model
Revises: 977adae777df
Create Date: 2026-02-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e001_employee_model'
down_revision: Union[str, None] = '977adae777df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create employee_role enum
    op.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            employee_code VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(100) NOT NULL,
            name_en VARCHAR(100),
            phone VARCHAR(20) NOT NULL,
            email VARCHAR(100),
            address TEXT,
            emergency_contact VARCHAR(20),
            photo_url VARCHAR(255),
            role VARCHAR(20) NOT NULL DEFAULT 'DRIVER',
            employment_type VARCHAR(20) NOT NULL DEFAULT 'FULL_TIME',
            department VARCHAR(100),
            position VARCHAR(100),
            hire_date DATE NOT NULL,
            resignation_date DATE,
            work_start_time VARCHAR(5) NOT NULL DEFAULT '08:00',
            work_end_time VARCHAR(5) NOT NULL DEFAULT '18:00',
            max_work_hours INTEGER NOT NULL DEFAULT 10,
            license_type VARCHAR(20),
            license_number VARCHAR(50),
            license_issue_date DATE,
            has_cargo_license BOOLEAN NOT NULL DEFAULT 0,
            cargo_license_number VARCHAR(50),
            cargo_license_expiry_date DATE,
            can_drive_forklift BOOLEAN NOT NULL DEFAULT 0,
            has_forklift_certificate BOOLEAN NOT NULL DEFAULT 0,
            forklift_certificate_number VARCHAR(50),
            forklift_certificate_issue_date DATE,
            forklift_certificate_expiry_date DATE,
            base_salary INTEGER,
            meal_allowance INTEGER DEFAULT 0,
            transportation_allowance INTEGER DEFAULT 0,
            hazard_allowance INTEGER DEFAULT 0,
            bank_name VARCHAR(50),
            account_number VARCHAR(50),
            account_holder VARCHAR(100),
            notes TEXT,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER,
            updated_by INTEGER,
            FOREIGN KEY(created_by) REFERENCES users (id),
            FOREIGN KEY(updated_by) REFERENCES users (id)
        )
    """)
    
    # Create indexes
    op.create_index('ix_employees_id', 'employees', ['id'])
    op.create_index('ix_employees_employee_code', 'employees', ['employee_code'])
    op.create_index('ix_employees_name', 'employees', ['name'])
    op.create_index('ix_employees_phone', 'employees', ['phone'])
    op.create_index('ix_employees_role', 'employees', ['role'])
    op.create_index('ix_employees_license_type', 'employees', ['license_type'])
    op.create_index('ix_employees_has_cargo_license', 'employees', ['has_cargo_license'])
    op.create_index('ix_employees_can_drive_forklift', 'employees', ['can_drive_forklift'])
    op.create_index('ix_employees_has_forklift_certificate', 'employees', ['has_forklift_certificate'])
    op.create_index('ix_employees_is_active', 'employees', ['is_active'])
    
    # Composite indexes
    op.create_index('idx_employee_name_phone', 'employees', ['name', 'phone'])
    op.create_index('idx_employee_role_active', 'employees', ['role', 'is_active'])
    op.create_index('idx_employee_forklift', 'employees', ['can_drive_forklift', 'has_forklift_certificate'])
    op.create_index('idx_employee_hire_date', 'employees', ['hire_date'])


def downgrade() -> None:
    op.drop_index('idx_employee_hire_date', table_name='employees')
    op.drop_index('idx_employee_forklift', table_name='employees')
    op.drop_index('idx_employee_role_active', table_name='employees')
    op.drop_index('idx_employee_name_phone', table_name='employees')
    
    op.drop_index('ix_employees_is_active', table_name='employees')
    op.drop_index('ix_employees_has_forklift_certificate', table_name='employees')
    op.drop_index('ix_employees_can_drive_forklift', table_name='employees')
    op.drop_index('ix_employees_has_cargo_license', table_name='employees')
    op.drop_index('ix_employees_license_type', table_name='employees')
    op.drop_index('ix_employees_role', table_name='employees')
    op.drop_index('ix_employees_phone', table_name='employees')
    op.drop_index('ix_employees_name', table_name='employees')
    op.drop_index('ix_employees_employee_code', table_name='employees')
    op.drop_index('ix_employees_id', table_name='employees')
    
    op.drop_table('employees')
