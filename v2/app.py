from flask import Flask, request, redirect, url_for, render_template, abort
app = Flask(__name__)
VERSION = "v2"
FEATURES = "Add Goal, Update Goal"
STATUSES = ["Not Started", "In Progress", "Completed"]
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
    """Create a goal with the status 'Not Started'."""
    global next_id
    if not is_valid_title(title):
        raise ValueError("title is required")
    goals.append({"id": next_id, "title": title.strip(),
                  "description": description.strip(), "status": "Not Started"})
    next_id += 1
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
    app.run(host="0.0.0.0", port=5000)
