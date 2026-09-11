from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import Settings, get_settings
from .db import Base, make_engine, make_session_factory
from .llm import LLMError, OpenAICompatibleClient
from .models import LessonSession, Message, utcnow
from .schemas import ChatRequest, ChatResponse, FinishResponse, MessageResponse, MessagesResponse, NewSessionResponse
from .textbook import TextbookSearch
from .tutor import build_llm_messages, choose_state


def create_app(settings: Settings | None = None, llm_client=None) -> FastAPI:
    settings = settings or get_settings()
    if settings.database_url.startswith("sqlite:///"):
        db_file = settings.database_url.removeprefix("sqlite:///")
        if db_file != ":memory:":
            Path(db_file).parent.mkdir(parents=True, exist_ok=True)
    engine = make_engine(settings.database_url)
    session_factory = make_session_factory(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        Base.metadata.create_all(engine)
        try:
            yield
        finally:
            close_llm = getattr(app.state.llm, "close", None)
            if close_llm:
                close_llm()
            engine.dispose()

    app = FastAPI(title="AI-репетитор", version="0.1.0", lifespan=lifespan)
    app.state.session_factory = session_factory
    app.state.llm = llm_client or OpenAICompatibleClient(
        settings.llm_base_url,
        settings.llm_api_key,
        settings.llm_model,
        settings.llm_timeout_seconds,
        settings.llm_max_tokens,
        settings.llm_disable_thinking,
    )
    app.state.textbook = TextbookSearch(settings.textbook_index)

    def get_db(request: Request):
        db = request.app.state.session_factory()
        try:
            yield db
        finally:
            db.close()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/session/new", response_model=NewSessionResponse)
    def new_session(db: Session = Depends(get_db)):
        lesson = LessonSession()
        db.add(lesson)
        db.commit()
        return NewSessionResponse(session_id=lesson.id, status=lesson.status)

    @app.post("/api/chat", response_model=ChatResponse)
    def chat(payload: ChatRequest, request: Request, db: Session = Depends(get_db)):
        lesson = db.get(LessonSession, payload.session_id)
        if not lesson:
            raise HTTPException(404, "Занятие не найдено")
        if lesson.status != "active":
            raise HTTPException(409, "Занятие уже завершено")

        previous_user_count = sum(message.role == "user" for message in lesson.messages)
        state = choose_state(previous_user_count, lesson.attempt_count)
        user_message = Message(session=lesson, role="user", content=payload.message, tutor_state=state.value)
        db.add(user_message)
        db.flush()
        recent_user_text = "\n".join(
            message.content for message in lesson.messages[-8:] if message.role == "user"
        )
        chunks = request.app.state.textbook.search(recent_user_text)
        llm_messages = build_llm_messages(lesson.messages, state, chunks)
        try:
            answer = request.app.state.llm.chat(llm_messages, session_id=lesson.id)
        except LLMError as exc:
            db.rollback()
            raise HTTPException(503, str(exc)) from exc

        db.add(Message(session=lesson, role="assistant", content=answer, tutor_state=state.value))
        lesson.tutor_state = state.value
        lesson.attempt_count += 1
        db.commit()
        return ChatResponse(session_id=lesson.id, message=answer)

    @app.get("/api/session/{session_id}/messages", response_model=MessagesResponse)
    def messages(session_id: str, db: Session = Depends(get_db)):
        lesson = db.get(LessonSession, session_id)
        if not lesson:
            raise HTTPException(404, "Занятие не найдено")
        return MessagesResponse(
            session_id=lesson.id,
            messages=[MessageResponse(role=m.role, content=m.content, created_at=m.created_at) for m in lesson.messages],
        )

    @app.post("/api/session/{session_id}/finish", response_model=FinishResponse)
    def finish(session_id: str, db: Session = Depends(get_db)):
        lesson = db.get(LessonSession, session_id)
        if not lesson:
            raise HTTPException(404, "Занятие не найдено")
        if lesson.status != "finished":
            user_messages = [m.content for m in lesson.messages if m.role == "user"]
            topic = user_messages[0][:160] if user_messages else "Занятие не началось"
            lesson.summary = (
                f"Чем занимались: {topic}\n"
                f"Решали: {max(0, len(user_messages) - 1)} шаг(а) после условия.\n"
                f"Сложности: потребовалось подсказок — {max(0, lesson.attempt_count - 1)}.\n"
                "Получилось: ребёнок участвовал в разборе задачи.\n"
                "Родителю: просмотрите диалог и повторите похожий пример."
            )
            lesson.status = "finished"
            lesson.tutor_state = "COMPLETE"
            lesson.finished_at = utcnow()
            db.commit()
        return FinishResponse(session_id=lesson.id, status=lesson.status, summary=lesson.summary or "")

    return app


app = create_app()
