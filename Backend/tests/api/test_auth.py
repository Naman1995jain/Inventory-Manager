"""
Test module for authentication endpoints
Tests registration, login, token validation, and security features
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import User
from app.core.security import verify_password


class TestAuthentication:
    """Test class for authentication endpoints"""

    def test_register_user_success(self, client: TestClient, db_session: Session):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@example.com",
            "password": "strongpassword123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Password should not be returned
        
        # Verify user was created in database
        user = db_session.query(User).filter(User.email == user_data["email"]).first()
        assert user is not None
        assert user.email == user_data["email"]

    def test_register_user_duplicate_email(self, client: TestClient, test_user: User):
        """Test registration with existing email fails"""
        user_data = {
            "email": test_user.email,
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already registered" in response.json()["detail"].lower()

    def test_register_user_invalid_email(self, client: TestClient):
        """Test registration with invalid email format"""
        user_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_weak_password(self, client: TestClient):
        """Test registration with weak password"""
        user_data = {
            "email": "newuser@example.com",
            "password": "123"  # Too short
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login"""
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_invalid_email(self, client: TestClient):
        """Test login with non-existent email"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect email or password" in response.json()["detail"].lower()

    def test_login_invalid_password(self, client: TestClient, test_user: User):
        """Test login with incorrect password"""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect email or password" in response.json()["detail"].lower()

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing required fields"""
        # Missing password
        response = client.post("/api/v1/auth/login", json={"email": "test@example.com"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Missing email
        response = client.post("/api/v1/auth/login", json={"password": "password123"})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        
        # Empty payload
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_password_hashing(self, test_user: User):
        """Test that passwords are properly hashed"""
        # Password should be hashed, not stored in plain text
        assert test_user.hashed_password != "testpassword123"
        assert test_user.hashed_password.startswith("$2b$")  # bcrypt format
        
        # Verify password verification works
        assert verify_password("testpassword123", test_user.hashed_password)
        assert not verify_password("wrongpassword", test_user.hashed_password)


class TestAuthenticationSecurity:
    """Test class for authentication security features"""

    def test_token_contains_user_info(self, client: TestClient, test_user: User):
        """Test that JWT token contains necessary user information"""
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        token = response.json()["access_token"]
        
        # Decode token to verify contents (for testing purposes)
        from jose import jwt
        from app.core.config import settings
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == test_user.email
        assert payload["user_id"] == test_user.id
        assert "exp" in payload  # Token should have expiration

    def test_concurrent_registrations(self, client: TestClient):
        """Test handling of concurrent user registrations"""
        user_data = {
            "email": "concurrent@example.com",
            "password": "password123"
        }
        
        # Simulate concurrent registration attempts
        response1 = client.post("/api/v1/auth/register", json=user_data)
        response2 = client.post("/api/v1/auth/register", json=user_data)
        
        # One should succeed, one should fail
        responses = [response1, response2]
        success_count = sum(1 for r in responses if r.status_code == status.HTTP_201_CREATED)
        failure_count = sum(1 for r in responses if r.status_code == status.HTTP_400_BAD_REQUEST)
        
        assert success_count == 1
        assert failure_count == 1

    def test_login_rate_limiting_simulation(self, client: TestClient, test_user: User):
        """Test multiple failed login attempts (simulating rate limiting)"""
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }
        
        # Simulate multiple failed attempts
        failed_attempts = []
        for _ in range(5):
            response = client.post("/api/v1/auth/login", json=login_data)
            failed_attempts.append(response.status_code)
        
        # All should fail with 401
        assert all(status_code == status.HTTP_401_UNAUTHORIZED for status_code in failed_attempts)

    def test_sql_injection_protection(self, client: TestClient):
        """Test protection against SQL injection in login"""
        malicious_data = {
            "email": "admin@example.com'; DROP TABLE users; --",
            "password": "password"
        }
        
        response = client.post("/api/v1/auth/login", json=malicious_data)
        
        # Should fail safely, not cause server error
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_xss_protection_in_registration(self, client: TestClient):
        """Test protection against XSS in user registration"""
        malicious_data = {
            "email": "<script>alert('xss')</script>@example.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/register", json=malicious_data)
        
        # Should either fail validation or sanitize input
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]

    def test_email_case_insensitive(self, client: TestClient, test_user: User):
        """Test that email authentication is case-insensitive"""
        login_data = {
            "email": test_user.email.upper(),  # Use uppercase email
            "password": "testpassword123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        # Should still authenticate successfully
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()