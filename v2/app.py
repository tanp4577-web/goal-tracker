from contextlib import contextmanager
import os
import sqlite3
from pathlib import Path

from flask import Flask, request, redirect, url_for, render_template, abort
app = Flask(__name__)
VERSION = "v2"
FEATURES = "Add Goal, Update Goal"
STATUSES = ["Not Started", "In Progress", "Completed"]
DATABASE = Path(os.environ.get("GOAL_TRACKER_DB", Path(__file__).parent / "instance" / "goals.sqlite3"))
DATABASE.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def connect_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def load_goals():
    with connect_db() as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL
            )"""
        )
        rows = connection.execute(
            "SELECT id, title, description, status FROM goals ORDER BY id"
        ).fetchall()
    return [dict(row) for row in rows]


goals = load_goals()


def reset_goals():
    """Clear all goals (used by the tests)."""
    goals.clear()
    with connect_db() as connection:
        connection.execute("DELETE FROM goals")
        connection.execute("DELETE FROM sqlite_sequence WHERE name = 'goals'")


def is_valid_title(title):
    """A title is valid when it is a non-empty string."""
    return isinstance(title, str) and title.strip() != ""


def add_goal(title, description=""):
    """Create a goal with the status 'Not Started'."""
    if not is_valid_title(title):
        raise ValueError("title is required")
    with connect_db() as connection:
        cursor = connection.execute(
            "INSERT INTO goals (title, description, status) VALUES (?, ?, ?)",
            (title.strip(), description.strip(), "Not Started"),
        )
        goal = {
            "id": cursor.lastrowid,
            "title": title.strip(),
            "description": description.strip(),
            "status": "Not Started",
        }
    goals.append(goal)
    return goals[-1]


def find_goal(goal_id):
    return next((g for g in goals if g["id"] == goal_id), None)


def update_goal(goal_id, title, description, status):
    """Change a goal. Everything is checked before anything is changed."""
    goal = find_goal(goal_id)
    if goal is None:
        raise LookupError("goal not found")
    if not is_valid_title(title):
        raise ValueError("title cannot be empty")
    if status not in STATUSES:
        raise ValueError("invalid status")
    with connect_db() as connection:
        connection.execute(
            "UPDATE goals SET title = ?, description = ?, status = ? WHERE id = ?",
            (title.strip(), description.strip(), status, goal_id),
        )
    goal.update(title=title.strip(), description=description.strip(), status=status)
    return goal


def render(**extra):
    ctx = {"version": VERSION, "features": FEATURES, "goal": {}, "error": None, **extra}
    return render_template("index.html", **ctx)


@app.route("/")
def index():
    return render(page="home", goals=list(reversed(goals)), action="/add")


@app.route("/add", methods=["POST"])
def add():
    try:
        add_goal(request.form.get("title", ""), request.form.get("description", ""))
    except ValueError:
        pass
    return redirect(url_for("index"))


@app.route("/edit/<int:goal_id>", methods=["GET", "POST"])
def edit(goal_id):
    goal = find_goal(goal_id)
    if goal is None:
        abort(404)
    error = None
    if request.method == "POST":
        f = request.form
        try:
            update_goal(goal_id, f.get("title", ""), f.get("description", ""),
                        f.get("status", goal["status"]))
            return redirect(url_for("index"))
        except ValueError as err:
            error = str(err)
    return render(page="edit", goal=goal, statuses=STATUSES, error=error, action=""), (400 if error else 200)


@app.route("/health")
def health():
    return {"status": "ok", "version": VERSION}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
