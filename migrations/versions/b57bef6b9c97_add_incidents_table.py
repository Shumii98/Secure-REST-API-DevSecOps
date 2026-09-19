"""add incidents table

Revision ID: b57bef6b9c97
Revises: 0001
Create Date: 2026-09-18 20:30:24.957340

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'b57bef6b9c97'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('incidents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('owner_id', sa.String(length=36), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        'ix_incidents_owner_id',
        'incidents',
        ['owner_id'],
        unique=False
    )

    op.create_index(
        'ix_incidents_severity_status',
        'incidents',
        ['severity', 'status'],
        unique=False
    )


def downgrade():
    op.drop_index(
        'ix_incidents_severity_status',
        table_name='incidents'
    )

    op.drop_index(
        'ix_incidents_owner_id',
        table_name='incidents'
    )

    op.drop_table('incidents')