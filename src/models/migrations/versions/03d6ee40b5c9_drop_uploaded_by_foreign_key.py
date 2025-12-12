"""drop uploaded_by foreign key

Revision ID: 03d6ee40b5c9
Revises: d8d5d9446eba
Create Date: 2025-12-03 18:28:06.697440

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03d6ee40b5c9'
down_revision = 'd8d5d9446eba'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('compliance_documents_and_policy_management_uploaded_by_fkey', 'compliance_documents_and_policy_management', type_='foreignkey')


def downgrade():
    op.create_foreign_key('compliance_documents_and_policy_management_uploaded_by_fkey', 'compliance_documents_and_policy_management', 'employees', ['uploaded_by'], ['employee_id'])
