from contextlib import contextmanager
import os
import sqlite3
from pathlib import Path

from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)

VERSION = "v1"
FEATURES = "Add Goal"
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
                description TEXT NOT NULL
            )"""
        )
        rows = connection.execute(
            "SELECT id, title, description FROM goals ORDER BY id"
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
    """Create a goal and store it. Raises ValueError for an empty title."""
    if not is_valid_title(title):
        raise ValueError("title is required")
    with connect_db() as connection:
        cursor = connection.execute(
            "INSERT INTO goals (title, description) VALUES (?, ?)",
            (title.strip(), description.strip()),
        )
        goal = {
            "id": cursor.lastrowid,
            "title": title.strip(),
            "description": description.strip(),
        }
    goals.append(goal)
    return goals[-1]


@app.route("/")
def index():
    return render_template("index.html", version=VERSION, features=FEATURES,
                           goals=list(reversed(goals)))


@app.route("/add", methods=["POST"])
def add():
    try:
        add_goal(request.form.get("title", ""), request.form.get("description", ""))
    except ValueError:
        pass
    return redirect(url_for("index"))


@app.route("/health")
def health():
    return {"status": "ok", "version": VERSION}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))