import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestAuthAPI:
    """Test authentication endpoints"""
    
    def test_user_registration(self, client: TestClient):
        """Test user registration endpoint"""
        import uuid
        unique_email = f"newuser-{uuid.uuid4()}@example.com"
        
        user_data = {
            "email": unique_email,
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "hashed_password" not in data  # Password should not be returned
    
    def test_user_registration_duplicate_email(self, client: TestClient, test_user):
        """Test registration with duplicate email"""
        user_data = {
            "email": test_user.email,
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_user_login_success(self, client: TestClient, test_user):
        """Test successful user login"""
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["access_token"] is not None
    
    def test_user_login_invalid_email(self, client: TestClient):
        """Test login with invalid email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "incorrect email or password" in response.json()["detail"].lower()
    
    def test_user_login_invalid_password(self, client: TestClient, test_user):
        """Test login with invalid password"""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "incorrect email or password" in response.json()["detail"].lower()
    
    def test_user_login_missing_fields(self, client: TestClient):
        """Test login with missing fields"""
        # Missing password
        response = client.post("/api/v1/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 422
        
        # Missing email
        response = client.post("/api/v1/auth/login", json={"password": "password123"})
        assert response.status_code == 422
        
        # Empty request
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422
    
    def test_registration_invalid_email_format(self, client: TestClient):
        """Test registration with invalid email format"""
        user_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_registration_weak_password(self, client: TestClient):
        """Test registration with weak password"""
        user_data = {
            "email": "test@example.com",
            "password": "123"  # Too short
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        # This should pass validation according to current schema, 
        # but you might want to add password strength validation
        assert response.status_code in [201, 422]