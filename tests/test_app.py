from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)
_initial_activities = {k: v["participants"][:] for k, v in activities.items()}


def setup_function():
    for name, participant_list in _initial_activities.items():
        activities[name]["participants"] = participant_list[:]


def test_root_redirect():
    # Arrange
    # Act
    response = client.get("/", allow_redirects=False)
    # Assert
    assert response.status_code in (301, 302, 307, 308)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_for_activity_success():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    # Arrange
    activity = "Chess Club"
    existing = activities[activity]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity}/signup", params={"email": existing})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_unregister_for_activity_success():
    # Arrange
    activity = "Gym Class"
    email = "tempuser@mergington.edu"
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_not_signed_up():
    # Arrange
    activity = "Gym Class"
    email = "nobody@mergington.edu"
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Act
    response = client.delete(f"/activities/{activity}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up"
