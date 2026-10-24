from flask import Flask, request, redirect, url_for, render_template, abort

app = Flask(__name__)

VERSION = "v3"
FEATURES = "Add Goal, Update Goal, View Progress"
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


def parse_progress(value):
    """Convert a value to a whole number from 0 to 100."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError("progress must be a number from 0 to 100")
    if isinstance(value, bool) or not 0 <= number <= 100:
        raise ValueError("progress must be a number from 0 to 100")
    return round(number)


def status_for_progress(progress):
    """0 -> Not Started, 1 to 99 -> In Progress, 100 -> Completed."""
    return "Completed" if progress >= 100 else "In Progress" if progress > 0 else "Not Started"


def add_goal(title, description="", deadline=None):
    global next_id
    if not is_valid_title(title):
        raise ValueError("title is required")
    goals.append({"id": next_id, "title": title.strip(), "description": description.strip(),
                  "deadline": deadline or None, "progress": 0, "status": "Not Started"})
    next_id += 1
    return goals[-1]


def find_goal(goal_id):
    return next((g for g in goals if g["id"] == goal_id), None)


def update_goal(goal_id, title, description, deadline, progress):
    """Change a goal. The status is worked out from the progress."""
    goal = find_goal(goal_id)
    if goal is None:
        raise LookupError("goal not found")
    if not is_valid_title(title):
        raise ValueError("title cannot be empty")
    value = parse_progress(progress)
    goal.update(title=title.strip(), description=description.strip(),
                deadline=deadline or None, progress=value, status=status_for_progress(value))
    return goal


def build_summary():
    """Totals and overall progress for the dashboard."""
    total = len(goals)
    done = sum(g["status"] == "Completed" for g in goals)
    working = sum(g["status"] == "In Progress" for g in goals)
    overall = round(sum(g["progress"] for g in goals) / total) if total else 0
    return {"total": total, "completed": done, "inProgress": working,
            "notStarted": total - done - working, "overallProgress": overall}


def render(**extra):
    ctx = {"version": VERSION, "features": FEATURES, "goal": {}, "error": None, **extra}
    return render_template("index.html", **ctx)


@app.route("/")
def index():
    return render(page="home", goals=list(reversed(goals)), summary=build_summary(), action="/add")


@app.route("/add", methods=["POST"])
def add():
    f = request.form
    try:
        add_goal(f.get("title", ""), f.get("description", ""), f.get("deadline"))
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
                        f.get("deadline"), f.get("progress", goal["progress"]))
            return redirect(url_for("index"))
        except ValueError as err:
            error = str(err)
    return render(page="edit", goal=goal, error=error, action=""), (400 if error else 200)


@app.route("/health")
def health():
    return {"status": "ok", "version": VERSION}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
