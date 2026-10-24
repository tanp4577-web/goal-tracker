import pytest
from app import (app, reset_goals, add_goal, update_goal, find_goal, parse_progress,
                 status_for_progress, build_summary)


@pytest.fixture(autouse=True)
def clean_state():
    reset_goals()


@pytest.fixture
def client():
    return app.test_client()


@pytest.mark.parametrize("progress, expected", [
    (0, "Not Started"),
    (1, "In Progress"),
    (50, "In Progress"),
    (99, "In Progress"),
    (100, "Completed"),
])
def test_status_for_progress(progress, expected):
    assert status_for_progress(progress) == expected


@pytest.mark.parametrize("value, expected", [
    (0, 0),
    ("40", 40),
    (72.6, 73),
    (100, 100),
])
def test_parse_progress_accepts_valid_values(value, expected):
    assert parse_progress(value) == expected


@pytest.mark.parametrize("value", [-1, 101, "abc", "", True])
def test_parse_progress_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        parse_progress(value)


def test_update_goal_sets_progress_status_and_deadline():
    goal = add_goal("Learn Jenkins")
    updated = update_goal(goal["id"], "Learn Jenkins", "", "2026-11-30", "60")
    assert updated["progress"] == 60
    assert updated["status"] == "In Progress"
    assert updated["deadline"] == "2026-11-30"


def test_invalid_progress_changes_nothing():
    goal = add_goal("Keep me")
    with pytest.raises(ValueError):
        update_goal(goal["id"], "Changed", "", None, "150")
    assert goal["title"] == "Keep me"
    assert goal["progress"] == 0


def test_update_unknown_goal_raises_lookup_error():
    with pytest.raises(LookupError):
        update_goal(999, "x", "", None, "10")


def test_summary_for_empty_list():
    assert build_summary()["overallProgress"] == 0


def test_summary_counts_and_average():
    a = add_goal("A")
    b = add_goal("B")
    add_goal("C")
    update_goal(a["id"], "A", "", None, "100")
    update_goal(b["id"], "B", "", None, "50")
    summary = build_summary()
    assert (summary["total"], summary["completed"],
            summary["inProgress"], summary["notStarted"]) == (3, 1, 1, 1)
    assert summary["overallProgress"] == 50


def test_add_and_update_through_the_forms(client):
    client.post("/add", data={"title": "Ship v3", "description": "", "deadline": "2026-12-01"})
    goal = find_goal(1)
    assert goal["deadline"] == "2026-12-01"
    resp = client.post("/edit/1", data={"title": "Ship v3", "description": "",
                                        "deadline": "2026-12-01", "progress": "100"},
                       follow_redirects=True)
    assert resp.status_code == 200
    assert b"Completed - 100%" in resp.data
    assert b"Overall progress: 100%" in resp.data


def test_edit_with_invalid_progress_returns_400(client):
    add_goal("Write report")
    resp = client.post("/edit/1", data={"title": "Write report", "description": "",
                                        "deadline": "", "progress": "150"})
    assert resp.status_code == 400


def test_edit_unknown_goal_returns_404(client):
    assert client.get("/edit/999").status_code == 404
