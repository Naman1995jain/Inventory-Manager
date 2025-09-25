import pytest
from fastapi.testclient import TestClient
from app.models import User
from app.core.security import get_password_hash


@pytest.mark.integration
class TestAuthAPI:
    """Integration tests for authentication endpoints"""

    def test_register_user_success(self, client: TestClient, db_session):
        """Test successful user registration"""
        # Arrange
        user_data = {
            "email": "newuser@example.com",
            "password": "newpassword123"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "created_at" in data
        
        # Verify user was created in database
        db_user = db_session.query(User).filter(User.email == user_data["email"]).first()
        assert db_user is not None
        assert db_user.email == user_data["email"]

    def test_register_user_duplicate_email(self, client: TestClient, test_user):
        """Test user registration with duplicate email"""
        # Arrange
        user_data = {
            "email": test_user.email,
            "password": "somepassword123"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "Email already registered" in data["detail"]

    def test_register_user_invalid_email(self, client: TestClient):
        """Test user registration with invalid email"""
        # Arrange
        user_data = {
            "email": "invalid-email",
            "password": "password123"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 422

    def test_register_user_short_password(self, client: TestClient):
        """Test user registration with short password"""
        # Arrange
        user_data = {
            "email": "user@example.com",
            "password": "short"
        }

        # Act
        response = client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 422

    def test_login_success(self, client: TestClient, test_user):
        """Test successful user login"""
        # Arrange
        login_data = {
            "email": test_user.email,
            "password": "testpassword123"
        }

        # Act
        response = client.post("/api/v1/auth/login", json=login_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["access_token"] is not None

    def test_login_wrong_password(self, client: TestClient, test_user):
        """Test login with wrong password"""
        # Arrange
        login_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }

        # Act
        response = client.post("/api/v1/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "Incorrect email or password" in data["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user"""
        # Arrange
        login_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword"
        }

        # Act
        response = client.post("/api/v1/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "Incorrect email or password" in data["detail"]

    def test_login_invalid_email_format(self, client: TestClient):
        """Test login with invalid email format"""
        # Arrange
        login_data = {
            "email": "invalid-email",
            "password": "password123"
        }

        # Act
        response = client.post("/api/v1/auth/login", json=login_data)

        # Assert
        assert response.status_code == 422

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing fields"""
        # Test missing password
        response = client.post("/api/v1/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 422

        # Test missing email
        response = client.post("/api/v1/auth/login", json={"password": "password123"})
        assert response.status_code == 422

        # Test empty request
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

    def test_multiple_users_registration(self, client: TestClient, db_session):
        """Test registering multiple users"""
        # Arrange
        users_data = [
            {"email": "user1@example.com", "password": "password123"},
            {"email": "user2@example.com", "password": "password456"},
            {"email": "user3@example.com", "password": "password789"}
        ]

        # Act & Assert
        for user_data in users_data:
            response = client.post("/api/v1/auth/register", json=user_data)
            assert response.status_code == 201
            
            # Verify each user in database
            db_user = db_session.query(User).filter(User.email == user_data["email"]).first()
            assert db_user is not None

    def test_login_after_registration(self, client: TestClient):
        """Test login immediately after registration"""
        # Arrange
        user_data = {
            "email": "loginafter@example.com",
            "password": "testpassword123"
        }

        # Act - Register
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201

        # Act - Login
        login_response = client.post("/api/v1/auth/login", json=user_data)

        # Assert
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        assert login_data["token_type"] == "bearer"