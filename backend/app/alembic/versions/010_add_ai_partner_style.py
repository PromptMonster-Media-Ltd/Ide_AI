"""Add ai_partner_style column to projects and sessions.

Revision ID: 010
Revises: 009
Create Date: 2026-03-10
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("ai_partner_style", sa.String(30), nullable=False, server_default="strategist"),
    )
    op.add_column(
        "sessions",
        sa.Column("ai_partner_style", sa.String(30), nullable=False, server_default="strategist"),
    )


def downgrade() -> None:
    op.drop_column("sessions", "ai_partner_style")
    op.drop_column("projects", "ai_partner_style")
