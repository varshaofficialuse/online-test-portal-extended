from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.test_session import TestSession
from app.models.question import Question
from app.schemas.analytics import TestAnalyticsOut, QuestionStat
from fastapi import APIRouter, Depends, HTTPException
router = APIRouter()


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings

auth_scheme = HTTPBearer()



""" analytical report is created after submitting the test to user"""




def get_current_user(token: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> int:
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")





@router.get("/tests/{test_id}", response_model=TestAnalyticsOut)
def test_analytics(
    test_id: int,
    db: Session = Depends(get_db),
    uid: int = Depends(get_current_user),
):
    """ this will return the anlytical report to the user for the current submitted test only"""
    last_session = (
        db.query(TestSession)
        .filter(TestSession.test_id == test_id, TestSession.user_id == uid)
        .order_by(TestSession.submitted_at.desc())
        .first()
    )

    if not last_session:
        raise HTTPException(status_code=404, detail="No submission found for this test")

    # load all questions
    questions = db.query(Question).filter(Question.test_id == test_id).all()
    answers = last_session.answers or {}

    qstats = []
    correct_count = 0

    for q in questions:
        submitted = answers.get(str(q.id)) or answers.get(q.id)
        is_correct = False

        if submitted:
            # convert stored answer index to actual option string
            correct_option = q.options[q.answer] if isinstance(q.answer, int) else q.answer
            selected_option = submitted.get("selected")

            if selected_option == correct_option:
                is_correct = True
                correct_count += 1

        qstats.append(
            QuestionStat(
                question_id=q.id,
                correct_rate=1.0 if is_correct else 0.0,
                avg_time_seconds=None
            )
        )

    # student percentage
    student_percentage = (
        (correct_count / len(questions)) * 100 if questions else 0.0
    )

    return TestAnalyticsOut(
        test_id=test_id,
        avg_score=float(last_session.score or 0),
        max_score=int(last_session.max_score or len(questions)),
        attempts=1,  # since we only return for current user’s last attempt
        question_stats=qstats,
        student_percentage=student_percentage,
    )
