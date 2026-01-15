"""rename redirect_uris to allowed_hosts

Revision ID: 59a3de2001d8
Revises: 
Create Date: 2026-01-15 10:29:34.035152

"""
from alembic import op
import sqlalchemy as sa


revision = '59a3de2001d8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('applications', 'redirect_uris', new_column_name='allowed_hosts')


def downgrade() -> None:
    op.alter_column('applications', 'allowed_hosts', new_column_name='redirect_uris')
