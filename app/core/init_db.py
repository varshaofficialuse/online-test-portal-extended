from app.core.database import Base, engine
# Import all models so that they are registered with SQLAlchemy metadata

from app.models.user import User  
from app.models.quiz import Quiz  
from app.models.quizResult import QuizResult 
from app.models.question import Question  
from app.models.test import Test  
from app.models.test_session import TestSession  

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
