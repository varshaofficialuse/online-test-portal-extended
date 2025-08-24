from pydantic import BaseModel, EmailStr
# from app.models.role_enum import UserRole


class SignupIn(BaseModel):
    name: str
    email: EmailStr
    password: str
    # role: UserRole = UserRole.STUDENT   # default to student


class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
