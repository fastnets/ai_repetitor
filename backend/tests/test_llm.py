from app.llm import OpenAICompatibleClient


class FakeResponse:
    text = "ok"

    def raise_for_status(self):
        return None

    def json(self):
        return {"choices": [{"message": {"content": "Какое действие выберешь?"}}]}


def test_deepseek_uses_short_non_thinking_request(monkeypatch):
    client = OpenAICompatibleClient(
        "https://api.deepseek.com",
        "test-key",
        "deepseek-v4-flash",
        max_tokens=250,
        disable_thinking=True,
    )
    captured = {}

    def fake_post(endpoint, headers, json):
        captured.update({"endpoint": endpoint, "headers": headers, "json": json})
        return FakeResponse()

    monkeypatch.setattr(client.client, "post", fake_post)
    result = client.chat([{"role": "user", "content": "Задача"}], session_id="lesson-id")
    client.close()

    assert result == "Какое действие выберешь?"
    assert captured["endpoint"] == "https://api.deepseek.com/chat/completions"
    assert captured["json"]["max_tokens"] == 250
    assert captured["json"]["thinking"] == {"type": "disabled"}
    assert "x-opencode-session" not in captured["headers"]
