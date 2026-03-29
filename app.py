import sqlite3

from flask import Flask, jsonify, request
from python_contracts_rs import contract, post, pre, pure

app = Flask(__name__)
DATABASE = "tasks.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS tasks
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         title TEXT NOT NULL,
         description TEXT DEFAULT '',
         done INTEGER DEFAULT 0,
         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    conn.close()


@contract(
    pre(lambda task: task is not None),
    post(lambda result: "id" in result and "title" in result and "done" in result),
    pure(),
)
def task_to_dict(task):
    """sqlite3.Row をAPIレスポンス用の辞書に変換する。"""
    return {
        "id": task["id"],
        "title": task["title"],
        "description": task["description"],
        "done": bool(task["done"]),
        "created_at": task["created_at"],
    }


@contract(
    pre(lambda title: isinstance(title, str) and len(title) > 0),
    pure(),
)
def validate_title(title):
    """タスクタイトルが有効であることを検証する。"""
    return title.strip()


init_db()


@app.route("/tasks", methods=["GET"])
def get_tasks():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    result = []
    for task in tasks:
        result.append(task_to_dict(task))
    return jsonify(result)


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if task is None:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task_to_dict(task))


@app.route("/tasks", methods=["POST"])
def create_task():
    if not request.json or "title" not in request.json:
        return jsonify({"error": "Title is required"}), 400
    title = validate_title(request.json["title"])
    description = request.json.get("description", "")
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO tasks (title, description) VALUES (?, ?)", (title, description)
    )
    conn.commit()
    task_id = cursor.lastrowid
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return jsonify(task_to_dict(task)), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404
    title = request.json.get("title", task["title"])
    description = request.json.get("description", task["description"])
    done = request.json.get("done", bool(task["done"]))
    conn.execute(
        "UPDATE tasks SET title = ?, description = ?, done = ? WHERE id = ?",
        (title, description, int(done), task_id),
    )
    conn.commit()
    updated = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return jsonify(task_to_dict(updated))


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task deleted"})


@app.route("/tasks/search", methods=["GET"])
def search_tasks():
    query = request.args.get("q", "")
    if query == "":
        return jsonify({"error": "Search query is required"}), 400
    conn = get_db()
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE title LIKE ? OR description LIKE ?",
        ("%" + query + "%", "%" + query + "%"),
    ).fetchall()
    conn.close()
    result = []
    for task in tasks:
        result.append(task_to_dict(task))
    return jsonify(result)


@app.route("/tasks/<int:task_id>/toggle", methods=["PATCH"])
def toggle_task(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404
    new_status = 0 if task["done"] else 1
    conn.execute("UPDATE tasks SET done = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    updated = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return jsonify(task_to_dict(updated))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
