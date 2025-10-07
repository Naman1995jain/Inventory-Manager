from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_database
from app.core.security import verify_token
from app.models import User
from app.schemas.schemas import User as UserSchema

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> UserSchema:
    """Get current authenticated user"""
    token = credentials.credentials
    token_data = verify_token(token)

    # verify_token now returns only `user_id`. Use it to load the user from DB.
    user = None
    if token_data.get("user_id"):
        user = db.query(User).filter(User.id == token_data["user_id"]).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Convert to schema and return. Any authorization decisions should consult
    # the returned user object (user.is_admin) after fetching from DB.
    user_schema = UserSchema.model_validate(user)
    return user_schema

def get_current_active_user(
    current_user: UserSchema = Depends(get_current_user)
) -> UserSchema:
    """Get current active user"""
    return current_user