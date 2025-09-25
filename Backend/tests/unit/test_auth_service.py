import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from app.services.auth_service import UserService
from app.models import User
from app.schemas.schemas import UserCreate


@pytest.mark.unit
class TestUserService:
    """Unit tests for UserService"""

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)

    @pytest.fixture
    def user_service(self, mock_db):
        """Create UserService instance with mock database"""
        return UserService(mock_db)

    def test_get_user_by_email_exists(self, user_service, mock_db):
        """Test getting user by email when user exists"""
        # Arrange
        test_email = "test@example.com"
        mock_user = Mock(spec=User)
        mock_user.email = test_email
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_user
        mock_db.query.return_value = mock_query

        # Act
        result = user_service.get_user_by_email(test_email)

        # Assert
        mock_db.query.assert_called_once_with(User)
        mock_query.filter.assert_called_once()
        mock_filter.first.assert_called_once()
        assert result == mock_user

    def test_get_user_by_email_not_exists(self, user_service, mock_db):
        """Test getting user by email when user doesn't exist"""
        # Arrange
        test_email = "nonexistent@example.com"
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        mock_db.query.return_value = mock_query

        # Act
        result = user_service.get_user_by_email(test_email)

        # Assert
        assert result is None

    @patch('app.services.auth_service.get_password_hash')
    def test_create_user_success(self, mock_hash, user_service, mock_db):
        """Test successful user creation"""
        # Arrange
        user_data = UserCreate(email="new@example.com", password="password123")
        mock_hash.return_value = "hashed_password"
        
        # Mock that user doesn't exist
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        mock_db.query.return_value = mock_query

        mock_new_user = Mock(spec=User)
        mock_db.add.return_value = None
        mock_db.commit.return_value = None
        mock_db.refresh.return_value = None

        # Act
        with patch('app.services.auth_service.User') as mock_user_model:
            mock_user_model.return_value = mock_new_user
            result = user_service.create_user(user_data)

        # Assert
        mock_hash.assert_called_once_with("password123")
        mock_user_model.assert_called_once_with(
            email="new@example.com",
            hashed_password="hashed_password"
        )
        mock_db.add.assert_called_once_with(mock_new_user)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_new_user)
        assert result == mock_new_user

    def test_create_user_email_already_exists(self, user_service, mock_db):
        """Test user creation with existing email"""
        # Arrange
        user_data = UserCreate(email="existing@example.com", password="password123")
        
        # Mock that user already exists
        existing_user = Mock(spec=User)
        mock_query = Mock()
        mock_filter = Mock()
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = existing_user
        mock_db.query.return_value = mock_query

        # Act & Assert
        with pytest.raises(ValueError, match="Email already registered"):
            user_service.create_user(user_data)

    @patch('app.services.auth_service.verify_password')
    def test_authenticate_user_success(self, mock_verify, user_service, mock_db):
        """Test successful user authentication"""
        # Arrange
        email = "test@example.com"
        password = "password123"
        mock_user = Mock(spec=User)
        mock_user.hashed_password = "hashed_password"
        
        # Mock get_user_by_email
        with patch.object(user_service, 'get_user_by_email') as mock_get_user:
            mock_get_user.return_value = mock_user
            mock_verify.return_value = True

            # Act
            result = user_service.authenticate_user(email, password)

            # Assert
            mock_get_user.assert_called_once_with(email)
            mock_verify.assert_called_once_with(password, "hashed_password")
            assert result == mock_user

    @patch('app.services.auth_service.verify_password')
    def test_authenticate_user_wrong_password(self, mock_verify, user_service, mock_db):
        """Test user authentication with wrong password"""
        # Arrange
        email = "test@example.com"
        password = "wrongpassword"
        mock_user = Mock(spec=User)
        mock_user.hashed_password = "hashed_password"
        
        # Mock get_user_by_email
        with patch.object(user_service, 'get_user_by_email') as mock_get_user:
            mock_get_user.return_value = mock_user
            mock_verify.return_value = False

            # Act
            result = user_service.authenticate_user(email, password)

            # Assert
            assert result is None

    def test_authenticate_user_not_found(self, user_service, mock_db):
        """Test user authentication with non-existent user"""
        # Arrange
        email = "nonexistent@example.com"
        password = "password123"
        
        # Mock get_user_by_email
        with patch.object(user_service, 'get_user_by_email') as mock_get_user:
            mock_get_user.return_value = None

            # Act
            result = user_service.authenticate_user(email, password)

            # Assert
            assert result is None