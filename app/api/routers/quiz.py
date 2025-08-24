from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.core.database import get_db
from app.core.config import settings
from app.models.quiz import Quiz
from app.models.note import Note
from app.models.quizResult import QuizResult
from app.schemas.quiz import QuizCreate, QuizOut
import openai
import json
from typing import List
from  app.api.routers.auth import admin_required
from app.models.user import User




router = APIRouter()

openai.api_key = settings.OPENAI_API_KEY


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings

auth_scheme = HTTPBearer()

# ------------------ Auth ------------------
def get_current_user_id(token: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> int:
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")



def generate_mcqs_from_note(note_title: str, note_content: str, num_questions: int = 30) -> list[dict]:
    messages = [
        {"role": "system", "content": "You are an assistant that outputs valid JSON only."},
        {"role": "user", "content": f"""
        Generate {num_questions} multiple-choice questions based on this note.
        Each question should have:
        - question text
        - 4 options
        - correct answer index (0-3)
        Note Title: {note_title}
        Note Content: {note_content}
        Return as JSON array of objects like this:
        [
          {{
            "question": "...",
            "options": ["...", "...", "...", "..."],
            "answer": 0
          }}
        ]
        Wrap the JSON in a single code block (```) without extra text.
        """}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    content = response.choices[0].message.content

    # Remove ``` wrapping if present
    if content.startswith("```"):
        content = "\n".join(content.split("\n")[1:-1])

    try:
        mcqs = json.loads(content)

        # Ensure output is always a list
        if isinstance(mcqs, dict):
            mcqs = list(mcqs.values())
        elif not isinstance(mcqs, list):
            raise ValueError("MCQs is not a list or dict")

        # Optional: validate each question
        for q in mcqs:
            if not all(k in q for k in ["question", "options", "answer"]):
                raise ValueError(f"Invalid question format: {q}")

        return mcqs

    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse MCQs from AI response:\n{content}\nError: {str(e)}"
        )



@router.post("/create/", response_model=QuizOut)
def create_quiz(
    data: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)  # admin or superadmin
):
    note = db.query(Note).filter(Note.id == data.note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Generate MCQs immediately
    questions = generate_mcqs_from_note(note.title, note.content, 30)

    # Save to database
    q = Quiz(note_id=note.id, created_by=current_user.id, questions=questions)
    db.add(q)
    db.commit()
    db.refresh(q)

    return q


@router.delete("/delete/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)  # admin or superadmin
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.created_by == current_user.id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found or you do not have permission to delete it")
    
    db.delete(quiz)
    db.commit()
    
    return {"detail": "Quiz deleted successfully"}




@router.get("/quizzes/", response_model=List[QuizOut])
def list_quizzes(db: Session = Depends(get_db), uid: int = Depends(get_current_user_id)):
    quizzes = db.query(Quiz).filter(Quiz.created_by == uid).all()
    result = []

    for q in quizzes:
        questions_data = q.questions

        # If stored as dict, convert to list
        if isinstance(questions_data, dict):
            questions_data = list(questions_data.values())

        # If stored as JSON string, parse first
        if isinstance(questions_data, str):
            try:
                questions_data = json.loads(questions_data)
                if isinstance(questions_data, dict):
                    questions_data = list(questions_data.values())
            except:
                questions_data = []

        result.append(
            QuizOut(
                id=q.id,
                note_id=q.note_id,
                created_by=q.created_by,
                questions=questions_data
            )
        )

    return result





@router.get("/{quiz_id}", response_model=QuizOut)
def get_quiz(quiz_id: int, db: Session = Depends(get_db), uid: int = Depends(get_current_user_id)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.created_by == uid).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz




@router.post("/{quiz_id}/submit")
def submit_quiz(
    quiz_id: int,
    answers: dict,  # { "0": 1, "1": 2, ... }
    db: Session = Depends(get_db),
    uid: int = Depends(get_current_user_id)
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = quiz.questions
    score = 0
    for idx, q in enumerate(questions):
        if str(idx) in answers and answers[str(idx)] == q["answer"]:
            score += 1

    result = QuizResult(
        quiz_id=quiz.id,
        user_id=uid,
        submitted_answers=answers,
        score=score
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    return {"quiz_id": quiz.id, "score": score, "total": len(questions)}
