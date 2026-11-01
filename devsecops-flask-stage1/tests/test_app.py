"""Tests for the TODO API."""


def test_health_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_list_todos_initially_empty(client):
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_todo(client):
    response = client.post("/todos", json={"title": "Learn DevSecOps"})
    assert response.status_code == 201
    assert response.get_json()["title"] == "Learn DevSecOps"
    assert response.get_json()["done"] is False


def test_create_todo_rejects_empty_title(client):
    response = client.post("/todos", json={"title": "   "})
    assert response.status_code == 400


def test_update_todo(client):
    created = client.post("/todos", json={"title": "Write tests"})
    todo_id = created.get_json()["id"]

    response = client.patch(f"/todos/{todo_id}", json={"done": True})
    assert response.status_code == 200
    assert response.get_json()["done"] is True


def test_update_todo_rejects_non_boolean(client):
    created = client.post("/todos", json={"title": "Review code"})
    todo_id = created.get_json()["id"]

    response = client.patch(f"/todos/{todo_id}", json={"done": "yes"})
    assert response.status_code == 400


def test_delete_todo(client):
    created = client.post("/todos", json={"title": "Delete me"})
    todo_id = created.get_json()["id"]

    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert client.get("/todos").get_json() == []


def test_missing_todo_returns_404(client):
    response = client.delete("/todos/999")
    assert response.status_code == 404
