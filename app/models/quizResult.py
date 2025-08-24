# quizResult.py
from sqlalchemy import Column, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class QuizResult(Base):
    __tablename__ = "quiz_results"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    submitted_answers = Column(JSON)  # {q_index: chosen_option}
    score = Column(Integer)

    # relationships
    quiz = relationship("Quiz", back_populates="results")
    user = relationship("User", back_populates="quiz_results")
