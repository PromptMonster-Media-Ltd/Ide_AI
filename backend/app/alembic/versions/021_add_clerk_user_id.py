"""021 — Add clerk_user_id column to users table for Clerk auth integration.

Revision ID: 021
Revises: 020
"""
from alembic import op
import sqlalchemy as sa

revision = "021"
down_revision = "020"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("clerk_user_id", sa.String(255), nullable=True))
    op.create_unique_constraint("uq_users_clerk_user_id", "users", ["clerk_user_id"])
    op.create_index("ix_users_clerk_user_id", "users", ["clerk_user_id"])


def downgrade() -> None:
    op.drop_index("ix_users_clerk_user_id", table_name="users")
    op.drop_constraint("uq_users_clerk_user_id", "users", type_="unique")
    op.drop_column("users", "clerk_user_id")
