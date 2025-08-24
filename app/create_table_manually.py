# app/create_tables.py
from app.core.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.note import Note
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.proctor_event import ProctorEvent
from app.models.role_enum import UserRole
from app.models.test_session import TestSession
from app.models.test import Test
from app.models.quizResult import QuizResult


def create_tables():

    # Base.metadata.drop_all(bind=engine)#restricted to execute this will permanently remove our data

    print("Creating tables in database...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully.")

def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("Users in database:")
        for user in users:
            print(f"ID: {user.id}, Email: {user.email}")
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    list_users()
