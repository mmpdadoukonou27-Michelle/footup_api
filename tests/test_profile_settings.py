import pytest
import requests

class TestProfile:
    """Profile endpoint tests"""

    def test_get_profile_authenticated(self, base_url, api_client, auth_headers):
        """Test getting user profile"""
        response = api_client.get(f"{base_url}/api/profile", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        assert "name" in data
        assert "_id" not in data
        assert "password_hash" not in data

    def test_get_profile_unauthenticated(self, base_url, api_client):
        """Test getting profile without token fails"""
        response = api_client.get(f"{base_url}/api/profile")
        assert response.status_code == 401

    def test_update_profile_authenticated(self, base_url, api_client, auth_headers):
        """Test updating user profile"""
        update_data = {
            "name": "Updated Name",
            "age": 25,
            "club": "Test FC",
            "position": "Midfielder"
        }
        response = api_client.put(f"{base_url}/api/profile", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["age"] == 25
        assert data["club"] == "Test FC"
        assert data["position"] == "Midfielder"
        assert "_id" not in data

    def test_update_profile_unauthenticated(self, base_url, api_client):
        """Test updating profile without token fails"""
        response = api_client.put(f"{base_url}/api/profile", json={"name": "Test"})
        assert response.status_code == 401


class TestSettings:
    """Settings endpoint tests"""

    def test_get_settings_authenticated(self, base_url, api_client, auth_headers):
        """Test getting user settings"""
        response = api_client.get(f"{base_url}/api/settings", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "theme" in data
        assert "language" in data
        assert "units" in data

    def test_get_settings_unauthenticated(self, base_url, api_client):
        """Test getting settings without token fails"""
        response = api_client.get(f"{base_url}/api/settings")
        assert response.status_code == 401

    def test_update_settings_authenticated(self, base_url, api_client, auth_headers):
        """Test updating user settings"""
        update_data = {
            "theme": "light",
            "language": "en",
            "units": "imperial"
        }
        response = api_client.put(f"{base_url}/api/settings", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "light"
        assert data["language"] == "en"
        assert data["units"] == "imperial"

    def test_update_settings_unauthenticated(self, base_url, api_client):
        """Test updating settings without token fails"""
        response = api_client.put(f"{base_url}/api/settings", json={"theme": "light"})
        assert response.status_code == 401
