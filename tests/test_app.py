"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to a known state before each test"""
    # Save original state
    from app import activities
    original_state = {k: {"participants": v["participants"].copy()} for k, v in activities.items()}
    
    yield
    
    # Restore original state
    for activity_name, activity_data in activities.items():
        activity_data["participants"] = original_state[activity_name]["participants"]


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test successfully retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_activities_have_required_fields(self, client):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, reset_activities):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant to the list"""
        # Get initial participants count
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before["Chess Club"]["participants"])
        
        # Sign up
        client.post("/activities/Chess Club/signup?email=newuser@mergington.edu")
        
        # Check participants count increased
        activities_after = client.get("/activities").json()
        new_count = len(activities_after["Chess Club"]["participants"])
        
        assert new_count == initial_count + 1
        assert "newuser@mergington.edu" in activities_after["Chess Club"]["participants"]

    def test_signup_duplicate_prevention(self, client, reset_activities):
        """Test that duplicate signups are prevented"""
        email = "duplicate@mergington.edu"
        
        # First signup
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup with same email
        response2 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify only one entry exists
        activities = client.get("/activities").json()
        count = activities["Chess Club"]["participants"].count(email)
        assert count == 1

    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_various_activities(self, client, reset_activities):
        """Test signing up for different activities"""
        email = "student@mergington.edu"
        activities_to_test = ["Chess Club", "Programming Class", "Gym Class"]
        
        for activity in activities_to_test:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/remove endpoint"""

    def test_remove_participant_success(self, client, reset_activities):
        """Test successfully removing a participant"""
        email = "remove-me@mergington.edu"
        
        # First sign up
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Then remove
        response = client.delete(
            f"/activities/Chess Club/remove?email={email}"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]

    def test_remove_participant_actually_removes(self, client, reset_activities):
        """Test that participant is actually removed from the list"""
        email = "test-remove@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Chess Club/signup?email={email}")
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        
        # Remove
        client.delete(f"/activities/Chess Club/remove?email={email}")
        activities = client.get("/activities").json()
        assert email not in activities["Chess Club"]["participants"]

    def test_remove_nonexistent_participant(self, client):
        """Test removing a participant that doesn't exist"""
        response = client.delete(
            "/activities/Chess Club/remove?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_from_nonexistent_activity(self, client):
        """Test removing from a non-existent activity"""
        response = client.delete(
            "/activities/Nonexistent Club/remove?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRootRedirect:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that / redirects to the static HTML"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
