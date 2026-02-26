from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app, activities


client = TestClient(app)


def test_get_activities_returns_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # known keys present
    assert "Chess Club" in data
    # all activity entries contain expected fields
    for name, details in data.items():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details


def test_post_signup_adds_participant_and_prevents_duplicates():
    activity = "Basketball Club"
    test_email = "test.add@example.com"

    url = f"/activities/{quote(activity)}/signup?email={quote(test_email)}"

    # First signup should succeed
    r1 = client.post(url)
    assert r1.status_code == 200
    assert test_email in activities[activity]["participants"]

    # Second signup same email should be rejected
    r2 = client.post(url)
    assert r2.status_code == 400
    assert r2.json().get("detail") == "Student is already signed up for this activity"

    # Ensure only one instance in participants list
    assert activities[activity]["participants"].count(test_email) == 1


def test_delete_participant_removes_and_handles_missing():
    activity = "Basketball Club"
    test_email = "test.remove@example.com"

    # Ensure participant exists by signing up
    signup_url = f"/activities/{quote(activity)}/signup?email={quote(test_email)}"
    r_signed = client.post(signup_url)
    assert r_signed.status_code == 200
    assert test_email in activities[activity]["participants"]

    # Delete existing participant
    del_url = f"/activities/{quote(activity)}/participants?email={quote(test_email)}"
    r_del = client.delete(del_url)
    assert r_del.status_code == 200
    assert test_email not in activities[activity]["participants"]

    # Deleting again should return 404
    r_del2 = client.delete(del_url)
    assert r_del2.status_code == 404
    assert r_del2.json().get("detail") == "Participant not found in this activity"
