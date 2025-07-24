from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# ------------------ USER SCHEMAS ------------------ #
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    elo: Optional[int] = 0
    mind_tokens: Optional[int] = 0

    class Config:
        orm_mode = True

# ------------------ AUTH TOKEN ------------------ #
class Token(BaseModel):
    access_token: str
    token_type: str


# ------------------ DEBATE SCHEMAS ------------------ #
class DebateCreate(BaseModel):
    topic: str
    stance: str


class DebateOut(BaseModel):
    id: int
    topic: str
    stance: str
    user_id: int

    class Config:
        from_attributes = True


# ------------------ MESSAGE SCHEMAS ------------------ #
class MessageCreate(BaseModel):
    debate_id: int
    sender_id: Optional[int] = None
    content: str
    sender_type: str = 'user'


class MessageOut(BaseModel):
    id: int
    content: str
    sender_id: Optional[int] = None
    debate_id: int
    timestamp: datetime
    sender_type: str

    class Config:
        from_attributes = True
