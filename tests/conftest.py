import pytest
import requests
import os
from pathlib import Path

@pytest.fixture(scope="session")
def base_url():
    """Get base URL from environment or frontend .env file"""
    url = os.environ.get('EXPO_PUBLIC_BACKEND_URL', '').rstrip('/')
    if not url:
        # Try reading from frontend/.env
        env_file = Path('/app/frontend/.env')
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith('EXPO_PUBLIC_BACKEND_URL='):
                    url = line.split('=', 1)[1].strip().strip('"').rstrip('/')
                    break
    if not url:
        pytest.fail("EXPO_PUBLIC_BACKEND_URL not found in environment or frontend/.env")
    return url

@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session

@pytest.fixture
def admin_token(base_url, api_client):
    """Get admin token for authenticated requests"""
    response = api_client.post(f"{base_url}/api/auth/login", json={
        "email": "admin@footup.com",
        "password": "admin123"
    })
    if response.status_code != 200:
        pytest.skip(f"Admin login failed: {response.status_code}")
    return response.json().get("token")

@pytest.fixture
def auth_headers(admin_token):
    """Headers with admin token"""
    return {"Authorization": f"Bearer {admin_token}"}
