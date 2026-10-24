from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)

VERSION = "v1"
FEATURES = "Add Goal"
goals = []
next_id = 1


def reset_goals():
    """Clear all goals (used by the tests)."""
    global next_id
    goals.clear()
    next_id = 1


def is_valid_title(title):
    """A title is valid when it is a non-empty string."""
    return isinstance(title, str) and title.strip() != ""


def add_goal(title, description=""):
    """Create a goal and store it. Raises ValueError for an empty title."""
    global next_id
    if not is_valid_title(title):
        raise ValueError("title is required")
    goals.append({"id": next_id, "title": title.strip(), "description": description.strip()})
    next_id += 1
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
    app.run(host="0.0.0.0", port=5000)