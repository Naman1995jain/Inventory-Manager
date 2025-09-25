from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_database
from app.core.security import create_access_token
from app.core.config import settings
from app.services.auth_service import UserService
from app.schemas.schemas import UserCreate, User, Token, UserLogin
import logging

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Setup logging for fail2ban
logger = logging.getLogger(__name__)

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_database)
):
    """Register a new user"""
    user_service = UserService(db)
    
    try:
        user = user_service.create_user(user_data)
        return User.model_validate(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    request: Request,
    db: Session = Depends(get_database)
):
    """Login and get access token"""
    user_service = UserService(db)
    
    user = user_service.authenticate_user(user_data.email, user_data.password)
    if not user:
        # Log failed authentication attempt for fail2ban
        client_ip = request.client.host
        logger.warning(f"Failed login attempt for email {user_data.email} from IP {client_ip}")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires
    )
    
    # Log successful login
    client_ip = request.client.host
    logger.info(f"Successful login for email {user_data.email} from IP {client_ip}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }