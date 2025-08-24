from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Literal, Dict, Any

class TestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    duration_minutes: int = 30
    shuffle_questions: bool = True
    allow_review: bool = True
    note_id: Optional[int] = None   # <-- FIXED


class TestOut(TestCreate):
    id: int
    creator_id: Optional[int] = None

    class Config:
        from_attributes = True

class QuestionCreate(BaseModel):
    ques: str
    type: Literal["mcq", "true_false"]
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    tags: Dict[str, Any] | None = None
    points: int = 1
    options: Optional[List[str]] = None  # For MCQs
    answer: Optional[int] = None    

class QuestionOut(QuestionCreate):
    id: int
    test_id: int

    class Config:
        from_attributes = True



class SessionStart(BaseModel):
    webcam_required: bool = False

class AnswerIn(BaseModel):
    answers: Dict[str, Any]  # {"<qid>": {"selected": "A"}}

class ProctorEventIn(BaseModel):
    event_type: str
    payload: Dict[str, Any] | None = None
