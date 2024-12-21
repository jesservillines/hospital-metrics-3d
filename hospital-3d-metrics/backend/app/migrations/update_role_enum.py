from alembic import op
import sqlalchemy as sa
from sqlalchemy import Enum
from app.models.user import UserRole

def upgrade():
    # Create the enum type
    userrole = sa.Enum('admin', 'staff', 'user', name='userrole')
    userrole.create(op.get_bind(), checkfirst=True)
    
    # Drop the old role column
    op.drop_column('users', 'role')
    
    # Add the new role column with enum type
    op.add_column('users',
        sa.Column('role', sa.Enum('admin', 'staff', 'user', name='userrole'),
                 nullable=False, server_default='user')
    )

def downgrade():
    # Drop the new role column
    op.drop_column('users', 'role')
    
    # Add back the old role column
    op.add_column('users',
        sa.Column('role', sa.String(6), nullable=True)
    )
    
    # Drop the enum type
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
