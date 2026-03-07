"""Add error_message column to sprint_plans if missing (patch for 007).

Revision ID: 008
Revises: 007
"""
from alembic import op
import sqlalchemy as sa

revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade():
    # Safely add error_message if 007 ran without it
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name = 'sprint_plans' AND column_name = 'error_message'"
        )
    )
    if result.fetchone() is None:
        op.add_column("sprint_plans", sa.Column("error_message", sa.String(500), nullable=True))

    # Ensure unique constraint on project_id exists
    try:
        op.create_unique_constraint("uq_sprint_plans_project_id", "sprint_plans", ["project_id"])
    except Exception:
        pass  # Already exists


def downgrade():
    try:
        op.drop_constraint("uq_sprint_plans_project_id", "sprint_plans", type_="unique")
    except Exception:
        pass
    op.drop_column("sprint_plans", "error_message")
