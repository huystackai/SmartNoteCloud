"""ai chat quota

Revision ID: 0004_ai_chat_quota
Revises: 0003_admin_controls
Create Date: 2026-06-08 03:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_ai_chat_quota"
down_revision = "0003_admin_controls"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=30), nullable=False, server_default="ai"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_ai_chat_messages_user_id", "ai_chat_messages", ["user_id"])
    op.create_index("ix_ai_chat_messages_created_at", "ai_chat_messages", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_ai_chat_messages_created_at", table_name="ai_chat_messages")
    op.drop_index("ix_ai_chat_messages_user_id", table_name="ai_chat_messages")
    op.drop_table("ai_chat_messages")
