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


class TopicActivityResponse(BaseModel):
    name: str
    lessons: int


class DialogueMessageResponse(BaseModel):
    role: str
    content: str


class LatestLessonResponse(BaseModel):
    session_id: str
    status: str
    task: str
    duration_minutes: int | None
    user_messages: int
    summary: str | None
    dialogue: list[DialogueMessageResponse]


class StatsResponse(BaseModel):
    lessons_started: int
    completed_tasks: int
    today_completed: int
    user_messages: int
    last_task: str | None
    recent_tasks: list[str]
    topic_activity: list[TopicActivityResponse]
    latest_lesson: LatestLessonResponse | None
