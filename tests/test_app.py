import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the activities dict to its original state after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all():
    # Arrange — default in-memory data has 9 activities including "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()


def test_get_activities_contains_expected_fields():
    # Arrange — no setup needed; using default data

    # Act
    activity = client.get("/activities").json()["Chess Club"]

    # Assert
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_signup_adds_participant():
    # Arrange
    email = "new@mergington.edu"

    # Act
    client.post("/activities/Chess Club/signup", params={"email": email})

    # Assert
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert email in participants


def test_signup_activity_not_found():
    # Arrange
    email = "student@mergington.edu"

    # Act
    response = client.post("/activities/Nonexistent Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_already_registered():
    # Arrange — "michael@mergington.edu" is pre-seeded in Chess Club

    # Act
    response = client.post("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success():
    # Arrange — "michael@mergington.edu" is pre-seeded in Chess Club

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})

    # Assert
    assert response.status_code == 200
    assert "michael@mergington.edu" in response.json()["message"]


def test_unregister_removes_participant():
    # Arrange — "michael@mergington.edu" is pre-seeded in Chess Club

    # Act
    client.delete("/activities/Chess Club/signup", params={"email": "michael@mergington.edu"})

    # Assert
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert "michael@mergington.edu" not in participants


def test_unregister_activity_not_found():
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete("/activities/Nonexistent Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_not_signed_up():
    # Arrange
    email = "nobody@mergington.edu"

    # Act
    response = client.delete("/activities/Chess Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up for this activity"
