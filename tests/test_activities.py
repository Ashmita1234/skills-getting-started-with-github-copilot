import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.app import app

client = TestClient(app)


class TestActivities:
    """Tests for activity endpoints"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        
        # Verify structure
        assert isinstance(activities, dict)
        assert "Tennis Club" in activities
        assert "Basketball Team" in activities
        
        # Verify activity structure
        tennis = activities["Tennis Club"]
        assert "description" in tennis
        assert "schedule" in tennis
        assert "max_participants" in tennis
        assert "participants" in tennis
        assert isinstance(tennis["participants"], list)

    def test_activities_have_participants(self):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        
        # Check specific activities have participants
        assert len(activities["Tennis Club"]["participants"]) > 0
        assert len(activities["Basketball Team"]["participants"]) > 0

    def test_activity_not_found(self):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"

    def test_signup_for_activity(self):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Drama Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert "newstudent@mergington.edu" in result["message"]

    def test_signup_duplicate_email(self):
        """Test that duplicate signup returns error"""
        email = "duplicate@mergington.edu"
        
        # Sign up once
        response1 = client.post(
            "/activities/Art Studio/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Try to sign up again
        response2 = client.post(
            "/activities/Art Studio/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_root_redirect(self):
        """Test that root redirects to index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307

    def test_activity_details(self):
        """Test that activity details are correct"""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        
        # Test Tennis Club details
        tennis = activities["Tennis Club"]
        assert tennis["max_participants"] == 16
        assert "tennis" in tennis["description"].lower()
        
        # Test Basketball Team details
        basketball = activities["Basketball Team"]
        assert basketball["max_participants"] == 15
        assert len(basketball["participants"]) >= 2

    def test_multiple_signups_different_users(self):
        """Test signing up multiple different users for an activity"""
        emails = [
            "user1@test.mergington.edu",
            "user2@test.mergington.edu",
            "user3@test.mergington.edu"
        ]
        
        for email in emails:
            response = client.post(
                "/activities/Gym Class/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all are signed up
        response = client.get("/activities")
        participants = response.json()["Gym Class"]["participants"]
        for email in emails:
            assert email in participants

    def test_signup_updates_participant_count(self):
        """Test that signup updates participant count"""
        response = client.get("/activities")
        initial_count = len(response.json()["Programming Class"]["participants"])
        
        # Sign up new participant
        client.post(
            "/activities/Programming Class/signup",
            params={"email": "countest@mergington.edu"}
        )
        
        # Verify count increased
        response = client.get("/activities")
        new_count = len(response.json()["Programming Class"]["participants"])
        assert new_count == initial_count + 1
