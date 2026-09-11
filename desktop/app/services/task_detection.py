import re


TASK_CUES = (
    "сколько",
    "найди",
    "найдите",
    "вычисли",
    "вычислите",
    "реши",
    "решите",
    "определи",
    "узнай",
    "было",
    "стало",
    "осталось",
    "всего",
    "периметр",
    "площадь",
)
MATH_CUES = (
    "слож",
    "вычит",
    "умнож",
    "делен",
    "раздел",
    "сумм",
    "разност",
    "произвед",
    "частн",
    "руб",
    "метр",
    "сантиметр",
    "килограмм",
    "дерев",
)


def is_likely_math_task(text: str) -> bool:
    """Recognise a task statement without another LLM request.

    Short calculations and conversational replies deliberately stay in chat.
    """

    normalized = " ".join(text.lower().split())
    words = re.findall(r"[а-яёa-z0-9]+", normalized)
    if len(normalized) < 24 or len(words) < 6:
        return False
    has_task_cue = any(cue in normalized for cue in TASK_CUES)
    has_math_content = bool(re.search(r"\d", normalized)) or any(cue in normalized for cue in MATH_CUES)
    return has_task_cue and has_math_content
