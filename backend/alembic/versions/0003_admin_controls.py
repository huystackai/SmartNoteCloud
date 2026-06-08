"""admin controls

Revision ID: 0003_admin_controls
Revises: 0002_minddeck_lite_schema
Create Date: 2026-06-08 02:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_admin_controls"
down_revision = "0002_minddeck_lite_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("is_locked", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "user_ip_addresses",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("ip_address", sa.String(length=64), nullable=False, index=True),
        sa.Column("request_count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "ip_address", name="uq_user_ip_address"),
    )

    op.create_table(
        "blocked_ip_addresses",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("ip_address", sa.String(length=64), nullable=False, unique=True, index=True),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.execute(
        """
        UPDATE users
        SET is_admin = true
        WHERE id = (SELECT id FROM users ORDER BY id ASC LIMIT 1)
           OR lower(email) IN ('ntptuy.1910@gmail.com', 'giahuy.workhard@gmail.com')
        """
    )


def downgrade() -> None:
    op.drop_table("blocked_ip_addresses")
    op.drop_table("user_ip_addresses")
    op.drop_column("users", "locked_at")
    op.drop_column("users", "is_locked")
    op.drop_column("users", "is_admin")
