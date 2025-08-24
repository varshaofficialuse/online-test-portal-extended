import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.core.database import Base
from app.core.config import settings

# Import your Base and models
from app.core.database import Base
from app.models.user import User
from app.models.note import Note
from app.models.quiz import Quiz
from app.models.quizResult import QuizResult  # if exists
from app.models.question import Question
from app.models.proctor_event import ProctorEvent
from app.models.role_enum import UserRole
from app.models.test_session import TestSession
from app.models.test import Test

config = context.config
fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = settings.DATABASE_URL
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": settings.DATABASE_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
