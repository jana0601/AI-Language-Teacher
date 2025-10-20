"""
User Schemas

Pydantic schemas for user-related data validation and serialization.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    language_preference: str = Field(default="en", max_length=10)

class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, max_length=100)

class UserResponse(UserBase):
    """User response schema"""
    id: UUID
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True
