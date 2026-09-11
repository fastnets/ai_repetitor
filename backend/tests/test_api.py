def test_create_session(client):
    response = client.post("/api/session/new")
    assert response.status_code == 200
    assert response.json()["status"] == "active"
    assert len(response.json()["session_id"]) == 36


def test_messages_are_saved(client):
    session_id = client.post("/api/session/new").json()["session_id"]
    response = client.post("/api/chat", json={"session_id": session_id, "message": "Было 24, отдали 8"})
    assert response.status_code == 200
    history = client.get(f"/api/session/{session_id}/messages").json()["messages"]
    assert [item["role"] for item in history] == ["user", "assistant"]
    assert history[0]["content"] == "Было 24, отдали 8"


def test_finish_session(client):
    session_id = client.post("/api/session/new").json()["session_id"]
    response = client.post(f"/api/session/{session_id}/finish")
    assert response.status_code == 200
    assert response.json()["status"] == "finished"
    assert "Чем занимались" in response.json()["summary"]


def test_stats_only_use_saved_lessons(client):
    empty = client.get("/api/stats").json()
    assert empty["lessons_started"] == 0
    assert empty["topic_activity"] == []
    assert empty["latest_lesson"] is None

    session_id = client.post("/api/session/new").json()["session_id"]
    client.post("/api/chat", json={"session_id": session_id, "message": "Найди периметр прямоугольника"})
    active = client.get("/api/stats").json()
    assert active["lessons_started"] == 1
    assert active["completed_tasks"] == 0
    assert active["recent_tasks"] == ["Найди периметр прямоугольника"]
    assert active["topic_activity"] == [{"name": "Периметр", "lessons": 1}]

    client.post(f"/api/session/{session_id}/finish")
    finished = client.get("/api/stats").json()
    assert finished["completed_tasks"] == 1
    assert finished["today_completed"] == 1
    stats = client.get("/api/stats").json()
    assert stats["latest_lesson"]["status"] == "finished"
