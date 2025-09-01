from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime, timedelta, timezone
from app.core.database import get_db
from app.models.test import Test
from app.models.question import Question, QuestionType
from app.models.test_session import TestSession
from app.schemas.test import SessionStart, AnswerIn
from app.core.utils import IST,now_ist, utc_now, ist_to_utc,utc_to_ist
router = APIRouter()


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings

auth_scheme = HTTPBearer()

# ------------------ Auth ------------------
def get_current_user(token: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> int:
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def calculate_score(db: Session, answers: Dict[str, Any], test_id: int) -> tuple[int, int]:

    """ calculate the score for the test recently submitted by the user"""
    questions = db.query(Question).filter(Question.test_id == test_id).all()
    score = 0
    max_score = 0
    answer_map = {int(k): v for k, v in answers.items()}

    for q in questions:
        max_score += q.points
        selected = (answer_map.get(q.id) or {}).get("selected")
        if selected is None:
            continue

        if q.type == QuestionType.MCQ or q.type == QuestionType.TRUE_FALSE:
            # Use the answer field directly
            if str(selected) == str(q.answer):
                score += q.points

    return score, max_score



@router.post("/{test_id}/start")
def start_session(
    test_id: int,
    payload: SessionStart, 
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    test = db.get(Test, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    now = now_ist()  # Current IST time

    # Convert test times to IST for comparison
    start_at = test.start_at
    end_at = test.end_at
    if start_at:
        start_at = utc_to_ist(start_at)
    if end_at:
        end_at = utc_to_ist(end_at)

    if start_at and now < start_at:
        raise HTTPException(status_code=400, detail="Test has not started yet")
    if end_at and now > end_at:
        raise HTTPException(status_code=400, detail="Test has ended")

    # Create session without 'webcam_required'
    session = TestSession(
        test_id=test_id,
        user_id=user_id
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "session_id": session.id,
        "started_at": utc_to_ist(session.started_at).isoformat(),
        "duration_minutes": test.duration_minutes
    }












from app.core.utils import utc_now  # use utc_now instead of datetime.utcnow()
@router.post("/{test_id}/submit")
def submit_answers(
    test_id: int,
    payload: AnswerIn,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """ this will submit all the selected answer by the user inside payload calculate score and return test result"""
    session = (
        db.query(TestSession)
        .filter_by(test_id=test_id, user_id=user_id, submitted_at=None)
        .order_by(TestSession.id.desc())
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Active session not found")

    session.answers = payload.answers
    session.submitted_at = utc_now()  # Store in UTC

    score, max_score = calculate_score(db, payload.answers, test_id)
    session.score = score
    session.max_score = max_score

    db.commit()
    db.refresh(session)

    # Return submitted_at in IST
    return {
        "score": score,
        "max_score": max_score,
        "submitted_at": utc_to_ist(session.submitted_at).isoformat()
    }


