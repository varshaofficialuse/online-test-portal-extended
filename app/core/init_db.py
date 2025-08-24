from app.core.database import Base, engine
# Import all models so that they are registered with SQLAlchemy metadata
from app.models.user import User  # noqa
from app.models.quiz import Quiz  # existing
from app.models.quizResult import QuizResult  # existing
from app.models.question import Question  # new
from app.models.test import Test  # new
from app.models.test_session import TestSession  # new
from app.models.proctor_event import ProctorEvent  # new

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
