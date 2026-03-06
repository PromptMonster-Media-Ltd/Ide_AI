"""Add market_analyses table.

Revision ID: 002
Revises: 001
Create Date: 2026-03-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "market_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id"), unique=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("target_market", postgresql.JSONB, nullable=True),
        sa.Column("competitive_landscape", postgresql.JSONB, nullable=True),
        sa.Column("market_metrics", postgresql.JSONB, nullable=True),
        sa.Column("revenue_projections", postgresql.JSONB, nullable=True),
        sa.Column("marketing_strategies", postgresql.JSONB, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("error_message", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_market_analyses_project_id", "market_analyses", ["project_id"])
    op.create_index("ix_market_analyses_user_id", "market_analyses", ["user_id"])


def downgrade() -> None:
    op.drop_table("market_analyses")
