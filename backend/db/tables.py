from sqlalchemy import (
    MetaData, Table, Column, String, Integer, Boolean, Text,
    DateTime, Date, ForeignKey, Index, UniqueConstraint,
    func, CheckConstraint, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.types import TypeDecorator, String as SAString
import uuid


class UUID(TypeDecorator):
    """Cross-dialect UUID: native UUID on PostgreSQL, VARCHAR(36) on SQLite."""
    impl = SAString(36)
    cache_ok = True

    def __init__(self, as_uuid: bool = True, *args, **kwargs):
        self.as_uuid = as_uuid
        super().__init__(*args, **kwargs)

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=self.as_uuid))
        return dialect.type_descriptor(SAString(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql" and self.as_uuid:
            return value
        if isinstance(value, str):
            import uuid as _uuid
            return _uuid.UUID(value)
        return value


class CompatibleJSON(TypeDecorator):
    """JSONB on PostgreSQL, JSON on SQLite."""
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB)
        return dialect.type_descriptor(JSON())

metadata = MetaData()

users = Table(
    "users", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("email", String(255), unique=True, nullable=False),
    Column("name", String(255), nullable=False),
    Column("tier", String(20), nullable=False, server_default="free"),
    Column("streak_days", Integer, nullable=False, server_default="0"),
    Column("last_active", Date, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("tier IN ('free', 'premium')", name="users_tier_check"),
)

chapters = Table(
    "chapters", metadata,
    Column("id", String(20), primary_key=True),
    Column("number", Integer, unique=True, nullable=False),
    Column("title", String(255), nullable=False),
    Column("tier_required", String(20), nullable=False, server_default="free"),
    Column("content_key", String(255), nullable=False),
    Column("search_text", Text, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("tier_required IN ('free', 'premium')", name="chapters_tier_check"),
    Index("idx_chapters_tier", "tier_required"),
    Index("idx_chapters_number", "number"),
)

progress = Table(
    "progress", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("chapter_id", String(20), ForeignKey("chapters.id"), nullable=False),
    Column("completed", Boolean, nullable=False, server_default="false"),
    Column("completed_at", DateTime(timezone=True), nullable=True),
    Column("time_spent_seconds", Integer, nullable=True),
    UniqueConstraint("user_id", "chapter_id", name="uq_progress_user_chapter"),
    Index("idx_progress_user", "user_id"),
)

quiz_results = Table(
    "quiz_results", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("chapter_id", String(20), ForeignKey("chapters.id"), nullable=False),
    Column("score", Integer, nullable=False),
    Column("total_questions", Integer, nullable=False),
    Column("answers", CompatibleJSON, nullable=False),
    Column("attempted_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Index("idx_quiz_results_user", "user_id"),
    Index("idx_quiz_results_chapter", "chapter_id"),
)

quiz_bank = Table(
    "quiz_bank", metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("chapter_id", String(20), ForeignKey("chapters.id"), nullable=False),
    Column("question_number", Integer, nullable=False),
    Column("question", Text, nullable=False),
    Column("option_a", Text, nullable=False),
    Column("option_b", Text, nullable=False),
    Column("option_c", Text, nullable=False),
    Column("option_d", Text, nullable=False),
    Column("correct_answer", String(1), nullable=False),
    UniqueConstraint("chapter_id", "question_number", name="uq_quiz_bank_chapter_question"),
    Index("idx_quiz_bank_chapter", "chapter_id"),
    CheckConstraint("correct_answer IN ('A', 'B', 'C', 'D')", name="quiz_bank_answer_check"),
)
