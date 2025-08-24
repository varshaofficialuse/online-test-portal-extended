# question.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, Enum, Text, JSON
from app.core.database import Base
import enum


class QuestionType(str, enum.Enum):
    MCQ = "mcq"
    TRUE_FALSE = "true_false"


# question.py
class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id", ondelete="CASCADE"), index=True)

    ques: Mapped[str] = mapped_column(Text)
    type: Mapped[QuestionType] = mapped_column(Enum(QuestionType))
    difficulty: Mapped[str] = mapped_column(String(20), default="medium")
    tags: Mapped[dict | None] = mapped_column(JSON, default={})
    data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=1)
    options: Mapped[list] = mapped_column(JSON, default=[])
    answer: Mapped[int | None] = mapped_column(Integer, nullable=True)


    test = relationship("Test", back_populates="questions")

