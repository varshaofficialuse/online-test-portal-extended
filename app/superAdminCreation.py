
from app.core.database import SessionLocal, Base, engine
from app.core.security import hash_password
from app.models.user import User
from app.models.note import Note
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.role_enum import UserRole
from app.models.test_session import TestSession
from app.models.test import Test
from app.models.quizResult import QuizResult

# optional: create tables if not exist
Base.metadata.create_all(bind=engine)


db = SessionLocal()

# Check if superadmin already exists
existing = db.query(User).filter(User.role == "superadmin").first()
if not existing:
    superadmin = User(
        name="Varsha Mahale",
        email="malivarsha1710@gmail.com",
        password_hash=hash_password(""),
        role=UserRole.SUPERADMIN  # or "superadmin" string
    )
    db.add(superadmin)
    db.commit()
    print("✅ Super admin created!")
else:
    print("⚠️ Super admin already exists")
#execute only once