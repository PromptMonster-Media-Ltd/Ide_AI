"""Add share comments, ratings, allow_feedback/allow_ratings on shares, and project_templates.

Revision ID: 015
Revises: 014
Create Date: 2026-03-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision: str = "015"
down_revision: Union[str, None] = "014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add feedback toggles to project_shares
    op.add_column("project_shares", sa.Column("allow_feedback", sa.Boolean(), server_default="true", nullable=False))
    op.add_column("project_shares", sa.Column("allow_ratings", sa.Boolean(), server_default="true", nullable=False))

    # Share comments
    op.create_table(
        "share_comments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("share_id", UUID(as_uuid=True), sa.ForeignKey("project_shares.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_name", sa.String(100), nullable=False),
        sa.Column("author_email", sa.String(255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_share_comments_share_id", "share_comments", ["share_id"])

    # Share ratings
    op.create_table(
        "share_ratings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("share_id", UUID(as_uuid=True), sa.ForeignKey("project_shares.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_name", sa.String(100), nullable=False),
        sa.Column("author_email", sa.String(255), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_share_ratings_share_id", "share_ratings", ["share_id"])

    # Project templates
    op.create_table(
        "project_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("icon", sa.String(10), server_default="📋"),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("concept_sheet", JSONB, nullable=True),
        sa.Column("is_system", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("project_templates")
    op.drop_index("ix_share_ratings_share_id", table_name="share_ratings")
    op.drop_table("share_ratings")
    op.drop_index("ix_share_comments_share_id", table_name="share_comments")
    op.drop_table("share_comments")
    op.drop_column("project_shares", "allow_ratings")
    op.drop_column("project_shares", "allow_feedback")
