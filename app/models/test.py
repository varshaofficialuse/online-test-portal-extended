# test.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean, Text
from app.core.database import Base
from datetime import datetime


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    creator_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )
    note_id: Mapped[int | None] = mapped_column(   # 🔥 NEW RELATION
        ForeignKey("notes.id", ondelete="CASCADE"),
        index=True,
        nullable=True
    )
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    shuffle_questions: Mapped[bool] = mapped_column(Boolean, default=True)
    allow_review: Mapped[bool] = mapped_column(Boolean, default=True)

    # relationships
    questions = relationship("Question", back_populates="test", cascade="all, delete-orphan")
    sessions = relationship("TestSession", back_populates="test", cascade="all, delete-orphan")
    note = relationship("Note", back_populates="tests")   # 🔥 NEW RELATION
