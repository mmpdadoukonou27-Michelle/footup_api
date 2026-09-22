import pytest
import requests

class TestSessions:
    """Session CRUD tests"""

    def test_create_session_authenticated(self, base_url, api_client, auth_headers):
        """Test creating a session with valid token"""
        session_data = {
            "successful_shots": 15,
            "precision": 75.5,
            "avg_latency": 0.45,
            "duration_seconds": 120,
            "zone_top_left": 30.0,
            "zone_center": 50.0,
            "zone_bottom_right": 20.0
        }
        response = api_client.post(f"{base_url}/api/sessions", json=session_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["successful_shots"] == 15
        assert data["precision"] == 75.5
        assert data["avg_latency"] == 0.45
        assert data["duration_seconds"] == 120
        assert "_id" not in data

    def test_create_session_unauthenticated(self, base_url, api_client):
        """Test creating session without token fails"""
        session_data = {
            "successful_shots": 10,
            "precision": 80.0,
            "avg_latency": 0.5,
            "duration_seconds": 60
        }
        response = api_client.post(f"{base_url}/api/sessions", json=session_data)
        assert response.status_code == 401

    def test_get_sessions_authenticated(self, base_url, api_client, auth_headers):
        """Test getting user sessions"""
        response = api_client.get(f"{base_url}/api/sessions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_sessions_unauthenticated(self, base_url, api_client):
        """Test getting sessions without token fails"""
        response = api_client.get(f"{base_url}/api/sessions")
        assert response.status_code == 401
