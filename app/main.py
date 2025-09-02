import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routers import auth, notes, quiz, tests, sessions, analytics
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Online Test Portal API")

ALLOWED_ORIGINS = os.getenv("ALLOW_ORIGINS", "")
ALLOWED_ORIGINS = ALLOWED_ORIGINS.split(",") if ALLOWED_ORIGINS else []
print(" Allowed origins:", ALLOWED_ORIGINS)


app.add_middleware(
    CORSMiddleware,
    # allow_origins=["*"],
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(notes.router, prefix="/notes", tags=["Notes"])
app.include_router(quiz.router, prefix="/quiz", tags=["Quiz"])

@app.get("/")
def root():
    return {"status": "ok", "service": "online-test-portal-backend"}

app.include_router(tests.router, prefix="/tests", tags=["Tests"])
app.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])