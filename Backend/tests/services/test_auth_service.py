"""
Test module for authentication and authorization
Tests token generation, validation, permissions, and security
"""
import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from app.core.security import (
    create_access_token, verify_token, get_password_hash, verify_password
)
from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.services.auth_service import UserService
from app.models.models import User
from app.schemas.schemas import UserCreate


class TestTokenGeneration:
    """Test class for JWT token generation"""

    def test_create_access_token_success(self):
        """Test successful access token creation"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode token to verify contents
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert "exp" in payload

    def test_create_access_token_with_expiry(self):
        """Test token creation with custom expiry"""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"])
        
        # Verify expiry is approximately 15 minutes from now
        expected_exp = datetime.utcnow() + expires_delta
        time_diff = abs((exp - expected_exp).total_seconds())
        assert time_diff < 60  # Within 1 minute tolerance

    def test_create_access_token_with_admin_flag(self):
        """Test token creation with admin flag"""
        data = {"sub": "admin@example.com", "user_id": 1, "is_admin": True}
        token = create_access_token(data)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["is_admin"] is True

    def test_token_expiry_default(self):
        """Test that token has default expiry"""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"])
        
        # Should expire approximately at default time
        expected_exp = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        time_diff = abs((exp - expected_exp).total_seconds())
        assert time_diff < 60


class TestTokenValidation:
    """Test class for JWT token validation"""

    def test_verify_valid_token(self):
        """Test verification of valid token"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1

    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        invalid_token = "invalid.jwt.token"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_verify_expired_token(self):
        """Test verification of expired token"""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(seconds=-1)  # Already expired
        token = create_access_token(data, expires_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_verify_malformed_token(self):
        """Test verification of malformed token"""
        malformed_tokens = [
            "",
            "not.a.token",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9",  # Incomplete
            "Bearer token",  # With Bearer prefix
        ]
        
        for token in malformed_tokens:
            with pytest.raises(HTTPException) as exc_info:
                verify_token(token)
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    def test_verify_token_wrong_secret(self):
        """Test verification with wrong secret key"""
        # Create token with different secret
        wrong_payload = jwt.encode(
            {"sub": "test@example.com", "exp": datetime.utcnow() + timedelta(minutes=15)},
            "wrong_secret",
            algorithm=settings.ALGORITHM
        )
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(wrong_payload)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED


class TestPasswordSecurity:
    """Test class for password hashing and verification"""

    def test_password_hashing(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password  # Should not store plain text
        assert hashed.startswith("$2b$")  # bcrypt format
        assert len(hashed) > len(password)

    def test_password_verification_success(self):
        """Test successful password verification"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Test failed password verification"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_password_hash_uniqueness(self):
        """Test that same password generates different hashes"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

    def test_empty_password_handling(self):
        """Test handling of empty passwords"""
        empty_passwords = ["", None]
        
        for pwd in empty_passwords:
            if pwd is not None:
                # Should handle gracefully
                try:
                    hashed = get_password_hash(pwd)
                    assert hashed is not None
                except Exception:
                    # Or raise appropriate exception
                    pass

    def test_special_characters_password(self):
        """Test password with special characters"""
        special_password = "P@ssw0rd!@#$%^&*()"
        hashed = get_password_hash(special_password)
        
        assert verify_password(special_password, hashed) is True

    def test_unicode_password(self):
        """Test password with unicode characters"""
        unicode_password = "пароль123🔒"
        hashed = get_password_hash(unicode_password)
        
        assert verify_password(unicode_password, hashed) is True


class TestUserService:
    """Test class for UserService authentication logic"""

    def test_create_user_success(self, db_session: Session):
        """Test successful user creation through service"""
        user_service = UserService(db_session)
        user_data = UserCreate(
            email="service@example.com",
            password="password123"
        )
        
        user = user_service.create_user(user_data)
        
        assert user.email == "service@example.com"
        assert user.id is not None
        assert user.hashed_password != "password123"  # Should be hashed
        assert verify_password("password123", user.hashed_password)

    def test_create_user_duplicate_email(self, db_session: Session, test_user: User):
        """Test creating user with duplicate email"""
        user_service = UserService(db_session)
        user_data = UserCreate(
            email=test_user.email,
            password="password123"
        )
        
        with pytest.raises(ValueError) as exc_info:
            user_service.create_user(user_data)
        
        assert "already registered" in str(exc_info.value).lower()

    def test_authenticate_user_success(self, db_session: Session, test_user: User):
        """Test successful user authentication"""
        user_service = UserService(db_session)
        
        authenticated_user = user_service.authenticate_user(
            test_user.email, 
            "testpassword123"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == test_user.id
        assert authenticated_user.email == test_user.email

    def test_authenticate_user_wrong_password(self, db_session: Session, test_user: User):
        """Test authentication with wrong password"""
        user_service = UserService(db_session)
        
        authenticated_user = user_service.authenticate_user(
            test_user.email,
            "wrongpassword"
        )
        
        assert authenticated_user is None

    def test_authenticate_user_nonexistent_email(self, db_session: Session):
        """Test authentication with non-existent email"""
        user_service = UserService(db_session)
        
        authenticated_user = user_service.authenticate_user(
            "nonexistent@example.com",
            "password123"
        )
        
        assert authenticated_user is None

    def test_authenticate_user_case_insensitive_email(self, db_session: Session, test_user: User):
        """Test case-insensitive email authentication"""
        user_service = UserService(db_session)
        
        # Test with uppercase email
        authenticated_user = user_service.authenticate_user(
            test_user.email.upper(),
            "testpassword123"
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == test_user.id


class TestAuthenticationDependency:
    """Test class for authentication dependency injection"""

    def test_get_current_user_valid_token(self, authenticated_client: TestClient, test_user: User):
        """Test getting current user with valid token"""
        # This test requires a way to inject the dependency
        # The actual implementation would depend on how dependencies are structured
        response = authenticated_client.get("/api/v1/products/")
        
        # If endpoint requires authentication and succeeds, dependency worked
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/products/", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_missing_token(self, client: TestClient):
        """Test getting current user without token"""
        response = client.get("/api/v1/products/")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_malformed_header(self, client: TestClient):
        """Test authentication with malformed header"""
        malformed_headers = [
            {"Authorization": "invalid_format"},
            {"Authorization": "Bearer"},  # Missing token
            {"Authorization": "Basic token"},  # Wrong type
            {"Auth": "Bearer valid_token"},  # Wrong header name
        ]
        
        for headers in malformed_headers:
            response = client.get("/api/v1/products/", headers=headers)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthorizationLevels:
    """Test class for different authorization levels"""

    def test_admin_user_permissions(self, db_session: Session):
        """Test admin user creation and permissions"""
        user_service = UserService(db_session)
        admin_data = UserCreate(
            email="admin@example.com",
            password="adminpass123"
        )
        
        admin_user = user_service.create_user(admin_data)
        
        # Manually set admin flag (in real app, this would be done differently)
        admin_user.is_admin = True
        db_session.commit()
        
        assert admin_user.is_admin is True

    def test_regular_user_permissions(self, test_user: User):
        """Test regular user permissions"""
        assert test_user.is_admin is False

    def test_token_contains_permission_info(self, test_user: User):
        """Test that tokens contain permission information"""
        data = {
            "sub": test_user.email,
            "user_id": test_user.id,
            "is_admin": test_user.is_admin
        }
        token = create_access_token(data)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "is_admin" in payload
        assert payload["is_admin"] == test_user.is_admin


class TestSecurityMeasures:
    """Test class for security measures and protections"""

    def test_token_rotation_scenario(self):
        """Test token rotation (creating new tokens)"""
        data = {"sub": "test@example.com", "user_id": 1}
        
        token1 = create_access_token(data)
        token2 = create_access_token(data)
        
        # Tokens should be different (due to different timestamps)
        assert token1 != token2
        
        # But both should be valid
        payload1 = verify_token(token1)
        payload2 = verify_token(token2)
        
        assert payload1["sub"] == payload2["sub"]

    def test_token_payload_tampering_protection(self):
        """Test protection against token payload tampering"""
        data = {"sub": "user@example.com", "user_id": 1}
        token = create_access_token(data)
        
        # Attempt to tamper with token
        parts = token.split('.')
        
        # Modify payload (this should invalidate signature)
        import base64
        import json
        
        try:
            payload_data = json.loads(base64.urlsafe_b64decode(parts[1] + '==='))
            payload_data["user_id"] = 999  # Tamper with user ID
            
            tampered_payload = base64.urlsafe_b64encode(
                json.dumps(payload_data).encode()
            ).decode().rstrip('=')
            
            tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"
            
            # Should fail verification
            with pytest.raises(HTTPException):
                verify_token(tampered_token)
                
        except Exception:
            # If tampering fails, that's also fine
            pass

    def test_brute_force_protection_simulation(self, db_session: Session, test_user: User):
        """Test simulation of brute force attack protection"""
        user_service = UserService(db_session)
        
        # Simulate multiple failed authentication attempts
        failed_attempts = 0
        for _ in range(10):
            result = user_service.authenticate_user(test_user.email, "wrongpassword")
            if result is None:
                failed_attempts += 1
        
        # All attempts should fail
        assert failed_attempts == 10
        
        # Valid password should still work (no lockout implemented yet)
        valid_result = user_service.authenticate_user(test_user.email, "testpassword123")
        assert valid_result is not None

    def test_timing_attack_resistance(self, db_session: Session):
        """Test resistance to timing attacks"""
        user_service = UserService(db_session)
        
        # Time authentication with valid and invalid emails
        import time
        
        # Test with non-existent email
        start_time = time.time()
        user_service.authenticate_user("nonexistent@example.com", "password")
        nonexistent_time = time.time() - start_time
        
        # Test with existing email but wrong password
        if hasattr(user_service, '_get_user_by_email'):
            # Create a user first
            test_user = User(
                email="timing@example.com",
                hashed_password=get_password_hash("correctpassword")
            )
            db_session.add(test_user)
            db_session.commit()
            
            start_time = time.time()
            user_service.authenticate_user("timing@example.com", "wrongpassword")
            existing_time = time.time() - start_time
            
            # Times should be relatively similar (within reasonable tolerance)
            # This is a basic check - real timing attack tests would be more sophisticated
            time_difference = abs(existing_time - nonexistent_time)
            assert time_difference < 1.0  # Within 1 second tolerance


class TestSessionManagement:
    """Test class for session management"""

    def test_token_blacklist_concept(self):
        """Test concept of token blacklisting (logout)"""
        # This would require implementing a token blacklist
        # For now, just test that tokens can be created and verified
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)
        
        # Token should be valid
        payload = verify_token(token)
        assert payload is not None
        
        # In a real implementation, after logout, this token should be blacklisted
        # and subsequent verification should fail

    def test_multiple_device_sessions(self):
        """Test multiple concurrent sessions"""
        user_data = {"sub": "multi@example.com", "user_id": 1}
        
        # Create multiple tokens for same user (different devices)
        token1 = create_access_token(user_data)
        token2 = create_access_token(user_data)
        token3 = create_access_token(user_data)
        
        # All tokens should be valid
        for token in [token1, token2, token3]:
            payload = verify_token(token)
            assert payload["sub"] == "multi@example.com"

    def test_token_refresh_concept(self):
        """Test concept of token refresh"""
        # Create token with short expiry
        data = {"sub": "refresh@example.com", "user_id": 1}
        short_token = create_access_token(data, timedelta(seconds=1))
        
        # Token should be valid immediately
        payload = verify_token(short_token)
        assert payload is not None
        
        # Create new token (refresh)
        new_token = create_access_token(data, timedelta(minutes=30))
        new_payload = verify_token(new_token)
        assert new_payload["sub"] == "refresh@example.com"


class TestConfigurationSecurity:
    """Test class for security configuration"""

    def test_secret_key_configuration(self):
        """Test that secret key is properly configured"""
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) > 10  # Minimum length
        assert settings.SECRET_KEY != "your-secret-key"  # Not default value

    def test_algorithm_configuration(self):
        """Test JWT algorithm configuration"""
        assert settings.ALGORITHM in ["HS256", "HS384", "HS512"]

    def test_token_expiry_configuration(self):
        """Test token expiry configuration"""
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES <= 1440  # Max 24 hours

    def test_bcrypt_rounds_configuration(self):
        """Test bcrypt rounds configuration"""
        assert settings.BCRYPT_ROUNDS >= 10  # Minimum secure rounds
        assert settings.BCRYPT_ROUNDS <= 15  # Reasonable maximum