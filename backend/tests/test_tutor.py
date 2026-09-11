from types import SimpleNamespace

from app.tutor import TutorState, build_llm_messages, choose_state


def test_llm_context_contains_rules_history_and_textbook():
    history = [SimpleNamespace(role="user", content="Как найти периметр?")]
    messages = build_llm_messages(history, TutorState.GIVE_HINT, [{"page": 12, "text": "Сложи длины сторон."}])
    assert "3 класса" in messages[0]["content"]
    assert "GIVE_HINT" in messages[0]["content"]
    assert "стр. 12" in messages[0]["content"]
    assert messages[1] == {"role": "user", "content": "Как найти периметр?"}


def test_state_machine_only_reveals_solution_after_several_attempts():
    assert choose_state(0, 0) == TutorState.ASSESS_CHILD
    assert choose_state(2, 2) == TutorState.CHECK_ANSWER
    assert choose_state(5, 5) == TutorState.STRONG_HINT
    assert choose_state(6, 6) == TutorState.SHOW_SOLUTION
