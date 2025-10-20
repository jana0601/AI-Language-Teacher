"""
FastAPI Backend for Language Teacher Application

Main application entry point with LLaMA integration for conversation analysis.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from app.services.llama_analysis import llama_service, AnalysisResult
from app.services.gpt_analysis import GPTAnalysisService
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.conversation import Conversation, ConversationEvaluation
from app.schemas.conversation import ConversationCreate, ConversationResponse, AnalysisResponse
from app.schemas.user import UserCreate, UserResponse
from app.services.auth import AuthService
from app.services.conversation_service import ConversationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Services
auth_service = AuthService()
conversation_service = ConversationService()

# Initialize GPT service
gpt_service = GPTAnalysisService(
    api_key=settings.OPENAI_API_KEY,
    model=settings.GPT_MODEL
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Language Teacher Application")
    if settings.USE_GPT_ANALYSIS and settings.OPENAI_API_KEY:
        logger.info(f"Using GPT model: {settings.GPT_MODEL}")
    else:
        logger.info(f"Using LLaMA model: {llama_service.model_name}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Language Teacher Application")

# Create FastAPI app
app = FastAPI(
    title="Language Teacher API",
    description="AI-powered language learning application with LLaMA conversation analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Set to False when allowing all origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        user = await auth_service.get_user_from_token(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# Test endpoint for LLaMA analysis (no authentication required)
@app.post("/api/test/analyze")
async def test_analyze_conversation(
    transcript: str = Form(...),
    context: Optional[str] = Form(None),
    audio_duration: Optional[float] = Form(None)
):
    """Test endpoint for LLaMA conversation analysis (no auth required)"""
    try:
        logger.info(f"Testing analysis with transcript: {transcript[:100]}...")
        
        # Choose analysis service based on configuration
        if settings.USE_GPT_ANALYSIS and settings.OPENAI_API_KEY:
            logger.info("Using GPT analysis")
            analysis_result = await gpt_service.analyze_conversation(
                transcript=transcript,
                context=context or "General conversation",
                audio_duration=audio_duration
            )
        else:
            logger.info("Using LLaMA analysis")
            analysis_result = await llama_service.analyze_conversation(
                transcript=transcript,
                context=context,
                audio_duration=audio_duration
            )
        
        logger.info(f"Analysis completed successfully")
        
        return {
            "conversation_id": "550e8400-e29b-41d4-a716-446655440000",  # Valid UUID format
            "overall_score": analysis_result.overall_score,
            "grammar_score": analysis_result.grammar_score,
            "vocabulary_score": analysis_result.vocabulary_score,
            "fluency_score": analysis_result.fluency_score,
            "pronunciation_score": analysis_result.pronunciation_score,
            "comprehension_score": analysis_result.comprehension_score,
            "proficiency_level": analysis_result.proficiency_level,
            "strengths": analysis_result.strengths,
            "areas_for_improvement": analysis_result.areas_for_improvement,
            "recommendations": analysis_result.recommendations,
            "detailed_feedback": analysis_result.detailed_feedback,
            "grammar_errors": analysis_result.grammar_errors,
            "vocabulary_analysis": analysis_result.vocabulary_analysis
        }
        
    except Exception as e:
        logger.error(f"Error in test analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "analysis_model": "GPT" if (settings.USE_GPT_ANALYSIS and settings.OPENAI_API_KEY) else "LLaMA",
        "model": settings.GPT_MODEL if (settings.USE_GPT_ANALYSIS and settings.OPENAI_API_KEY) else llama_service.model_name,
        "device": llama_service.device,
        "version": "1.0.0"
    }

# Authentication endpoints
@app.post("/api/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db=Depends(get_db)):
    """Register a new user"""
    try:
        user = await auth_service.create_user(user_data, db)
        return UserResponse.from_orm(user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
async def login_user(user_data: UserCreate, db=Depends(get_db)):
    """Login user and return JWT token"""
    try:
        token = await auth_service.authenticate_user(user_data.email, user_data.password, db)
        return {"access_token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# Conversation endpoints
@app.post("/api/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Create a new conversation"""
    try:
        conversation = await conversation_service.create_conversation(
            conversation_data, current_user.id, db
        )
        return ConversationResponse.from_orm(conversation)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/conversations/{conversation_id}/analyze", response_model=AnalysisResponse)
async def analyze_conversation(
    conversation_id: str,
    transcript: str = Form(...),
    context: Optional[str] = Form(None),
    audio_duration: Optional[float] = Form(None),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Analyze a conversation using LLaMA"""
    try:
        # Get conversation
        conversation = await conversation_service.get_conversation(conversation_id, current_user.id, db)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Update conversation with transcript
        conversation.transcript = transcript
        conversation.status = "processing"
        db.commit()
        
        # Analyze with LLaMA
        logger.info(f"Analyzing conversation {conversation_id} with LLaMA")
        analysis_result = await llama_service.analyze_conversation(
            transcript=transcript,
            context=context,
            audio_duration=audio_duration
        )
        
        # Save analysis results
        evaluation = ConversationEvaluation(
            conversation_id=conversation.id,
            evaluator_id=current_user.id,
            overall_score=analysis_result.overall_score,
            grammar_score=analysis_result.grammar_score,
            vocabulary_score=analysis_result.vocabulary_score,
            fluency_score=analysis_result.fluency_score,
            pronunciation_score=analysis_result.pronunciation_score,
            comprehension_score=analysis_result.comprehension_score,
            proficiency_level=analysis_result.proficiency_level,
            strengths=analysis_result.strengths,
            areas_for_improvement=analysis_result.areas_for_improvement,
            recommendations=analysis_result.recommendations,
            detailed_feedback=analysis_result.detailed_feedback,
            is_ai_generated=True
        )
        
        db.add(evaluation)
        db.commit()
        
        # Update conversation status
        conversation.status = "completed"
        db.commit()
        
        logger.info(f"Analysis completed for conversation {conversation_id}")
        
        return AnalysisResponse(
            conversation_id=conversation.id,
            overall_score=analysis_result.overall_score,
            grammar_score=analysis_result.grammar_score,
            vocabulary_score=analysis_result.vocabulary_score,
            fluency_score=analysis_result.fluency_score,
            pronunciation_score=analysis_result.pronunciation_score,
            comprehension_score=analysis_result.comprehension_score,
            proficiency_level=analysis_result.proficiency_level,
            strengths=analysis_result.strengths,
            areas_for_improvement=analysis_result.areas_for_improvement,
            recommendations=analysis_result.recommendations,
            detailed_feedback=analysis_result.detailed_feedback,
            grammar_errors=analysis_result.grammar_errors,
            vocabulary_analysis=analysis_result.vocabulary_analysis
        )
        
    except Exception as e:
        logger.error(f"Error analyzing conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/conversations", response_model=List[ConversationResponse])
async def get_user_conversations(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get all conversations for the current user"""
    try:
        conversations = await conversation_service.get_user_conversations(current_user.id, db)
        return [ConversationResponse.from_orm(conv) for conv in conversations]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get a specific conversation"""
    try:
        conversation = await conversation_service.get_conversation(conversation_id, current_user.id, db)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return ConversationResponse.from_orm(conversation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}/analysis", response_model=AnalysisResponse)
async def get_conversation_analysis(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get analysis results for a conversation"""
    try:
        evaluation = await conversation_service.get_conversation_evaluation(conversation_id, db)
        if not evaluation:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return AnalysisResponse(
            conversation_id=evaluation.conversation_id,
            overall_score=evaluation.overall_score,
            grammar_score=evaluation.grammar_score,
            vocabulary_score=evaluation.vocabulary_score,
            fluency_score=evaluation.fluency_score,
            pronunciation_score=evaluation.pronunciation_score,
            comprehension_score=evaluation.comprehension_score,
            proficiency_level=evaluation.proficiency_level,
            strengths=evaluation.strengths,
            areas_for_improvement=evaluation.areas_for_improvement,
            recommendations=evaluation.recommendations,
            detailed_feedback=evaluation.detailed_feedback,
            grammar_errors=[],  # Would need separate query for detailed errors
            vocabulary_analysis=[]  # Would need separate query for detailed analysis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Audio upload endpoint
@app.post("/api/conversations/{conversation_id}/audio")
async def upload_audio(
    conversation_id: str,
    audio_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Upload audio file for conversation"""
    try:
        # Validate file type
        if not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Get conversation
        conversation = await conversation_service.get_conversation(conversation_id, current_user.id, db)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Save audio file (simplified - in production, use cloud storage)
        audio_path = f"uploads/{conversation_id}_{audio_file.filename}"
        os.makedirs("uploads", exist_ok=True)
        
        with open(audio_path, "wb") as buffer:
            content = await audio_file.read()
            buffer.write(content)
        
        # Update conversation with audio file path
        conversation.audio_file_url = audio_path
        db.commit()
        
        return {"message": "Audio uploaded successfully", "file_path": audio_path}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Progress tracking endpoints
@app.get("/api/users/{user_id}/progress")
async def get_user_progress(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get user's learning progress"""
    try:
        if current_user.id != user_id and current_user.role != "teacher":
            raise HTTPException(status_code=403, detail="Not authorized")
        
        progress = await conversation_service.get_user_progress(user_id, db)
        return progress
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
