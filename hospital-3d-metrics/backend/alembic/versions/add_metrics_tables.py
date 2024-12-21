"""add metrics tables

Revision ID: add_metrics_tables
Revises: 87f072926187
Create Date: 2024-12-20 15:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_metrics_tables'
down_revision: Union[str, None] = '87f072926187'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create floor_metrics table
    op.create_table('floor_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('floor_name', sa.String(), nullable=False),
        sa.Column('floor_id', sa.String(), nullable=False),
        sa.Column('metric_name', sa.String(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('metric_category', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create room_metrics table
    op.create_table('room_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('floor_id', sa.String(), nullable=False),
        sa.Column('room_id', sa.String(), nullable=False),
        sa.Column('metric_name', sa.String(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('metric_category', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_floor_metrics_floor_id'), 'floor_metrics', ['floor_id'], unique=False)
    op.create_index(op.f('ix_floor_metrics_metric_name'), 'floor_metrics', ['metric_name'], unique=False)
    op.create_index(op.f('ix_floor_metrics_timestamp'), 'floor_metrics', ['timestamp'], unique=False)
    
    op.create_index(op.f('ix_room_metrics_floor_id'), 'room_metrics', ['floor_id'], unique=False)
    op.create_index(op.f('ix_room_metrics_room_id'), 'room_metrics', ['room_id'], unique=False)
    op.create_index(op.f('ix_room_metrics_metric_name'), 'room_metrics', ['metric_name'], unique=False)
    op.create_index(op.f('ix_room_metrics_timestamp'), 'room_metrics', ['timestamp'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_floor_metrics_timestamp'), table_name='floor_metrics')
    op.drop_index(op.f('ix_floor_metrics_metric_name'), table_name='floor_metrics')
    op.drop_index(op.f('ix_floor_metrics_floor_id'), table_name='floor_metrics')
    
    op.drop_index(op.f('ix_room_metrics_timestamp'), table_name='room_metrics')
    op.drop_index(op.f('ix_room_metrics_metric_name'), table_name='room_metrics')
    op.drop_index(op.f('ix_room_metrics_room_id'), table_name='room_metrics')
    op.drop_index(op.f('ix_room_metrics_floor_id'), table_name='room_metrics')
    
    # Drop tables
    op.drop_table('room_metrics')
    op.drop_table('floor_metrics')
