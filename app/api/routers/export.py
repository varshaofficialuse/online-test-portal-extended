from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
import io, csv
from app.core.database import get_db
from app.models.test_session import TestSession

router = APIRouter()

@router.get("/tests/{test_id}/results.csv")
def export_results_csv(test_id: int, db: Session = Depends(get_db)):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["session_id", "user_id", "score", "max_score", "started_at", "submitted_at", "invalidated"])
    for sess in db.query(TestSession).filter(TestSession.test_id == test_id).all():
        writer.writerow([sess.id, sess.user_id, sess.score, sess.max_score, sess.started_at, sess.submitted_at, sess.invalidated])
    output.seek(0)
    return StreamingResponse(iter([output.read()]), media_type="text/csv")
