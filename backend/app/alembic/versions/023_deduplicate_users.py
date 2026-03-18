"""Deduplicate user rows — keep the oldest row per email, delete newer duplicates."""

from alembic import op
import sqlalchemy as sa

revision = "023"
down_revision = "022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Delete duplicate user rows, keeping the one with the earliest created_at per email.
    # This uses a CTE to find duplicates and deletes all but the oldest.
    op.execute("""
        DELETE FROM users
        WHERE id IN (
            SELECT id FROM (
                SELECT id,
                       ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at ASC) AS rn
                FROM users
            ) ranked
            WHERE rn > 1
        )
    """)


def downgrade() -> None:
    # Cannot undo a data deletion
    pass
