import pytest
from app import (app, reset_goals, is_valid_title, add_goal, update_goal,
                 find_goal, load_goals, STATUSES)


@pytest.fixture(autouse=True)
def clean_state():
    reset_goals()


@pytest.fixture
def client():
    return app.test_client()


@pytest.mark.parametrize("title, expected", [
    ("Learn Docker", True),
    ("", False),
    ("   ", False),
    (None, False),
])
def test_is_valid_title(title, expected):
    assert is_valid_title(title) == expected


def test_new_goal_starts_as_not_started():
    assert add_goal("Learn Kubernetes")["status"] == "Not Started"


def test_goal_and_edits_are_saved_persistently():
    goal = add_goal("Persistent goal", "before")
    update_goal(goal["id"], "Persistent goal", "after", "In Progress")
    assert load_goals() == [
        {
            "id": 1,
            "title": "Persistent goal",
            "description": "after",
            "status": "In Progress",
        }
    ]


@pytest.mark.parametrize("status", STATUSES)
def test_update_goal_accepts_every_status(status):
    goal = add_goal("Learn Kubernetes")
    updated = update_goal(goal["id"], "Learn Kubernetes", "", status)
    assert updated["status"] == status


def test_update_goal_changes_title_and_description():
    goal = add_goal("Old title", "old")
    updated = update_goal(goal["id"], " New title ", "new", "In Progress")
    assert (updated["title"], updated["description"]) == ("New title", "new")


@pytest.mark.parametrize("title, status", [
    ("", "In Progress"),
    ("   ", "In Progress"),
    ("Valid title", "Done"),
])
def test_update_goal_rejects_bad_input(title, status):
    goal = add_goal("Keep me")
    with pytest.raises(ValueError):
        update_goal(goal["id"], title, "", status)
    assert goal["title"] == "Keep me"
    assert goal["status"] == "Not Started"


def test_update_unknown_goal_raises_lookup_error():
    with pytest.raises(LookupError):
        update_goal(999, "x", "", "Completed")


def test_edit_page_opens_with_old_values(client):
    goal = add_goal("Write report", "first draft")
    resp = client.get(f"/edit/{goal['id']}")
    assert resp.status_code == 200
    assert b"Write report" in resp.data and b"first draft" in resp.data


def test_edit_through_the_form(client):
    goal = add_goal("Write report")
    resp = client.post(f"/edit/{goal['id']}",
                       data={"title": "Write final report", "description": "",
                             "status": "In Progress"},
                       follow_redirects=True)
    assert resp.status_code == 200
    assert find_goal(goal["id"])["title"] == "Write final report"
    assert find_goal(goal["id"])["status"] == "In Progress"


def test_edit_with_empty_title_returns_400(client):
    goal = add_goal("Write report")
    resp = client.post(f"/edit/{goal['id']}",
                       data={"title": "", "description": "", "status": "Completed"})
    assert resp.status_code == 400


def test_edit_unknown_goal_returns_404(client):
    assert client.get("/edit/999").status_code == 404
