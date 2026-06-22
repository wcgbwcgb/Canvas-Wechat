"""Initial schema — all core tables

Revision ID: 0001
Revises:
Create Date: 2026-06-22
"""
from typing import Sequence, Union

import pgvector
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # user_mappings
    op.create_table(
        "user_mappings",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("wechat_user_id", sa.String(256), nullable=False),
        sa.Column("canvas_user_id", sa.BigInteger(), nullable=False),
        sa.Column("canvas_domain", sa.String(255), nullable=False),
        sa.Column("canvas_name", sa.String(500), nullable=True),
        sa.Column("canvas_email", sa.String(500), nullable=True),
        sa.Column("encrypted_access_token", sa.Text(), nullable=True),
        sa.Column("encrypted_refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("context_token", sa.Text(), nullable=True),
        sa.Column("context_token_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("wechat_user_id"),
    )
    op.create_index("idx_user_mappings_wechat_user_id", "user_mappings", ["wechat_user_id"])
    op.create_index("idx_user_mappings_canvas_user_id", "user_mappings", ["canvas_user_id"])

    # courses
    op.create_table(
        "courses",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("canvas_course_id", sa.BigInteger(), nullable=False),
        sa.Column("canvas_domain", sa.String(255), nullable=False),
        sa.Column("name", sa.String(1000), nullable=False),
        sa.Column("course_code", sa.String(255), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("workflow_state", sa.String(50), nullable=False, server_default="available"),
        sa.Column("syllabus_body", sa.Text(), nullable=True),
        sa.Column("raw_json", postgresql.JSONB(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_courses_canvas_course_id", "courses", ["canvas_course_id"])
    op.create_index("idx_courses_workflow_state", "courses", ["workflow_state"])

    # enrollments
    op.create_table(
        "enrollments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("canvas_enrollment_id", sa.BigInteger(), nullable=False),
        sa.Column("user_mapping_id", sa.BigInteger(), nullable=False),
        sa.Column("course_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.String(50), nullable=True, server_default="StudentEnrollment"),
        sa.Column("enrollment_state", sa.String(50), nullable=True, server_default="active"),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("canvas_enrollment_id"),
        sa.ForeignKeyConstraint(["user_mapping_id"], ["user_mappings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_enrollments_user", "enrollments", ["user_mapping_id"])
    op.create_index("idx_enrollments_course", "enrollments", ["course_id"])
    op.create_index("idx_enrollments_state", "enrollments", ["enrollment_state"])

    # assignments
    op.create_table(
        "assignments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("canvas_assignment_id", sa.BigInteger(), nullable=False),
        sa.Column("course_id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(1000), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("unlock_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lock_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("points_possible", sa.Numeric(10, 2), nullable=True),
        sa.Column("submission_types", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("workflow_state", sa.String(50), nullable=False, server_default="published"),
        sa.Column("html_url", sa.String(2000), nullable=True),
        sa.Column("raw_json", postgresql.JSONB(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_assignments_canvas_id", "assignments", ["canvas_assignment_id"])
    op.create_index("idx_assignments_course", "assignments", ["course_id"])
    op.create_index("idx_assignments_due_at", "assignments", ["due_at"], postgresql_where=sa.text("due_at IS NOT NULL"))
    op.create_index("idx_assignments_workflow", "assignments", ["workflow_state"])

    # submissions
    op.create_table(
        "submissions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("canvas_submission_id", sa.BigInteger(), nullable=False),
        sa.Column("canvas_assignment_id", sa.BigInteger(), nullable=False),
        sa.Column("user_mapping_id", sa.BigInteger(), nullable=False),
        sa.Column("course_id", sa.BigInteger(), nullable=False),
        sa.Column("score", sa.Numeric(10, 2), nullable=True),
        sa.Column("grade", sa.String(50), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("graded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("workflow_state", sa.String(50), nullable=True),
        sa.Column("late", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("missing", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        sa.Column("raw_json", postgresql.JSONB(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("canvas_submission_id"),
        sa.ForeignKeyConstraint(["user_mapping_id"], ["user_mappings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_submissions_assignment", "submissions", ["canvas_assignment_id"])
    op.create_index("idx_submissions_user", "submissions", ["user_mapping_id", "canvas_assignment_id"])
    op.create_index("idx_submissions_course", "submissions", ["course_id"])

    # announcements
    op.create_table(
        "announcements",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("canvas_topic_id", sa.BigInteger(), nullable=False),
        sa.Column("course_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(1000), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("author_name", sa.String(255), nullable=True),
        sa.Column("raw_json", postgresql.JSONB(), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_announcements_topic", "announcements", ["canvas_topic_id"])
    op.create_index("idx_announcements_course", "announcements", ["course_id"])
    op.create_index("idx_announcements_posted", "announcements", ["posted_at"], postgresql_using="btree")

    # notification_log
    op.create_table(
        "notification_log",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_mapping_id", sa.BigInteger(), nullable=False),
        sa.Column("notification_type", sa.String(50), nullable=False),
        sa.Column("course_id", sa.BigInteger(), nullable=True),
        sa.Column("assignment_id", sa.BigInteger(), nullable=True),
        sa.Column("announcement_id", sa.BigInteger(), nullable=True),
        sa.Column("submission_id", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="sent"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_mapping_id"], ["user_mappings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
        sa.ForeignKeyConstraint(["assignment_id"], ["assignments.id"]),
        sa.ForeignKeyConstraint(["announcement_id"], ["announcements.id"]),
        sa.ForeignKeyConstraint(["submission_id"], ["submissions.id"]),
    )
    op.create_index("idx_notif_log_user", "notification_log", ["user_mapping_id", "created_at"])
    op.create_index("idx_notif_log_type", "notification_log", ["notification_type"])
    op.create_index("idx_notif_log_assignment", "notification_log", ["assignment_id", "notification_type"])

    # pending_notifications
    op.create_table(
        "pending_notifications",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_mapping_id", sa.BigInteger(), nullable=False),
        sa.Column("notification_type", sa.String(50), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("max_retries", sa.Integer(), nullable=True, server_default="10"),
        sa.Column("last_retry_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_mapping_id"], ["user_mappings.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_pending_user", "pending_notifications", ["user_mapping_id"])

    # conversation_history
    op.create_table(
        "conversation_history",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("user_mapping_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tool_calls", postgresql.JSONB(), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_mapping_id"], ["user_mappings.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_conv_user", "conversation_history", ["user_mapping_id", "created_at"])

    # document_chunks (pgvector)
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("source_id", sa.BigInteger(), nullable=False),
        sa.Column("course_id", sa.BigInteger(), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", pgvector.sqlalchemy.vector.VECTOR(1536), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"]),
    )
    op.create_index("idx_doc_chunks_embedding", "document_chunks", ["embedding"],
                     postgresql_using="ivfflat",
                     postgresql_ops={"embedding": "vector_cosine_ops"},
                     postgresql_with={"lists": 100})
    op.create_index("idx_doc_chunks_source", "document_chunks", ["source_type", "source_id"])


def downgrade() -> None:
    op.drop_table("document_chunks")
    op.drop_table("conversation_history")
    op.drop_table("pending_notifications")
    op.drop_table("notification_log")
    op.drop_table("announcements")
    op.drop_table("submissions")
    op.drop_table("assignments")
    op.drop_table("enrollments")
    op.drop_table("courses")
    op.drop_table("user_mappings")
    op.execute("DROP EXTENSION IF EXISTS vector")
