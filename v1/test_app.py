import pytest
from app import app, goals, reset_goals, is_valid_title, add_goal, load_goals


@pytest.fixture(autouse=True)
def clean_state():
    reset_goals()


@pytest.fixture
def client():
    return app.test_client()


@pytest.mark.parametrize("title, expected", [
    ("Learn Docker", True),
    ("  Learn Kubernetes  ", True),
    ("", False),
    ("   ", False),
    (None, False),
])
def test_is_valid_title(title, expected):
    assert is_valid_title(title) == expected


@pytest.mark.parametrize("title, expected_title", [
    ("Learn Docker", "Learn Docker"),
    ("  Run Jenkins  ", "Run Jenkins"),
])
def test_add_goal_stores_trimmed_title(title, expected_title):
    goal = add_goal(title, "demo")
    assert goal["title"] == expected_title
    assert goal["id"] == 1


def test_goal_is_saved_persistently():
    add_goal("Persistent goal", "keep this")
    assert load_goals() == [
        {"id": 1, "title": "Persistent goal", "description": "keep this"}
    ]


def test_add_goal_rejects_empty_title():
    with pytest.raises(ValueError):
        add_goal("   ")


def test_add_goal_through_the_form(client):
    resp = client.post("/add", data={"title": "Finish DevOps project",
                                     "description": "three versions"},
                       follow_redirects=True)
    assert resp.status_code == 200
    assert b"Finish DevOps project" in resp.data


@pytest.mark.parametrize("title", ["", "   "])
def test_empty_title_is_not_saved(client, title):
    client.post("/add", data={"title": title}, follow_redirects=True)
    assert len(goals) == 0


def test_home_page_shows_version(client):
    assert b"Features: Add Goal" in client.get("/").data


def test_health_endpoint(client):
    assert client.get("/health").get_json()["version"] == "v1"
