import pytest
import requests

class TestHealth:
    """Health check endpoint tests"""

    def test_health_check(self, base_url, api_client):
        """Test health endpoint returns 200"""
        response = api_client.get(f"{base_url}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
