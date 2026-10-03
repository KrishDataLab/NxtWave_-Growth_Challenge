def test_track_analytics_event_success(client):
    event_payload = {
        "event_name": "hero_cta_click",
        "session_id": "sess-12345",
        "anonymous_id": "anon-67890",
        "source": "instagram",
        "medium": "ad",
        "campaign": "ai60_launch",
        "content": "story_video",
        "metadata": {"button_text": "Register Now for Free"}
    }
    response = client.post("/api/v1/events", json=event_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] is True
    assert "event_id" in data
    assert data["message"] == "Event recorded successfully"

def test_track_unsupported_event(client):
    event_payload = {
        "event_name": "unknown_random_event"
    }
    response = client.post("/api/v1/events", json=event_payload)
    assert response.status_code == 422
