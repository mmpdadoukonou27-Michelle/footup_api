import pytest
import requests

class TestChallenges:
    """Challenge endpoint tests"""

    def test_get_challenges_authenticated(self, base_url, api_client, auth_headers):
        """Test getting challenges list"""
        response = api_client.get(f"{base_url}/api/challenges", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
        
        # Verify challenge structure
        for challenge in data:
            assert "id" in challenge
            assert "title" in challenge
            assert "description" in challenge
            assert "icon" in challenge
            assert "color" in challenge
            assert "type" in challenge
            assert "completed" in challenge
            assert "_id" not in challenge

    def test_get_challenges_unauthenticated(self, base_url, api_client):
        """Test getting challenges without token fails"""
        response = api_client.get(f"{base_url}/api/challenges")
        assert response.status_code == 401

    def test_complete_challenge_authenticated(self, base_url, api_client, auth_headers):
        """Test completing a challenge"""
        response = api_client.post(f"{base_url}/api/challenges/complete", 
                                   json={"challenge_id": "sprint_60s"}, 
                                   headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_complete_nonexistent_challenge(self, base_url, api_client, auth_headers):
        """Test completing non-existent challenge fails"""
        response = api_client.post(f"{base_url}/api/challenges/complete", 
                                   json={"challenge_id": "nonexistent_challenge"}, 
                                   headers=auth_headers)
        assert response.status_code == 404

    def test_complete_challenge_unauthenticated(self, base_url, api_client):
        """Test completing challenge without token fails"""
        response = api_client.post(f"{base_url}/api/challenges/complete", 
                                   json={"challenge_id": "sprint_60s"})
        assert response.status_code == 401
