# test_session.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, DateTime, Boolean, JSON
from app.core.database import Base
from datetime import datetime
from app.core.utils import utc_now


class TestSession(Base):
    __tablename__ = "test_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    answers: Mapped[dict] = mapped_column(JSON, default={})
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # relationships
    test = relationship("Test", back_populates="sessions")
    user = relationship("User", back_populates="test_sessions")
