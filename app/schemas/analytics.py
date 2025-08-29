from pydantic import BaseModel
from typing import List

class QuestionStat(BaseModel):
    question_id: int
    correct_rate: float
    avg_time_seconds: float | None = None

class TestAnalyticsOut(BaseModel):
    test_id: int
    avg_score: float
    max_score: int
    attempts: int
    question_stats: List[QuestionStat]
