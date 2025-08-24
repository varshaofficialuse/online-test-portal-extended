from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.test_session import TestSession
from app.models.proctor_event import ProctorEvent
from app.schemas.test import ProctorEventIn

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
@router.post("/sessions/{session_id}/event")
def log_proctor_event(session_id: int, payload: ProctorEventIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sess = db.get(TestSession, session_id)
    if not sess or sess.user_id != user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    ev = ProctorEvent(session_id=session_id, event_type=payload.event_type, payload=payload.payload or {})
    db.add(ev)

    # Aggregate simple suspicious flags
    flags = sess.suspicious_flags or {}
    flags[payload.event_type] = int(flags.get(payload.event_type, 0)) + 1
    sess.suspicious_flags = flags

    db.commit()
    return {"ok": True, "flags": flags}
