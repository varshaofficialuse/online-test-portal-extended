from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt,JWTError
from app.core.config import settings
import random
from  app.api.routers.auth import admin_required
from app.models.note import Note
from app.models.user import User

from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.quiz import Quiz
from app.schemas.test import TestCreate, TestManualCreate, TestOut, QuestionCreate, QuestionOut
from app.models.test import Test
from app.models.question import Question, QuestionType
from app.models.user import User
router = APIRouter()
auth_scheme = HTTPBearer()



@router.post("/create", response_model=TestOut)
def create_test(payload: TestCreate, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    test = Test(**payload.dict(), creator_id=current_user.id)
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


@router.post("/create/manually", response_model=TestOut)
def create_test_manually(data: TestManualCreate, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    note = db.query(Note).filter(Note.id == data.note_id).first()
    if data.note_id and not note:
         raise HTTPException(status_code=400, detail="Note not found")

    # create Test object
    new_test = Test(
        title=data.title,
        description=data.description,
        start_at=data.start_at,
        end_at=data.end_at,
        duration_minutes=data.duration_minutes,
        shuffle_questions=data.shuffle_questions,
        allow_review=data.allow_review,
        note_id=data.note_id
    )
    db.add(new_test)
    db.flush()  # get new_test.id before adding questions

    # create Questions
    for q in data.questions:
        question = Question(
            test_id=new_test.id,
            ques=q.ques,
            type=q.type,
            difficulty=q.difficulty,
            tags=q.tags or {},
            points=q.points,
            options=q.options or [],
            answer=q.answer,
        )
        db.add(question)

    db.commit()
    db.refresh(new_test)

    return new_test


@router.post("/{test_id}/bulk-from-quiz", response_model=list[QuestionOut])
def add_random_questions_from_quiz(
    test_id: int,
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
):
    test = db.get(Test, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    quiz = db.get(Quiz, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    existing_count = db.query(Question).filter_by(test_id=test_id).count()
    if existing_count > 0:
        raise HTTPException(status_code=400, detail=f"Test already has {existing_count} questions")

    if not quiz.questions:
        raise HTTPException(status_code=400, detail="Quiz has no valid questions")

    questions_data = [q.__dict__ for q in quiz.questions] if hasattr(quiz.questions[0], "__dict__") else quiz.questions

    seen = set()
    unique_questions = []
    for q in questions_data:
        ques = q.get("question") if isinstance(q, dict) else getattr(q, "question", None)
        if ques and ques not in seen:
            seen.add(ques)
            unique_questions.append(q)

    if not unique_questions:
        raise HTTPException(status_code=400, detail="No unique questions available")

    selected = random.sample(unique_questions, min(30, len(unique_questions)))
    created_questions = []
    seen.clear()

    for q in selected:
        ques = q.get("question") if isinstance(q, dict) else getattr(q, "question", "")
        options = q.get("options") if isinstance(q, dict) else getattr(q, "options", [])
        answer = q.get("answer") if isinstance(q, dict) else getattr(q, "answer", None)

        if ques in seen:
            continue
        seen.add(ques)

        new_q = Question(
            test_id=test_id,
            ques=ques,
            type="mcq",
            difficulty="medium",
            tags={},
            options=options,
            answer=answer,
            points=1
        )
        db.add(new_q)
        created_questions.append(new_q)

    db.commit()
    for q in created_questions:
        db.refresh(q)

    return created_questions



@router.get("/{test_id}", response_model=TestOut)
def get_test(test_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    test = db.get(Test, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test


@router.get("/{test_id}/questions", response_model=List[QuestionOut])
def list_questions(test_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    return db.query(Question).filter(Question.test_id == test_id).all()


@router.delete("/{test_id}", status_code=204)
def delete_test(test_id: int, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    test = db.get(Test, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    db.delete(test)
    db.commit()
    return None

@router.get("/", response_model=List[TestOut])
def list_all_tests(db: Session = Depends(get_db)):
    """
    Get the list of all tests
    """
    tests = db.query(Test).all()
    return tests