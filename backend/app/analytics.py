from collections import Counter
from datetime import datetime, timezone

from .models import LessonSession
from .schemas import DialogueMessageResponse, LatestLessonResponse, StatsResponse, TopicActivityResponse


TOPIC_MARKERS = (
    ("Периметр", ("периметр",)),
    ("Единицы времени", ("час", "минут", "секунд", "сут", "времен")),
    ("Умножение", ("умнож", "произвед", "×", "*")),
    ("Деление", ("делен", "раздел", "частн", ":")),
    ("Сложение", ("слож", "прибав", "сумм", "+")),
    ("Вычитание", ("вычит", "отня", "уменьш", "разност", "-")),
)


def classify_topic(task: str) -> str | None:
    lowered = task.lower()
    return next((name for name, markers in TOPIC_MARKERS if any(marker in lowered for marker in markers)), None)


def first_user_message(lesson: LessonSession):
    return next((message for message in lesson.messages if message.role == "user"), None)


def build_stats(lessons: list[LessonSession]) -> StatsResponse:
    with_tasks = [(lesson, first_user_message(lesson)) for lesson in lessons]
    with_tasks = [(lesson, message) for lesson, message in with_tasks if message is not None]
    finished = [(lesson, message) for lesson, message in with_tasks if lesson.status == "finished"]
    today = datetime.now(timezone.utc).date()
    today_completed = sum(
        bool(lesson.finished_at and lesson.finished_at.date() == today) for lesson, _message in finished
    )

    topic_counts = Counter()
    for _lesson, message in with_tasks:
        topic = classify_topic(message.content)
        if topic:
            topic_counts[topic] += 1

    recent_tasks = [message.content.strip()[:180] for _lesson, message in with_tasks[:5]]
    latest_lesson = None
    if with_tasks:
        lesson, first_message = with_tasks[0]
        duration = None
        if lesson.finished_at:
            started = lesson.created_at
            finished_at = lesson.finished_at
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            if finished_at.tzinfo is None:
                finished_at = finished_at.replace(tzinfo=timezone.utc)
            duration = max(0, round((finished_at - started).total_seconds() / 60))
        latest_lesson = LatestLessonResponse(
            session_id=lesson.id,
            status=lesson.status,
            task=first_message.content.strip()[:500],
            duration_minutes=duration,
            user_messages=sum(message.role == "user" for message in lesson.messages),
            summary=lesson.summary,
            dialogue=[
                DialogueMessageResponse(role=message.role, content=message.content)
                for message in lesson.messages[-4:]
            ],
        )

    return StatsResponse(
        lessons_started=len(with_tasks),
        completed_tasks=len(finished),
        today_completed=today_completed,
        user_messages=sum(sum(message.role == "user" for message in lesson.messages) for lesson, _ in with_tasks),
        last_task=recent_tasks[0] if recent_tasks else None,
        recent_tasks=recent_tasks,
        topic_activity=[
            TopicActivityResponse(name=name, lessons=count)
            for name, count in sorted(topic_counts.items(), key=lambda item: (-item[1], item[0]))
        ],
        latest_lesson=latest_lesson,
    )
