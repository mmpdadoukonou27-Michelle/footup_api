import pytest
import requests

class TestBadges:
    """Badges endpoint tests"""

    def test_get_badges_authenticated(self, base_url, api_client, auth_headers):
        """Test getting badges list"""
        response = api_client.get(f"{base_url}/api/badges", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 5
        
        # Verify badge structure
        for badge in data:
            assert "id" in badge
            assert "title" in badge
            assert "description" in badge
            assert "icon" in badge
            assert "earned" in badge
            assert "_id" not in badge

    def test_get_badges_unauthenticated(self, base_url, api_client):
        """Test getting badges without token fails"""
        response = api_client.get(f"{base_url}/api/badges")
        assert response.status_code == 401


class TestLeaderboard:
    """Leaderboard endpoint tests"""

    def test_get_leaderboard_authenticated(self, base_url, api_client, auth_headers):
        """Test getting leaderboard"""
        response = api_client.get(f"{base_url}/api/leaderboard", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Verify leaderboard structure
        for entry in data:
            assert "user_id" in entry
            assert "name" in entry
            assert "total_score" in entry
            assert "rank" in entry
            assert "_id" not in entry

    def test_get_leaderboard_with_region_filter(self, base_url, api_client, auth_headers):
        """Test getting leaderboard with region filter"""
        response = api_client.get(f"{base_url}/api/leaderboard?region=Île-de-France", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_leaderboard_unauthenticated(self, base_url, api_client):
        """Test getting leaderboard without token fails"""
        response = api_client.get(f"{base_url}/api/leaderboard")
        assert response.status_code == 401
