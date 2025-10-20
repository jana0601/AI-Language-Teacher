"""
Pydantic Schemas

Data validation and serialization schemas for API requests and responses.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID

# User Schemas
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

# Conversation Schemas
class ConversationBase(BaseModel):
    """Base conversation schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    topic: Optional[str] = Field(None, max_length=100)
    difficulty_level: str = Field(..., max_length=10)
    language: str = Field(default="en", max_length=10)

class ConversationCreate(ConversationBase):
    """Conversation creation schema"""
    class_id: Optional[UUID] = None

class ConversationResponse(ConversationBase):
    """Conversation response schema"""
    id: UUID
    user_id: UUID
    class_id: Optional[UUID] = None
    duration_seconds: Optional[int] = None
    audio_file_url: Optional[str] = None
    video_file_url: Optional[str] = None
    transcript: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Analysis Schemas
class AnalysisResponse(BaseModel):
    """Analysis response schema"""
    conversation_id: UUID
    overall_score: float = Field(..., ge=0, le=100)
    grammar_score: float = Field(..., ge=0, le=25)
    vocabulary_score: float = Field(..., ge=0, le=20)
    fluency_score: float = Field(..., ge=0, le=20)
    pronunciation_score: float = Field(..., ge=0, le=15)
    comprehension_score: float = Field(..., ge=0, le=20)
    proficiency_level: str
    strengths: List[str]
    areas_for_improvement: List[str]
    recommendations: List[str]
    detailed_feedback: Dict[str, Any]
    grammar_errors: List[Dict[str, Any]]
    vocabulary_analysis: List[Dict[str, Any]]

# Progress Schemas
class ProgressMetrics(BaseModel):
    """Progress metrics schema"""
    total_conversations: int
    average_score: float
    current_level: str
    last_conversation_date: Optional[datetime] = None
    grammar_trend: List[float]
    vocabulary_trend: List[float]
    fluency_trend: List[float]
    pronunciation_trend: List[float]
    comprehension_trend: List[float]

# Class Schemas
class ClassBase(BaseModel):
    """Base class schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    language: str = Field(..., max_length=10)
    level: str = Field(..., max_length=10)
    max_students: int = Field(default=30, ge=1, le=100)

class ClassCreate(ClassBase):
    """Class creation schema"""
    pass

class ClassResponse(ClassBase):
    """Class response schema"""
    id: UUID
    teacher_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Assignment Schemas
class AssignmentBase(BaseModel):
    """Base assignment schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str
    instructions: str
    topic: Optional[str] = Field(None, max_length=100)
    difficulty_level: str = Field(..., max_length=10)
    duration_minutes: Optional[int] = Field(None, ge=1, le=120)
    due_date: Optional[datetime] = None

class AssignmentCreate(AssignmentBase):
    """Assignment creation schema"""
    class_id: UUID

class AssignmentResponse(AssignmentBase):
    """Assignment response schema"""
    id: UUID
    class_id: UUID
    teacher_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Achievement Schemas
class AchievementBase(BaseModel):
    """Base achievement schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: str
    icon_url: Optional[str] = None
    criteria: Dict[str, Any]
    points: int = Field(default=0, ge=0)
    category: Optional[str] = Field(None, max_length=100)

class AchievementResponse(AchievementBase):
    """Achievement response schema"""
    id: UUID
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserAchievementResponse(BaseModel):
    """User achievement response schema"""
    id: UUID
    user_id: UUID
    achievement_id: UUID
    earned_at: datetime
    achievement: AchievementResponse
    
    class Config:
        from_attributes = True

# Practice Session Schemas
class PracticeSessionBase(BaseModel):
    """Base practice session schema"""
    session_type: str = Field(..., max_length=50)
    topic: Optional[str] = Field(None, max_length=100)
    difficulty_level: Optional[str] = Field(None, max_length=10)
    duration_minutes: Optional[int] = Field(None, ge=1, le=120)

class PracticeSessionCreate(PracticeSessionBase):
    """Practice session creation schema"""
    pass

class PracticeSessionResponse(PracticeSessionBase):
    """Practice session response schema"""
    id: UUID
    user_id: UUID
    score: Optional[float] = None
    completed_at: datetime
    session_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Error Schemas
class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Success Schemas
class SuccessResponse(BaseModel):
    """Success response schema"""
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
