"""
Test suite for Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities data before each test"""
    # Store original data
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        }
    }
    
    # Reset to original state
    activities.clear()
    activities.update(original_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/")
        assert response.status_code == 200
        # Should redirect to static files


class TestActivitiesEndpoint:
    """Test the activities endpoint"""
    
    def test_get_activities_success(self, client, reset_activities):
        """Test getting all activities successfully"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        
    def test_activities_have_required_fields(self, client, reset_activities):
        """Test that all activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupEndpoint:
    """Test the signup functionality"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify student was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post("/activities/Nonexistent Club/signup?email=student@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_signup_duplicate_registration(self, client, reset_activities):
        """Test that a student cannot register twice for the same activity"""
        # First signup should succeed
        response1 = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
        assert response1.status_code == 400
        data1 = response1.json()
        assert "already signed up" in data1["detail"].lower()
    
    def test_signup_multiple_different_activities(self, client, reset_activities):
        """Test that a student can register for multiple different activities"""
        email = "multistudent@mergington.edu"
        
        # Register for Chess Club
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        # Register for Programming Class
        response2 = client.post(f"/activities/Programming Class/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify registrations
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data["Chess Club"]["participants"]
        assert email in activities_data["Programming Class"]["participants"]
    
    def test_signup_with_special_characters_in_activity_name(self, client, reset_activities):
        """Test signup with URL encoding for activity names"""
        # Test with space in activity name
        response = client.post("/activities/Chess%20Club/signup?email=test@mergington.edu")
        assert response.status_code == 200


class TestUnregisterEndpoint:
    """Test the unregister functionality"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        # First, verify the student is registered
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]
        
        # Unregister
        response = client.delete("/activities/Chess Club/unregister?email=michael@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
        
        # Verify student was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.delete("/activities/Nonexistent Club/unregister?email=student@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
    
    def test_unregister_student_not_registered(self, client, reset_activities):
        """Test unregister student who is not registered"""
        response = client.delete("/activities/Chess Club/unregister?email=notregistered@mergington.edu")
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_with_special_characters(self, client, reset_activities):
        """Test unregister with URL encoding"""
        response = client.delete("/activities/Chess%20Club/unregister?email=michael@mergington.edu")
        assert response.status_code == 200


class TestDataIntegrity:
    """Test data integrity and edge cases"""
    
    def test_participant_count_accuracy(self, client, reset_activities):
        """Test that participant counts are accurate"""
        # Get initial state
        response = client.get("/activities")
        initial_data = response.json()
        initial_count = len(initial_data["Chess Club"]["participants"])
        
        # Add a participant
        client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
        
        # Check count increased
        response = client.get("/activities")
        new_data = response.json()
        new_count = len(new_data["Chess Club"]["participants"])
        assert new_count == initial_count + 1
        
        # Remove a participant
        client.delete("/activities/Chess Club/unregister?email=newstudent@mergington.edu")
        
        # Check count decreased
        response = client.get("/activities")
        final_data = response.json()
        final_count = len(final_data["Chess Club"]["participants"])
        assert final_count == initial_count
    
    def test_email_validation_in_urls(self, client, reset_activities):
        """Test that email parameters are handled correctly"""
        # Test with valid email
        response = client.post("/activities/Chess Club/signup?email=valid.email@mergington.edu")
        assert response.status_code == 200
        
        # The API should handle URL encoding properly
        response = client.post("/activities/Chess Club/signup?email=test%2Bemail@mergington.edu")
        assert response.status_code == 200


class TestAPIResponseFormat:
    """Test API response formats"""
    
    def test_success_response_format(self, client, reset_activities):
        """Test that success responses have correct format"""
        response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert isinstance(data["message"], str)
    
    def test_error_response_format(self, client, reset_activities):
        """Test that error responses have correct format"""
        response = client.post("/activities/Nonexistent/signup?email=test@mergington.edu")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)


# Integration tests
class TestWorkflowIntegration:
    """Test complete workflows"""
    
    def test_complete_signup_unregister_workflow(self, client, reset_activities):
        """Test complete workflow of signup and unregister"""
        email = "workflow@mergington.edu"
        activity = "Programming Class"
        
        # 1. Check initial state
        response = client.get("/activities")
        initial_data = response.json()
        assert email not in initial_data[activity]["participants"]
        
        # 2. Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # 3. Verify signup
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]
        
        # 4. Try to sign up again (should fail)
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400
        
        # 5. Unregister
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        
        # 6. Verify unregistration
        response = client.get("/activities")
        final_data = response.json()
        assert email not in final_data[activity]["participants"]
        
        # 7. Try to unregister again (should fail)
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 400