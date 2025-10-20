"""
Conversation Schemas

Pydantic schemas for conversation-related data validation and serialization.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID

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
