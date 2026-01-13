import os
import sys
import uuid

# Ensure src is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_PATH = os.path.join(ROOT, "src")
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

from fastapi.testclient import TestClient
from app import app, activities


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Expect some known activity keys exist
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    # create a temporary activity to avoid colliding with existing state
    activity_name = f"Autotest Club {uuid.uuid4().hex[:6]}"
    activities[activity_name] = {
        "description": "Temporary activity for tests",
        "schedule": "Now",
        "max_participants": 10,
        "participants": []
    }

    email = f"testuser+{uuid.uuid4().hex[:6]}@example.com"

    # Sign up
    resp = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Verify participant present
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert email in data[activity_name]["participants"]

    # Unregister
    resp = client.delete(f"/activities/{activity_name}/participants", params={"email": email})
    assert resp.status_code == 200
    body = resp.json()
    assert "Unregistered" in body.get("message", "")

    # Verify removed
    resp = client.get("/activities")
    data = resp.json()
    assert email not in data[activity_name]["participants"]

    # Cleanup
    del activities[activity_name]
