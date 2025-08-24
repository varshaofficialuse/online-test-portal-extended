from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.test import Test
from app.models.question import Question, QuestionType
from app.models.test_session import TestSession
from app.schemas.test import SessionStart, AnswerIn

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

def _calc_score(db: Session, answers: Dict[str, Any], test_id: int) -> tuple[int, int]:
    questions = db.query(Question).filter(Question.test_id == test_id).all()
    score = 0
    max_score = 0
    answer_map = {int(k): v for k, v in answers.items()}
    for q in questions:
        max_score += q.points
        if q.type == QuestionType.MCQ:
            correct = (q.metadata or {}).get("answer")
            selected = (answer_map.get(q.id) or {}).get("selected")
            if selected is not None and str(selected) == str(correct):
                score += q.points
        elif q.type == QuestionType.TRUE_FALSE:
            correct = (q.metadata or {}).get("answer")
            selected = (answer_map.get(q.id) or {}).get("selected")
            if selected is not None and bool(selected) == bool(correct):
                score += q.points
    return score, max_score

@router.post("/{test_id}/start")
def start_session(test_id: int, payload: SessionStart, db: Session = Depends(get_db), user=Depends(get_current_user)):
    test = db.get(Test, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    now = datetime.utcnow()
    if test.start_at and now < test.start_at:
        raise HTTPException(status_code=400, detail="Test has not started yet")
    if test.end_at and now > test.end_at:
        raise HTTPException(status_code=400, detail="Test has ended")

    sess = TestSession(test_id=test_id, user_id=user.id, webcam_required=payload.webcam_required)
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return {"session_id": sess.id, "started_at": sess.started_at, "duration_minutes": test.duration_minutes}

@router.post("/{test_id}/submit")
def submit_answers(test_id: int, payload: AnswerIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sess = db.query(TestSession).filter_by(test_id=test_id, user_id=user.id, submitted_at=None).order_by(TestSession.id.desc()).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Active session not found")
    sess.answers = payload.answers
    sess.submitted_at = datetime.utcnow()
    score, max_score = _calc_score(db, payload.answers, test_id)
    sess.score = score
    sess.max_score = max_score
    db.commit()
    return {"score": score, "max_score": max_score}
