from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
"""  database engine is created to connect with database with the optimized technique """

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True, pool_size=10, max_overflow=5, pool_timeout=30,)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()