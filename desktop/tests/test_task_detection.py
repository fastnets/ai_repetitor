import sys
from pathlib import Path

DESKTOP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DESKTOP))

from app.services.task_detection import is_likely_math_task


def test_short_calculation_is_not_task():
    assert not is_likely_math_task("2+2")
    assert not is_likely_math_task("Я не понимаю, помоги")


def test_word_problem_is_task():
    assert is_likely_math_task(
        "В парке было 35 деревьев. После урагана сломалось 7 деревьев. Потом посадили ещё 12 деревьев. Сколько стало?"
    )
