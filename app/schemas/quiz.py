from pydantic import BaseModel
from typing import List,Dict, Any

class Question(BaseModel):
    question: str
    options: List[str]
    answer: int

class QuizOut(BaseModel):
    id: int
    note_id: int
    title: str | None = None  

    created_by: int
    questions: List[Question]   # ✅ list, not dict
    

    class Config:
        from_attributes = True  
    
class QuizCreate(BaseModel):
    note_id: int



class AnswerSubmission(BaseModel):
    answers: Dict[int, int]  # {question_id: selected_option_index}


class ResultOut(BaseModel):
    score: int
    total: int
    details: List[Dict[str, Any]]

class ResultOut(BaseModel):
    score: int
    total: int
    details: List[Dict[str, Any]]
