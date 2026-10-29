from fastapi.testclient import TestClient
from app.main import app

def test_health():
    assert TestClient(app).get("/health").json()["status"] == "ok"

def test_create_workflow(monkeypatch):
    monkeypatch.setattr("app.main.enqueue", lambda _: "celery")
    response = TestClient(app).post("/api/v1/pipelines", json={"repository": "jenish16-9/demo", "branch": "main", "commit_sha": "abc123"})
    assert response.status_code == 202
    assert response.json()["template"] == "ci_cd"
    assert response.json()["steps"][0]["name"] == "checkout"
