"""add default roles

Revision ID: add_default_roles
Revises: 157b83656103
Create Date: 2024-12-18 20:12:36.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
import uuid


# revision identifiers, used by Alembic.
revision = 'add_default_roles'
down_revision = '157b83656103'
branch_labels = None
depends_on = None


def upgrade():
    # Create default roles
    default_roles = [
        {
            'id': str(uuid.uuid4()),
            'role_name': 'ADMIN',
            'patient_access': 'full',
            'staff_access': 'full',
            'resource_access': 'full',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'role_name': 'STAFF',
            'patient_access': 'limited',
            'staff_access': 'view',
            'resource_access': 'limited',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        },
        {
            'id': str(uuid.uuid4()),
            'role_name': 'USER',
            'patient_access': 'none',
            'staff_access': 'none',
            'resource_access': 'view',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    ]
    
    # Insert default roles
    op.bulk_insert(
        sa.table('role_access',
            sa.Column('id', sa.String(36)),
            sa.Column('role_name', sa.String),
            sa.Column('patient_access', sa.String),
            sa.Column('staff_access', sa.String),
            sa.Column('resource_access', sa.String),
            sa.Column('created_at', sa.DateTime),
            sa.Column('updated_at', sa.DateTime)
        ),
        default_roles
    )


def downgrade():
    # Remove default roles
    op.execute("DELETE FROM role_access WHERE role_name IN ('ADMIN', 'STAFF', 'USER')")
