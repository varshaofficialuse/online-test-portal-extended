from pydantic import BaseModel

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteOut(BaseModel):
    id: int
    title: str
    content: str
    user_id: int

    class Config:
        from_attributes = True
