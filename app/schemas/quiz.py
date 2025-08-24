from pydantic import BaseModel
from typing import List

class Question(BaseModel):
    question: str
    options: List[str]
    answer: int

class QuizOut(BaseModel):
    id: int
    note_id: int
    created_by: int
    questions: List[Question]   # ✅ list, not dict


    
class QuizCreate(BaseModel):
    note_id: int