"""
Authentication Service

JWT-based authentication service for user management.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Authentication service"""
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            return None
    
    async def create_user(self, user_data: UserCreate, db: Session) -> User:
        """Create a new user"""
        try:
            # Check if user already exists
            existing_user = await db.execute(
                select(User).where(User.email == user_data.email)
            )
            if existing_user.scalar_one_or_none():
                raise ValueError("User with this email already exists")
            
            existing_username = await db.execute(
                select(User).where(User.username == user_data.username)
            )
            if existing_username.scalar_one_or_none():
                raise ValueError("Username already taken")
            
            # Create new user
            hashed_password = self.get_password_hash(user_data.password)
            user = User(
                email=user_data.email,
                username=user_data.username,
                password_hash=hashed_password,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                language_preference=user_data.language_preference
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            logger.info(f"Created new user: {user.email}")
            return user
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating user: {e}")
            raise
    
    async def authenticate_user(self, email: str, password: str, db: Session) -> str:
        """Authenticate user and return JWT token"""
        try:
            # Get user from database
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError("Invalid email or password")
            
            if not user.is_active:
                raise ValueError("User account is disabled")
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                raise ValueError("Invalid email or password")
            
            # Update last login
            user.last_login = datetime.utcnow()
            await db.commit()
            
            # Create access token
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role
            }
            access_token = self.create_access_token(token_data)
            
            logger.info(f"User authenticated: {user.email}")
            return access_token
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise
    
    async def get_user_from_token(self, token: str) -> Optional[User]:
        """Get user from JWT token"""
        try:
            payload = self.verify_token(token)
            if not payload or payload.get("type") != "access":
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            # Note: In a real implementation, you'd need a database session here
            # For now, we'll return a mock user object
            return User(
                id=user_id,
                email=payload.get("email"),
                role=payload.get("role")
            )
            
        except Exception as e:
            logger.error(f"Error getting user from token: {e}")
            return None
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Refresh access token using refresh token"""
        try:
            payload = self.verify_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                return None
            
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            # Create new access token
            token_data = {
                "sub": user_id,
                "email": payload.get("email"),
                "role": payload.get("role")
            }
            new_access_token = self.create_access_token(token_data)
            
            return new_access_token
            
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None
