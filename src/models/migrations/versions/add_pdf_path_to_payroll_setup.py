"""add pdf_path to payroll_setup

Revision ID: add_pdf_path_001
Revises: ef5cb2effd53
Create Date: 2025-01-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_pdf_path_001'
down_revision = 'ef5cb2effd53'
branch_labels = None
depends_on = None

def upgrade():
    # Add missing columns to payroll_setup table
    op.add_column('payroll_setup', sa.Column('pdf_path', sa.String(255), nullable=True))
    op.add_column('payroll_setup', sa.Column('month', sa.String(20), nullable=True))
    op.add_column('payroll_setup', sa.Column('basic_salary_type', sa.String(50), nullable=True))
    op.add_column('payroll_setup', sa.Column('hra_type', sa.String(50), nullable=True))
    op.add_column('payroll_setup', sa.Column('allowance_type', sa.String(50), nullable=True))
    op.add_column('payroll_setup', sa.Column('provident_fund_type', sa.String(50), nullable=True))
    op.add_column('payroll_setup', sa.Column('professional_tax_type', sa.String(50), nullable=True))
    op.add_column('payroll_setup', sa.Column('salary_components', sa.JSON(), nullable=True))
    op.add_column('payroll_setup', sa.Column('organization_name', sa.String(100), nullable=True))
    
    # Add indexes
    op.create_index('idx_payroll_month', 'payroll_setup', ['month'])
    op.create_index('idx_payroll_employee_id', 'payroll_setup', ['employee_id'])
    op.create_index('idx_payroll_created_at', 'payroll_setup', ['created_at'])
    op.create_index('idx_employee_month', 'payroll_setup', ['employee_id', 'month'])

def downgrade():
    # Remove indexes
    op.drop_index('idx_employee_month', 'payroll_setup')
    op.drop_index('idx_payroll_created_at', 'payroll_setup')
    op.drop_index('idx_payroll_employee_id', 'payroll_setup')
    op.drop_index('idx_payroll_month', 'payroll_setup')
    
    # Remove columns
    op.drop_column('payroll_setup', 'organization_name')
    op.drop_column('payroll_setup', 'salary_components')
    op.drop_column('payroll_setup', 'professional_tax_type')
    op.drop_column('payroll_setup', 'provident_fund_type')
    op.drop_column('payroll_setup', 'allowance_type')
    op.drop_column('payroll_setup', 'hra_type')
    op.drop_column('payroll_setup', 'basic_salary_type')
    op.drop_column('payroll_setup', 'month')
    op.drop_column('payroll_setup', 'pdf_path')