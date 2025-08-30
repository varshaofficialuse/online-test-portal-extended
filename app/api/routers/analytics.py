from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.test_session import TestSession
from app.models.question import Question
from app.schemas.analytics import TestAnalyticsOut, QuestionStat

router = APIRouter()

@router.get("/tests/{test_id}", response_model=TestAnalyticsOut)
def test_analytics(test_id: int, db: Session = Depends(get_db)):
    # Total attempts
    attempts = db.query(func.count(TestSession.id))\
                 .filter(TestSession.test_id == test_id).scalar() or 0

    # Average score
    avg_score = db.query(func.avg(TestSession.score))\
                  .filter(TestSession.test_id == test_id).scalar() or 0.0

    # Maximum score
    max_score = db.query(func.max(TestSession.max_score))\
                  .filter(TestSession.test_id == test_id).scalar() or 0

    # All questions
    questions = db.query(Question).filter(Question.test_id == test_id).all()

    # All sessions for this test
    sessions = db.query(TestSession).filter(TestSession.test_id == test_id, TestSession.submitted_at != None).all()

    qstats = []

    for q in questions:
        total_attempts = 0
        correct_count = 0

        for s in sessions:
            # Ensure session.answers exists and question is answered
            if s.answers and str(q.id) in s.answers:
                total_attempts += 1
                selected = s.answers[str(q.id)].get("selected")
                if str(selected) == str(q.answer):
                    correct_count += 1

        correct_rate = (correct_count / total_attempts) if total_attempts > 0 else 0.0

        qstats.append(
            QuestionStat(
                question_id=q.id,
                correct_rate=correct_rate,
                avg_time_seconds=None  # You can calculate later if needed
            )
        )

    return TestAnalyticsOut(
        test_id=test_id,
        avg_score=float(avg_score),
        max_score=int(max_score),
        attempts=int(attempts),
        question_stats=qstats
    )
