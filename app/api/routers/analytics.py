from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.test_session import TestSession
from app.models.question import Question
from app.models.test import Test
from app.schemas.analytics import TestAnalyticsOut, QuestionStat

router = APIRouter()

@router.get("/tests/{test_id}", response_model=TestAnalyticsOut)
def test_analytics(test_id: int, db: Session = Depends(get_db)):
    attempts = db.query(func.count(TestSession.id)).filter(TestSession.test_id == test_id).scalar() or 0
    avg_score = db.query(func.avg(TestSession.score)).filter(TestSession.test_id == test_id).scalar() or 0.0
    max_score = db.query(func.max(TestSession.max_score)).filter(TestSession.test_id == test_id).scalar() or 0

    # Simple placeholder question stats
    q_ids = [q.id for q in db.query(Question).filter(Question.test_id == test_id).all()]
    qstats = [QuestionStat(question_id=qid, correct_rate=0.0, avg_time_seconds=None) for qid in q_ids]

    return TestAnalyticsOut(test_id=test_id, avg_score=float(avg_score), max_score=int(max_score or 0), attempts=int(attempts or 0), question_stats=qstats)
