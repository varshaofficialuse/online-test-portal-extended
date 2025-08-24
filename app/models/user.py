# user.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Enum
from app.models.role_enum import UserRole
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(191), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.STUDENT, index=True)

    # relationships
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="creator", cascade="all, delete-orphan")
    quiz_results = relationship("QuizResult", back_populates="user", cascade="all, delete-orphan")
    test_sessions = relationship("TestSession", back_populates="user", cascade="all, delete-orphan")
