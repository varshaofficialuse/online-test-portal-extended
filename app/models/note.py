# note.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)

    # relationships
    user = relationship("User", back_populates="notes")
    quizzes = relationship("Quiz", back_populates="note", cascade="all, delete-orphan")
    tests = relationship("Test", back_populates="note", cascade="all, delete-orphan")  # 🔥 NEW RELATION
