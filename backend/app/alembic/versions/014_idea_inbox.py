"""Add idea_inbox table and inbox_email on users.

Revision ID: 014
Revises: 013
Create Date: 2026-03-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "014"
down_revision: Union[str, None] = "013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Unique inbox email address per user
    op.add_column("users", sa.Column("inbox_email", sa.String(255), nullable=True, unique=True))

    op.create_table(
        "idea_inbox",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("source", sa.String(50), server_default="manual", nullable=False),
        sa.Column("sender_email", sa.String(255), nullable=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_idea_inbox_user_id", "idea_inbox", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_idea_inbox_user_id", table_name="idea_inbox")
    op.drop_table("idea_inbox")
    op.drop_column("users", "inbox_email")
