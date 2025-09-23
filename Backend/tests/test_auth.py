import pytest
from app.core.security import get_password_hash, verify_password, create_access_token, verify_token
from app.services.auth_service import UserService
from app.models import User
from app.schemas.schemas import UserCreate
from fastapi import HTTPException

class TestSecurity:
    """Test security utilities"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_token(self):
        """Test JWT token verification"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        decoded = verify_token(token)
        assert decoded["username"] == "testuser"
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        with pytest.raises(HTTPException):
            verify_token("invalid.token.here")

class TestUserService:
    """Test user service functions"""
    
    def test_create_user(self, clean_db, sample_user_data):
        """Test user creation"""
        user_service = UserService(clean_db)
        user_data = UserCreate(**sample_user_data)
        
        user = user_service.create_user(user_data)
        
        assert user.username == sample_user_data["username"]
        assert user.email == sample_user_data["email"]
        assert user.full_name == sample_user_data["full_name"]
        assert user.is_active is True
        assert user.is_superuser is False
        assert user.hashed_password != sample_user_data["password"]
    
    def test_create_duplicate_username(self, clean_db, sample_user_data):
        """Test creating user with duplicate username"""
        user_service = UserService(clean_db)
        user_data = UserCreate(**sample_user_data)
        
        # Create first user
        user_service.create_user(user_data)
        
        # Try to create second user with same username
        duplicate_data = sample_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        user_data_dup = UserCreate(**duplicate_data)
        
        with pytest.raises(ValueError, match="Username already registered"):
            user_service.create_user(user_data_dup)
    
    def test_create_duplicate_email(self, clean_db, sample_user_data):
        """Test creating user with duplicate email"""
        user_service = UserService(clean_db)
        user_data = UserCreate(**sample_user_data)
        
        # Create first user
        user_service.create_user(user_data)
        
        # Try to create second user with same email
        duplicate_data = sample_user_data.copy()
        duplicate_data["username"] = "differentuser"
        user_data_dup = UserCreate(**duplicate_data)
        
        with pytest.raises(ValueError, match="Email already registered"):
            user_service.create_user(user_data_dup)
    
    def test_authenticate_user(self, clean_db, sample_user_data):
        """Test user authentication"""
        user_service = UserService(clean_db)
        user_data = UserCreate(**sample_user_data)
        
        # Create user
        created_user = user_service.create_user(user_data)
        
        # Authenticate with correct credentials
        authenticated_user = user_service.authenticate_user(
            sample_user_data["username"], 
            sample_user_data["password"]
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
    
    def test_authenticate_wrong_password(self, clean_db, sample_user_data):
        """Test authentication with wrong password"""
        user_service = UserService(clean_db)
        user_data = UserCreate(**sample_user_data)
        
        # Create user
        user_service.create_user(user_data)
        
        # Try to authenticate with wrong password
        result = user_service.authenticate_user(
            sample_user_data["username"], 
            "wrongpassword"
        )
        
        assert result is None
    
    def test_authenticate_nonexistent_user(self, clean_db):
        """Test authentication with nonexistent user"""
        user_service = UserService(clean_db)
        
        result = user_service.authenticate_user("nonexistent", "password")
        assert result is None