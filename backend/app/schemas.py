from datetime import datetime

from pydantic import BaseModel, Field


class NewSessionResponse(BaseModel):
    session_id: str
    status: str


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=1, max_length=4000)


class ChatResponse(BaseModel):
    session_id: str
    message: str


class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime


class MessagesResponse(BaseModel):
    session_id: str
    messages: list[MessageResponse]


class FinishResponse(BaseModel):
    session_id: str
    status: str
    summary: str

