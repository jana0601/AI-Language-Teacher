"""
Conversation Service

Business logic for conversation management and analysis.
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from uuid import UUID

from app.models.conversation import Conversation, ConversationEvaluation
from app.models.user import User
from app.schemas.conversation import ConversationCreate

logger = logging.getLogger(__name__)

class ConversationService:
    """Conversation service"""
    
    async def create_conversation(
        self, 
        conversation_data: ConversationCreate, 
        user_id: UUID, 
        db: Session
    ) -> Conversation:
        """Create a new conversation"""
        try:
            conversation = Conversation(
                user_id=user_id,
                class_id=conversation_data.class_id,
                title=conversation_data.title,
                description=conversation_data.description,
                topic=conversation_data.topic,
                difficulty_level=conversation_data.difficulty_level,
                language=conversation_data.language
            )
            
            db.add(conversation)
            await db.commit()
            await db.refresh(conversation)
            
            logger.info(f"Created conversation: {conversation.id}")
            return conversation
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating conversation: {e}")
            raise
    
    async def get_conversation(
        self, 
        conversation_id: UUID, 
        user_id: UUID, 
        db: Session
    ) -> Optional[Conversation]:
        """Get a conversation by ID"""
        try:
            result = await db.execute(
                select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return None
    
    async def get_user_conversations(
        self, 
        user_id: UUID, 
        db: Session
    ) -> List[Conversation]:
        """Get all conversations for a user"""
        try:
            result = await db.execute(
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(desc(Conversation.created_at))
            )
            return result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error getting user conversations: {e}")
            return []
    
    async def get_conversation_evaluation(
        self, 
        conversation_id: UUID, 
        db: Session
    ) -> Optional[ConversationEvaluation]:
        """Get evaluation for a conversation"""
        try:
            result = await db.execute(
                select(ConversationEvaluation).where(
                    ConversationEvaluation.conversation_id == conversation_id
                )
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting conversation evaluation: {e}")
            return None
    
    async def get_user_progress(
        self, 
        user_id: UUID, 
        db: Session
    ) -> Dict[str, Any]:
        """Get user's learning progress"""
        try:
            # Get total conversations
            total_conversations_result = await db.execute(
                select(func.count(Conversation.id)).where(Conversation.user_id == user_id)
            )
            total_conversations = total_conversations_result.scalar() or 0
            
            # Get average score
            avg_score_result = await db.execute(
                select(func.avg(ConversationEvaluation.overall_score))
                .join(Conversation)
                .where(Conversation.user_id == user_id)
            )
            average_score = avg_score_result.scalar() or 0.0
            
            # Get current level (latest evaluation)
            latest_evaluation_result = await db.execute(
                select(ConversationEvaluation.proficiency_level)
                .join(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(desc(ConversationEvaluation.created_at))
                .limit(1)
            )
            current_level = latest_evaluation_result.scalar() or "A1"
            
            # Get last conversation date
            last_conversation_result = await db.execute(
                select(Conversation.created_at)
                .where(Conversation.user_id == user_id)
                .order_by(desc(Conversation.created_at))
                .limit(1)
            )
            last_conversation_date = last_conversation_result.scalar()
            
            # Get trend data (last 10 conversations)
            trend_evaluations_result = await db.execute(
                select(
                    ConversationEvaluation.grammar_score,
                    ConversationEvaluation.vocabulary_score,
                    ConversationEvaluation.fluency_score,
                    ConversationEvaluation.pronunciation_score,
                    ConversationEvaluation.comprehension_score
                )
                .join(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(desc(ConversationEvaluation.created_at))
                .limit(10)
            )
            
            trend_data = trend_evaluations_result.all()
            
            # Extract trend arrays
            grammar_trend = [eval.grammar_score for eval in trend_data]
            vocabulary_trend = [eval.vocabulary_score for eval in trend_data]
            fluency_trend = [eval.fluency_score for eval in trend_data]
            pronunciation_trend = [eval.pronunciation_score for eval in trend_data]
            comprehension_trend = [eval.comprehension_score for eval in trend_data]
            
            return {
                "total_conversations": total_conversations,
                "average_score": round(average_score, 2),
                "current_level": current_level,
                "last_conversation_date": last_conversation_date,
                "grammar_trend": grammar_trend,
                "vocabulary_trend": vocabulary_trend,
                "fluency_trend": fluency_trend,
                "pronunciation_trend": pronunciation_trend,
                "comprehension_trend": comprehension_trend
            }
            
        except Exception as e:
            logger.error(f"Error getting user progress: {e}")
            return {
                "total_conversations": 0,
                "average_score": 0.0,
                "current_level": "A1",
                "last_conversation_date": None,
                "grammar_trend": [],
                "vocabulary_trend": [],
                "fluency_trend": [],
                "pronunciation_trend": [],
                "comprehension_trend": []
            }
    
    async def update_conversation_status(
        self, 
        conversation_id: UUID, 
        status: str, 
        db: Session
    ) -> bool:
        """Update conversation status"""
        try:
            result = await db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                return False
            
            conversation.status = status
            if status == "completed":
                conversation.completed_at = datetime.utcnow()
            
            await db.commit()
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating conversation status: {e}")
            return False
    
    async def delete_conversation(
        self, 
        conversation_id: UUID, 
        user_id: UUID, 
        db: Session
    ) -> bool:
        """Delete a conversation"""
        try:
            result = await db.execute(
                select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                return False
            
            await db.delete(conversation)
            await db.commit()
            
            logger.info(f"Deleted conversation: {conversation_id}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting conversation: {e}")
            return False
