import pytest
import requests
import secrets

class TestAuth:
    """Authentication endpoint tests"""

    def test_login_success(self, base_url, api_client):
        """Test admin login with correct credentials"""
        response = api_client.post(f"{base_url}/api/auth/login", json={
            "email": "admin@footup.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user_id" in data
        assert data["email"] == "admin@footup.com"
        assert data["role"] == "coach"

    def test_login_invalid_credentials(self, base_url, api_client):
        """Test login with wrong password"""
        response = api_client.post(f"{base_url}/api/auth/login", json={
            "email": "admin@footup.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_login_nonexistent_user(self, base_url, api_client):
        """Test login with non-existent email"""
        response = api_client.post(f"{base_url}/api/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        assert response.status_code == 401

    def test_register_new_user(self, base_url, api_client):
        """Test user registration with unique email"""
        unique_email = f"TEST_user_{secrets.token_hex(8)}@example.com"
        response = api_client.post(f"{base_url}/api/auth/register", json={
            "email": unique_email,
            "password": "testpass123",
            "name": "Test User"
        })
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "user_id" in data
        assert data["email"] == unique_email.lower()
        assert data["name"] == "Test User"
        assert data["role"] == "player"

    def test_register_duplicate_email(self, base_url, api_client):
        """Test registration with existing email fails"""
        response = api_client.post(f"{base_url}/api/auth/register", json={
            "email": "admin@footup.com",
            "password": "testpass123",
            "name": "Duplicate User"
        })
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    def test_get_me_authenticated(self, base_url, api_client, auth_headers):
        """Test /auth/me with valid token"""
        response = api_client.get(f"{base_url}/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "user_id" in data
        assert "_id" not in data
        assert "password_hash" not in data

    def test_get_me_unauthenticated(self, base_url, api_client):
        """Test /auth/me without token returns 401"""
        response = api_client.get(f"{base_url}/api/auth/me")
        assert response.status_code == 401

    def test_logout(self, base_url, api_client):
        """Test logout endpoint"""
        response = api_client.post(f"{base_url}/api/auth/logout")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
