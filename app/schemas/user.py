from pydantic import BaseModel, EmailStr

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True
