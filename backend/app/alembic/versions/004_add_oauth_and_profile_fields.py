"""Add OAuth and profile fields to users table.

Revision ID: 004
Revises: 003
Create Date: 2026-03-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add OAuth provider fields, display_name, avatar_url, and preferences to users.

    Also makes hashed_password nullable so OAuth-only users can exist without a password.
    """
    op.add_column("users", sa.Column("display_name", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("avatar_url", sa.String(500), nullable=True))
    op.add_column("users", sa.Column("oauth_provider", sa.String(50), nullable=True))
    op.add_column("users", sa.Column("oauth_id", sa.String(255), nullable=True))
    op.add_column("users", sa.Column("preferences", postgresql.JSONB, nullable=True))

    # Make hashed_password nullable for OAuth users
    op.alter_column("users", "hashed_password", existing_type=sa.String(255), nullable=True)

    # Index for fast OAuth lookups
    op.create_index("ix_users_oauth_provider_id", "users", ["oauth_provider", "oauth_id"])


def downgrade() -> None:
    """Remove OAuth and profile columns from users."""
    op.drop_index("ix_users_oauth_provider_id", table_name="users")
    op.alter_column("users", "hashed_password", existing_type=sa.String(255), nullable=False)
    op.drop_column("users", "preferences")
    op.drop_column("users", "oauth_id")
    op.drop_column("users", "oauth_provider")
    op.drop_column("users", "avatar_url")
    op.drop_column("users", "display_name")
