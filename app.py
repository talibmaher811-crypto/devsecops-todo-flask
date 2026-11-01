"""A small Flask TODO API used for the DevSecOps Stage 1 pipeline."""

import os

from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage keeps this starter project simple for CI exercises.
todos = []
next_id = 1


@app.get("/")
def index():
    """Return a basic service status."""
    return jsonify({"service": "devsecops-todo-flask", "status": "ok"})


@app.get("/todos")
def list_todos():
    """Return all TODO items."""
    return jsonify(todos)


@app.post("/todos")
def create_todo():
    """Create a TODO item after validating the supplied title."""
    global next_id

    data = request.get_json(silent=True) or {}
    title = data.get("title")

    if not isinstance(title, str) or not title.strip():
        return jsonify({"error": "title is required"}), 400

    todo = {"id": next_id, "title": title.strip(), "done": False}
    todos.append(todo)
    next_id += 1
    return jsonify(todo), 201


@app.patch("/todos/<int:todo_id>")
def update_todo(todo_id):
    """Update the completion state of a TODO item."""
    data = request.get_json(silent=True) or {}

    for todo in todos:
        if todo["id"] == todo_id:
            done = data.get("done")
            if not isinstance(done, bool):
                return jsonify({"error": "done must be a boolean"}), 400
            todo["done"] = done
            return jsonify(todo)

    return jsonify({"error": "todo not found"}), 404


@app.delete("/todos/<int:todo_id>")
def delete_todo(todo_id):
    """Delete a TODO item."""
    for index, todo in enumerate(todos):
        if todo["id"] == todo_id:
            deleted = todos.pop(index)
            return jsonify(deleted)
    return jsonify({"error": "todo not found"}), 404


if __name__ == "__main__":  # pragma: no cover
    # Bind to loopback by default; the container sets FLASK_HOST explicitly.
    app.run(
        host=os.environ.get("FLASK_HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
    )
