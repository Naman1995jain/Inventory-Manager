import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    verify_token
)


@pytest.mark.unit
class TestSecurity:
    """Unit tests for security functions"""

    @patch('app.core.security.pwd_context')
    def test_verify_password_success(self, mock_pwd_context):
        """Test successful password verification"""
        # Arrange
        plain_password = "testpassword123"
        hashed_password = "hashed_password"
        mock_pwd_context.verify.return_value = True

        # Act
        result = verify_password(plain_password, hashed_password)

        # Assert
        mock_pwd_context.verify.assert_called_once_with(plain_password, hashed_password)
        assert result is True

    @patch('app.core.security.pwd_context')
    def test_verify_password_failure(self, mock_pwd_context):
        """Test failed password verification"""
        # Arrange
        plain_password = "wrongpassword"
        hashed_password = "hashed_password"
        mock_pwd_context.verify.return_value = False

        # Act
        result = verify_password(plain_password, hashed_password)

        # Assert
        mock_pwd_context.verify.assert_called_once_with(plain_password, hashed_password)
        assert result is False

    @patch('app.core.security.pwd_context')
    def test_get_password_hash(self, mock_pwd_context):
        """Test password hashing"""
        # Arrange
        password = "testpassword123"
        expected_hash = "hashed_password"
        mock_pwd_context.hash.return_value = expected_hash

        # Act
        result = get_password_hash(password)

        # Assert
        mock_pwd_context.hash.assert_called_once_with(password)
        assert result == expected_hash

    @patch('app.core.security.jwt')
    @patch('app.core.security.datetime')
    @patch('app.core.security.settings')
    def test_create_access_token_with_expires_delta(self, mock_settings, mock_datetime, mock_jwt):
        """Test creating access token with custom expiration"""
        # Arrange
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=15)
        
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_expire = mock_now + expires_delta
        mock_datetime.utcnow.return_value = mock_now
        
        mock_settings.SECRET_KEY = "secret_key"
        mock_settings.ALGORITHM = "HS256"
        
        mock_jwt.encode.return_value = "encoded_token"

        # Act
        result = create_access_token(data, expires_delta)

        # Assert
        expected_payload = {"sub": "test@example.com", "exp": mock_expire}
        mock_jwt.encode.assert_called_once_with(expected_payload, "secret_key", algorithm="HS256")
        assert result == "encoded_token"

    @patch('app.core.security.jwt')
    @patch('app.core.security.datetime')
    @patch('app.core.security.settings')
    def test_create_access_token_default_expiration(self, mock_settings, mock_datetime, mock_jwt):
        """Test creating access token with default expiration"""
        # Arrange
        data = {"sub": "test@example.com"}
        
        mock_now = datetime(2023, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = mock_now
        
        mock_settings.SECRET_KEY = "secret_key"
        mock_settings.ALGORITHM = "HS256"
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        
        mock_jwt.encode.return_value = "encoded_token"

        # Act
        result = create_access_token(data)

        # Assert
        expected_expire = mock_now + timedelta(minutes=30)
        expected_payload = {"sub": "test@example.com", "exp": expected_expire}
        mock_jwt.encode.assert_called_once_with(expected_payload, "secret_key", algorithm="HS256")
        assert result == "encoded_token"

    @patch('app.core.security.jwt')
    @patch('app.core.security.settings')
    def test_verify_token_success(self, mock_settings, mock_jwt):
        """Test successful token verification"""
        # Arrange
        token = "valid_token"
        mock_settings.SECRET_KEY = "secret_key"
        mock_settings.ALGORITHM = "HS256"
        
        mock_payload = {"sub": "test@example.com", "exp": 1234567890}
        mock_jwt.decode.return_value = mock_payload

        # Act
        result = verify_token(token)

        # Assert
        mock_jwt.decode.assert_called_once_with(token, "secret_key", algorithms=["HS256"])
        assert result == {"email": "test@example.com"}

    @patch('app.core.security.jwt')
    @patch('app.core.security.settings')
    def test_verify_token_no_subject(self, mock_settings, mock_jwt):
        """Test token verification with missing subject"""
        # Arrange
        token = "invalid_token"
        mock_settings.SECRET_KEY = "secret_key"
        mock_settings.ALGORITHM = "HS256"
        
        mock_payload = {"exp": 1234567890}  # Missing 'sub'
        mock_jwt.decode.return_value = mock_payload

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)

    @patch('app.core.security.jwt')
    @patch('app.core.security.settings')
    def test_verify_token_jwt_error(self, mock_settings, mock_jwt):
        """Test token verification with JWT error"""
        # Arrange
        token = "invalid_token"
        mock_settings.SECRET_KEY = "secret_key"
        mock_settings.ALGORITHM = "HS256"
        
        mock_jwt.decode.side_effect = JWTError("Invalid token")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)

    @patch('app.core.security.jwt')
    @patch('app.core.security.settings')
    def test_verify_token_expired(self, mock_settings, mock_jwt):
        """Test token verification with expired token"""
        # Arrange
        token = "expired_token"
        mock_settings.SECRET_KEY = "secret_key"
        mock_settings.ALGORITHM = "HS256"
        
        mock_jwt.decode.side_effect = JWTError("Token expired")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in str(exc_info.value.detail)