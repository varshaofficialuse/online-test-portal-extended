from pydantic import BaseModel, Field, validator
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Literal, Dict, Any
from typing import Optional
from app.core.utils import ist_to_utc

class TestCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    duration_minutes: int = 30
    shuffle_questions: bool = True
    allow_review: bool = True
    note_id: Optional[int] = None

    @validator("start_at", "end_at", pre=True)
    def convert_to_utc(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            v = datetime.fromisoformat(v) 
        return ist_to_utc(v) 


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

class QuizIdSchema(BaseModel):
    quiz_id: int

class TestManualCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    duration_minutes: int = 30
    shuffle_questions: bool = True
    allow_review: bool = True
    note_id: Optional[int] = None
    questions: List[QuestionCreate]  # 👈 include questions inside

    # convert times to UTC if provided
    @classmethod
    def validate_time(cls, v):
        return ist_to_utc(v) if v else v


class SessionStart(BaseModel):
    webcam_required: bool = False

class AnswerIn(BaseModel):
    answers: Dict[str, Any]  # {"<qid>": {"selected": "A"}}

class ProctorEventIn(BaseModel):
    event_type: str
    payload: Dict[str, Any] | None = None


class QuestionUpdate(BaseModel):
    id: Optional[int] = None
    ques: str
    type: str
    difficulty: Optional[str] = None
    tags: Optional[dict] = {}
    points: int
    options: List[str]
    answer: int

class TestManualUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    start_at: Optional[datetime]
    end_at: Optional[datetime]
    duration_minutes: Optional[int]
    shuffle_questions: Optional[bool]
    allow_review: Optional[bool]
    questions: List[QuestionUpdate]