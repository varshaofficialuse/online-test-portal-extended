# quiz.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, JSON, ForeignKey
from app.core.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    note_id: Mapped[int] = mapped_column(ForeignKey("notes.id", ondelete="CASCADE"), index=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    questions: Mapped[dict] = mapped_column(JSON)

    # relationships
    note = relationship("Note", back_populates="quizzes")
    creator = relationship("User", back_populates="quizzes")

    results = relationship("QuizResult", back_populates="quiz", cascade="all, delete-orphan")
   
   
