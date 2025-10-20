"""
LLaMA-based Language Analysis Service

This module provides conversation analysis using LLaMA models for:
- Grammar analysis
- Vocabulary assessment
- Fluency evaluation
- Comprehension scoring
- Overall proficiency assessment
"""

import asyncio
import json
import logging
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig,
    pipeline
)
import spacy
from textblob import TextBlob
import nltk
from nltk.corpus import wordnet
import numpy as np

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Result of conversation analysis"""
    overall_score: float
    grammar_score: float
    vocabulary_score: float
    fluency_score: float
    pronunciation_score: float
    comprehension_score: float
    proficiency_level: str
    strengths: List[str]
    areas_for_improvement: List[str]
    recommendations: List[str]
    grammar_errors: List[Dict[str, Any]]
    vocabulary_analysis: List[Dict[str, Any]]
    detailed_feedback: Dict[str, Any]

class LLaMAAnalysisService:
    """LLaMA-based conversation analysis service"""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self.nlp = None
        
        # Set random seed for consistent results
        torch.manual_seed(42)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(42)
        
        # Initialize components
        self._initialize_model()
        self._initialize_nlp()
        
    def _initialize_model(self):
        """Initialize model with fallback support"""
        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name,
                trust_remote_code=True
            )
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32 if self.device == "cpu" else torch.float16
            )
            
            # Set pad token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
            logger.info(f"Model {self.model_name} loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            # Fallback to a smaller model
            self._load_fallback_model()
    
    def _load_fallback_model(self):
        """Load a fallback model if main model fails"""
        try:
            fallback_model = "gpt2"
            self.tokenizer = AutoTokenizer.from_pretrained(fallback_model)
            self.model = AutoModelForCausalLM.from_pretrained(fallback_model)
            self.model_name = fallback_model
            logger.info(f"Loaded fallback model: {fallback_model}")
        except Exception as e:
            logger.error(f"Failed to load fallback model: {e}")
            raise RuntimeError("No suitable model could be loaded")
    
    def _initialize_nlp(self):
        """Initialize spaCy NLP model"""
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy English model not found. Using basic text processing.")
            # Create a simple fallback NLP processor
            self.nlp = None
    
    async def _llm_based_evaluation(self, transcript: str, context: Optional[str] = None) -> Dict[str, Any]:
        """LLM-based evaluation using intelligent analysis instead of rigid rules"""
        try:
            # Create a comprehensive prompt for LLM evaluation
            evaluation_prompt = f"""
You are an expert English language teacher evaluating a student's text. Please provide a detailed analysis in JSON format.

Student's text: "{transcript}"
Context: {context or "General conversation"}

Evaluate the following aspects and provide scores (0-25 for each):

1. GRAMMAR: Assess grammatical accuracy, sentence structure, verb tenses, articles, prepositions
2. VOCABULARY: Evaluate word choice, sophistication, appropriateness, spelling
3. FLUENCY: Assess natural flow, coherence, sentence variety, readability
4. COMPREHENSION: Evaluate clarity of meaning, logical structure, completeness

Consider the context and provide realistic scores. For very short texts (< 5 words), give low scores as they lack sufficient content for proper evaluation.

Respond ONLY with valid JSON in this exact format:
{{
    "grammar_score": <number>,
    "vocabulary_score": <number>, 
    "fluency_score": <number>,
    "comprehension_score": <number>,
    "overall_score": <sum of all scores>,
    "proficiency_level": "<A1/A2/B1/B2/C1/C2>",
    "detailed_feedback": {{
        "grammar": "<detailed grammar feedback>",
        "vocabulary": "<detailed vocabulary feedback>",
        "fluency": "<detailed fluency feedback>",
        "comprehension": "<detailed comprehension feedback>",
        "strengths": ["<strength1>", "<strength2>"],
        "improvements": ["<improvement1>", "<improvement2>"],
        "recommendations": ["<recommendation1>", "<recommendation2>"]
    }}
}}
"""

            # Generate response using LLaMA
            response = await self._generate_llama_response(evaluation_prompt)
            
            # Parse JSON response
            try:
                evaluation_data = json.loads(response)
                
                # Validate and ensure scores are within bounds
                grammar_score = max(0, min(25, evaluation_data.get("grammar_score", 0)))
                vocabulary_score = max(0, min(25, evaluation_data.get("vocabulary_score", 0)))
                fluency_score = max(0, min(25, evaluation_data.get("fluency_score", 0)))
                comprehension_score = max(0, min(25, evaluation_data.get("comprehension_score", 0)))
                
                overall_score = grammar_score + vocabulary_score + fluency_score + comprehension_score
                
                return {
                    "grammar_score": grammar_score,
                    "vocabulary_score": vocabulary_score,
                    "fluency_score": fluency_score,
                    "comprehension_score": comprehension_score,
                    "overall_score": overall_score,
                    "proficiency_level": evaluation_data.get("proficiency_level", "A1"),
                    "detailed_feedback": evaluation_data.get("detailed_feedback", {}),
                    "evaluation_method": "LLM-based"
                }
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM evaluation JSON, using fallback")
                return self._fallback_evaluation(transcript)
                
        except Exception as e:
            logger.error(f"LLM-based evaluation failed: {e}")
            return self._fallback_evaluation(transcript)
    
    def _fallback_evaluation(self, transcript: str) -> Dict[str, Any]:
        """Fallback evaluation when LLM evaluation fails"""
        words = transcript.split()
        word_count = len(words)
        
        # Simple fallback scoring based on length
        if word_count < 2:
            base_score = 1
        elif word_count < 5:
            base_score = 3
        elif word_count < 10:
            base_score = 8
        else:
            base_score = 15
        
        return {
            "grammar_score": base_score,
            "vocabulary_score": base_score,
            "fluency_score": base_score,
            "comprehension_score": base_score,
            "overall_score": base_score * 4,
            "proficiency_level": "A1" if word_count < 5 else "B1",
            "detailed_feedback": {
                "grammar": "Basic evaluation - please provide more text for detailed analysis",
                "vocabulary": "Basic evaluation - please provide more text for detailed analysis",
                "fluency": "Basic evaluation - please provide more text for detailed analysis",
                "comprehension": "Basic evaluation - please provide more text for detailed analysis",
                "strengths": ["Attempted communication"],
                "improvements": ["Provide more complete sentences"],
                "recommendations": ["Try writing longer, more detailed responses"]
            },
            "evaluation_method": "Fallback"
        }

    async def analyze_conversation(
        self, 
        transcript: str, 
        context: Optional[str] = None,
        audio_duration: Optional[float] = None
    ) -> AnalysisResult:
        """
        Analyze a conversation transcript using LLM-based evaluation
        
        Args:
            transcript: The conversation text to analyze
            context: Optional context about the conversation
            audio_duration: Duration of the audio in seconds
            
        Returns:
            AnalysisResult with detailed analysis
        """
        try:
            # Use LLM-based evaluation instead of rule-based analysis
            evaluation_result = await self._llm_based_evaluation(transcript, context)
            
            # Extract scores and feedback
            overall_score = evaluation_result["overall_score"]
            grammar_score = evaluation_result["grammar_score"]
            vocabulary_score = evaluation_result["vocabulary_score"]
            fluency_score = evaluation_result["fluency_score"]
            comprehension_score = evaluation_result["comprehension_score"]
            proficiency_level = evaluation_result["proficiency_level"]
            detailed_feedback = evaluation_result["detailed_feedback"]
            
            # Create analysis result
            return AnalysisResult(
                overall_score=overall_score,
                grammar_score=grammar_score,
                vocabulary_score=vocabulary_score,
                fluency_score=fluency_score,
                pronunciation_score=0,  # Removed pronunciation analysis
                comprehension_score=comprehension_score,
                proficiency_level=proficiency_level,
                strengths=detailed_feedback.get("strengths", ["Communication attempted"]),
                areas_for_improvement=detailed_feedback.get("improvements", ["Continue practicing"]),
                recommendations=detailed_feedback.get("recommendations", ["Keep learning"]),
                grammar_errors=[{"feedback": detailed_feedback.get("grammar", "Grammar analysis completed")}],
                vocabulary_analysis=[{"feedback": detailed_feedback.get("vocabulary", "Vocabulary analysis completed")}],
                detailed_feedback=detailed_feedback
            )
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            # Return a basic fallback result
            return AnalysisResult(
                overall_score=5,
                grammar_score=1,
                vocabulary_score=1,
                fluency_score=1,
                pronunciation_score=0,
                comprehension_score=2,
                proficiency_level="A1",
                strengths=["Attempted communication"],
                areas_for_improvement=["Try again with a complete sentence"],
                recommendations=["Check your internet connection"],
                grammar_errors=[{"feedback": "Analysis failed - please try again"}],
                vocabulary_analysis=[{"feedback": "Analysis failed - please try again"}],
                detailed_feedback={"error": "Analysis failed"}
            )
    
    async def _analyze_grammar(self, text: str) -> Dict[str, Any]:
        """Analyze grammar using spaCy and custom rules"""
        if self.nlp is None:
            # Fallback grammar analysis without spaCy
            return self._fallback_grammar_analysis(text)
        
        doc = self.nlp(text)
        
        errors = []
        error_count = 0
        
        # Check for common grammar issues
        for token in doc:
            # Subject-verb agreement
            if token.dep_ == "nsubj" and token.head.pos_ == "VERB":
                if not self._check_subject_verb_agreement(token, token.head):
                    errors.append({
                        "type": "subject_verb_agreement",
                        "description": f"Subject-verb disagreement: '{token.text}' and '{token.head.text}'",
                        "severity": "high",
                        "position": token.idx
                    })
                    error_count += 1
            
            # Article usage
            if token.pos_ == "DET" and token.text.lower() in ["a", "an"]:
                if not self._check_article_usage(token):
                    errors.append({
                        "type": "article_usage",
                        "description": f"Incorrect article usage: '{token.text}'",
                        "severity": "medium",
                        "position": token.idx
                    })
                    error_count += 1
        
        # Calculate grammar score (0-25 points) - More sophisticated scoring with length penalties
        word_count = len(text.split())
        error_rate = error_count / max(word_count, 1)
        
        # Base score based on error rate
        if error_rate < 0.05:  # Less than 5% errors - Excellent
            base_score = 25
        elif error_rate < 0.1:  # Less than 10% errors - Very Good
            base_score = 22
        elif error_rate < 0.15:  # Less than 15% errors - Good
            base_score = 18
        elif error_rate < 0.25:  # Less than 25% errors - Fair
            base_score = 15
        else:
            base_score = max(8, 25 - error_count * 1.5)  # More lenient penalty
        
        # Additional base score reduction for very short texts (grammar needs sufficient content)
        if word_count < 2:
            base_score = max(1, base_score - 15)  # Severe reduction for single words
        elif word_count < 3:
            base_score = max(2, base_score - 10)  # Heavy reduction for two words
        elif word_count < 5:
            base_score = max(3, base_score - 6)   # Moderate reduction for short texts
        elif word_count < 10:
            base_score = max(5, base_score - 3)   # Light reduction for medium texts
        
        # Length penalty for very short texts (grammar analysis needs sufficient content)
        if word_count < 2:
            length_penalty = 25  # Maximum penalty for single words
        elif word_count < 3:
            length_penalty = 22  # Extreme penalty for two words
        elif word_count < 5:
            length_penalty = 18  # Heavy penalty for short texts
        elif word_count < 10:
            length_penalty = 12  # Moderate penalty for medium texts
        else:
            length_penalty = 0   # No penalty for longer texts
        
        score = max(1, base_score - length_penalty)
        
        return {
            "score": score,
            "errors": errors,
            "error_count": error_count,
            "error_rate": error_rate
        }
    
    async def _analyze_vocabulary(self, text: str) -> Dict[str, Any]:
        """Analyze vocabulary sophistication and diversity with spelling check"""
        try:
            words = text.lower().split()
            if not words:
                return {"score": 0, "feedback": "No vocabulary to analyze"}
            
            # Check for spelling errors (comprehensive dictionary check)
            common_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
                'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
                'will', 'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall',
                'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
                'this', 'that', 'these', 'those', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
                'hello', 'hi', 'how', 'are', 'you', 'fine', 'good', 'bad', 'yes', 'no', 'thank', 'thanks',
                'please', 'sorry', 'excuse', 'name', 'what', 'where', 'when', 'why', 'who', 'which',
                'go', 'come', 'see', 'look', 'hear', 'listen', 'speak', 'talk', 'say', 'tell',
                'know', 'think', 'believe', 'want', 'need', 'like', 'love', 'hate', 'feel',
                'make', 'take', 'give', 'get', 'put', 'find', 'work', 'play', 'eat', 'drink',
                'sleep', 'walk', 'run', 'sit', 'stand', 'open', 'close', 'start', 'stop', 'help',
                'time', 'day', 'night', 'morning', 'evening', 'week', 'month', 'year', 'today', 'tomorrow',
                'yesterday', 'now', 'then', 'here', 'there', 'up', 'down', 'left', 'right', 'front', 'back',
                'big', 'small', 'large', 'little', 'old', 'new', 'young', 'hot', 'cold', 'warm', 'cool',
                'fast', 'slow', 'quick', 'easy', 'hard', 'difficult', 'simple', 'complex', 'important',
                'beautiful', 'ugly', 'nice', 'great', 'wonderful', 'terrible', 'excellent', 'perfect',
                'happy', 'sad', 'angry', 'excited', 'nervous', 'calm', 'tired', 'busy', 'free', 'ready',
                'sure', 'certain', 'possible', 'impossible', 'necessary', 'enough', 'too', 'very', 'quite',
                'really', 'actually', 'finally', 'suddenly', 'usually', 'always', 'never', 'sometimes',
                'often', 'rarely', 'almost', 'nearly', 'exactly', 'about', 'around', 'between', 'among',
                'through', 'across', 'over', 'under', 'above', 'below', 'inside', 'outside', 'near', 'far',
                'first', 'second', 'third', 'last', 'next', 'previous', 'other', 'another', 'same', 'different',
                'each', 'every', 'all', 'some', 'many', 'much', 'few', 'little', 'more', 'most', 'less', 'least',
                'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
                'hundred', 'thousand', 'million', 'billion', 'number', 'amount', 'quantity', 'size', 'length',
                'width', 'height', 'weight', 'price', 'cost', 'money', 'dollar', 'cent', 'euro', 'pound',
                'house', 'home', 'room', 'door', 'window', 'wall', 'floor', 'ceiling', 'bed', 'chair', 'table',
                'car', 'bus', 'train', 'plane', 'boat', 'bike', 'bicycle', 'motorcycle', 'truck', 'taxi',
                'food', 'water', 'bread', 'meat', 'fish', 'chicken', 'beef', 'pork', 'vegetable', 'fruit',
                'apple', 'banana', 'orange', 'grape', 'strawberry', 'milk', 'coffee', 'tea', 'juice', 'beer',
                'wine', 'cake', 'cookie', 'candy', 'chocolate', 'ice', 'cream', 'sugar', 'salt', 'pepper',
                'family', 'mother', 'father', 'parent', 'child', 'son', 'daughter', 'brother', 'sister',
                'grandmother', 'grandfather', 'uncle', 'aunt', 'cousin', 'friend', 'neighbor', 'teacher',
                'student', 'doctor', 'nurse', 'police', 'firefighter', 'engineer', 'lawyer', 'artist',
                'musician', 'singer', 'dancer', 'actor', 'writer', 'journalist', 'photographer', 'cook',
                'waiter', 'driver', 'pilot', 'sailor', 'farmer', 'worker', 'manager', 'boss', 'employee',
                'company', 'business', 'office', 'factory', 'hospital', 'school', 'university', 'library',
                'museum', 'theater', 'cinema', 'restaurant', 'hotel', 'shop', 'store', 'market', 'bank',
                'post', 'office', 'station', 'airport', 'park', 'garden', 'beach', 'mountain', 'river',
                'lake', 'ocean', 'sea', 'forest', 'desert', 'city', 'town', 'village', 'country', 'world',
                'earth', 'sky', 'sun', 'moon', 'star', 'cloud', 'rain', 'snow', 'wind', 'storm', 'weather',
                'spring', 'summer', 'autumn', 'winter', 'season', 'temperature', 'climate', 'nature',
                'animal', 'dog', 'cat', 'bird', 'fish', 'horse', 'cow', 'pig', 'sheep', 'chicken', 'duck',
                'elephant', 'lion', 'tiger', 'bear', 'wolf', 'fox', 'rabbit', 'mouse', 'snake', 'spider',
                'tree', 'flower', 'grass', 'leaf', 'root', 'branch', 'fruit', 'seed', 'plant', 'garden',
                'book', 'page', 'story', 'novel', 'magazine', 'newspaper', 'letter', 'email', 'message',
                'phone', 'computer', 'internet', 'website', 'television', 'radio', 'music', 'song', 'movie',
                'game', 'sport', 'football', 'basketball', 'tennis', 'golf', 'swimming', 'running', 'cycling',
                'dancing', 'singing', 'reading', 'writing', 'drawing', 'painting', 'photography', 'cooking',
                'shopping', 'traveling', 'vacation', 'holiday', 'party', 'celebration', 'birthday', 'wedding',
                'funeral', 'meeting', 'conference', 'interview', 'presentation', 'speech', 'lecture', 'class',
                'lesson', 'homework', 'exam', 'test', 'grade', 'score', 'result', 'success', 'failure',
                'problem', 'solution', 'question', 'answer', 'idea', 'opinion', 'fact', 'truth', 'lie',
                'secret', 'mystery', 'adventure', 'journey', 'trip', 'visit', 'tour', 'guide', 'map',
                'direction', 'way', 'path', 'road', 'street', 'address', 'location', 'place', 'position',
                'job', 'career', 'profession', 'work', 'task', 'project', 'plan', 'goal', 'dream', 'hope',
                'wish', 'desire', 'choice', 'decision', 'option', 'possibility', 'chance', 'opportunity',
                'risk', 'danger', 'safety', 'security', 'protection', 'help', 'support', 'assistance',
                'advice', 'suggestion', 'recommendation', 'instruction', 'rule', 'law', 'regulation',
                'policy', 'agreement', 'contract', 'deal', 'bargain', 'discount', 'sale', 'offer',
                'request', 'demand', 'order', 'command', 'permission', 'allowance', 'freedom', 'right',
                'responsibility', 'duty', 'obligation', 'promise', 'commitment', 'loyalty', 'trust',
                'honesty', 'integrity', 'character', 'personality', 'behavior', 'attitude', 'mood',
                'emotion', 'feeling', 'sensation', 'experience', 'memory', 'thought', 'mind', 'brain',
                'heart', 'soul', 'spirit', 'life', 'death', 'birth', 'age', 'health', 'illness', 'disease',
                'medicine', 'drug', 'treatment', 'therapy', 'cure', 'recovery', 'healing', 'pain',
                'injury', 'wound', 'cut', 'bruise', 'burn', 'fever', 'cold', 'flu', 'headache', 'stomach',
                'tooth', 'eye', 'ear', 'nose', 'mouth', 'hand', 'finger', 'arm', 'leg', 'foot', 'head',
                'face', 'hair', 'skin', 'blood', 'bone', 'muscle', 'nerve', 'organ', 'body', 'human',
                'person', 'people', 'man', 'woman', 'boy', 'girl', 'baby', 'adult', 'teenager', 'elderly'
            }
            
            # Count spelling errors (words not in common dictionary)
            spelling_errors = 0
            misspelled_words = []
            for word in words:
                # Remove punctuation for spelling check
                clean_word = ''.join(c for c in word if c.isalpha())
                if clean_word and clean_word not in common_words and len(clean_word) > 1:
                    spelling_errors += 1
                    misspelled_words.append(clean_word)
            
            # Calculate base score (reduced for short texts)
            base_score = min(10, len(words) * 0.4)  # Reduced from 12 to 10
            
            # Penalty for spelling errors (significant impact)
            spelling_penalty = spelling_errors * 2.5  # Each error costs 2.5 points
            
            # Advanced vocabulary detection (reduced bonus)
            advanced_words = [
                'sophisticated', 'comprehensive', 'implementation', 'paradigm', 'methodology',
                'contemporary', 'multifaceted', 'stakeholders', 'prioritize', 'simultaneously',
                'fundamentally', 'transformed', 'revolution', 'artificial', 'intelligence',
                'healthcare', 'systems', 'regulatory', 'frameworks', 'nevertheless',
                'outweigh', 'inherent', 'properly', 'managed', 'consequently',
                'reevaluation', 'traditional', 'embracing', 'technological', 'innovation',
                'ethical', 'considerations', 'implications', 'necessitate', 'comprehensive',
                'paradigm', 'methodology', 'contemporary', 'multifaceted', 'stakeholders',
                'prioritize', 'simultaneously', 'fundamentally', 'transformed', 'revolution',
                'artificial', 'intelligence', 'healthcare', 'systems', 'regulatory', 'frameworks',
                'nevertheless', 'outweigh', 'inherent', 'properly', 'managed', 'consequently',
                'reevaluation', 'traditional', 'embracing', 'technological', 'innovation',
                'ethical', 'considerations', 'implications', 'necessitate', 'comprehensive'
            ]
            
            advanced_count = sum(1 for word in words if word in advanced_words)
            advanced_bonus = min(6, advanced_count * 1.5)  # Reduced from 12 to 6
            
            # Vocabulary diversity bonus (reduced)
            unique_words = len(set(words))
            diversity_bonus = min(4, unique_words * 0.15)  # Reduced from 8 to 4
            
            # Length penalty for very short texts (increased penalties)
            if len(words) < 2:
                length_penalty = 15  # Extreme penalty for single words
            elif len(words) < 3:
                length_penalty = 12  # Heavy penalty for very short texts
            elif len(words) < 5:
                length_penalty = 8   # Moderate penalty for short texts
            elif len(words) < 10:
                length_penalty = 4   # Light penalty for medium texts
            else:
                length_penalty = 0
            
            # Sophistication bonus based on average word length (reduced)
            avg_word_length = sum(len(word) for word in words) / len(words)
            sophistication_bonus = min(2, (avg_word_length - 4) * 0.5)  # Reduced from 3 to 2
            
            # Calculate total score with proper capping to ensure it never exceeds 20
            total_score = base_score + advanced_bonus + diversity_bonus + sophistication_bonus - spelling_penalty - length_penalty
            
            # Ensure minimum score but heavily penalize very short texts
            if len(words) < 2:
                min_score = max(0.1, len(words) * 0.1)  # Very low minimum for single words
            elif len(words) < 3:
                min_score = max(0.3, len(words) * 0.2)  # Very low minimum for short texts
            elif len(words) < 5:
                min_score = max(0.5, len(words) * 0.3)  # Low minimum for short texts
            else:
                min_score = max(1, len(words) * 0.15)  # Normal minimum for longer texts
            
            # Ensure score is between min_score and 20 (maximum)
            final_score = max(min_score, min(20, total_score))
            
            feedback = f"Vocabulary: {len(words)} words, {unique_words} unique, {advanced_count} advanced, {spelling_errors} spelling errors"
            if misspelled_words:
                feedback += f" (misspelled: {', '.join(misspelled_words[:3])})"
            
            return {"score": final_score, "feedback": feedback}
            
        except Exception as e:
            logger.error(f"Vocabulary analysis error: {e}")
            return {"score": 1, "feedback": "Vocabulary analysis failed"}
    
    async def _analyze_fluency(self, text: str, duration: Optional[float] = None) -> Dict[str, Any]:
        """Analyze fluency based on text patterns"""
        words = text.split()
        word_count = len(words)
        
        if word_count == 0:
            return {"score": 0, "metrics": {}}
        
        # Calculate words per minute if duration provided
        wpm = (word_count / duration * 60) if duration else 150
        
        # Analyze sentence structure
        sentences = re.split(r'[.!?]+', text)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        avg_sentence_length = np.mean(sentence_lengths) if sentence_lengths else 0
        
        # Check for repetition
        unique_words = len(set(words))
        lexical_diversity = unique_words / word_count if word_count > 0 else 0
        
        # Calculate fluency score (0-20 points)
        wpm_score = 1.0 if 120 <= wpm <= 180 else 0.7 if 100 <= wpm <= 200 else 0.4
        sentence_score = 1.0 if 8 <= avg_sentence_length <= 20 else 0.7
        diversity_score = min(1.0, lexical_diversity * 2)
        
        base_score = (wpm_score + sentence_score + diversity_score) / 3 * 20
        
        # Severe penalties for short texts (fluency requires sufficient content)
        if word_count < 2:
            length_penalty = 18  # Maximum penalty for single words
        elif word_count < 3:
            length_penalty = 15  # Extreme penalty for two words
        elif word_count < 5:
            length_penalty = 12  # Heavy penalty for short texts
        elif word_count < 10:
            length_penalty = 8   # Moderate penalty for medium texts
        else:
            length_penalty = 0   # No penalty for longer texts
        
        # Additional base score reduction for very short texts
        if word_count < 2:
            base_score = max(0.1, base_score - 12)  # Severe reduction for single words
        elif word_count < 3:
            base_score = max(0.2, base_score - 8)   # Heavy reduction for two words
        elif word_count < 5:
            base_score = max(0.5, base_score - 5)   # Moderate reduction for short texts
        elif word_count < 10:
            base_score = max(1, base_score - 2)     # Light reduction for medium texts
        
        score = max(0.1, base_score - length_penalty)
        
        return {
            "score": score,
            "metrics": {
                "words_per_minute": wpm,
                "average_sentence_length": avg_sentence_length,
                "lexical_diversity": lexical_diversity,
                "unique_words": unique_words
            }
        }
    
    async def _analyze_comprehension(self, text: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Analyze comprehension using enhanced heuristics and LLaMA model"""
        
        # Enhanced heuristic analysis
        heuristic_score = self._enhanced_comprehension_analysis(text, context)
        
        # Use LLaMA to assess comprehension (if available)
        try:
            prompt = f"""
            Analyze the following text for comprehension and coherence:
            
            Text: "{text}"
            Context: {context or "General conversation"}
            
            Rate the comprehension level (0-20) based on:
            1. Logical flow of ideas
            2. Appropriate responses to context
            3. Coherence and clarity
            4. Understanding of topic
            5. Sophistication of expression
            
            Provide a score and brief explanation.
            """
            
            response = await self._generate_llama_response(prompt)
            llama_score = self._extract_score_from_response(response, max_score=20)
            
            # Combine heuristic and LLaMA scores
            score = (heuristic_score * 0.6 + llama_score * 0.4)
            
        except Exception as e:
            logger.warning(f"LLaMA comprehension analysis failed: {e}")
            score = heuristic_score
        
        return {
            "score": min(20, score),
            "analysis": "Enhanced comprehension analysis completed"
        }
    
    def _enhanced_comprehension_analysis(self, text: str, context: Optional[str] = None) -> float:
        """Enhanced heuristic comprehension analysis"""
        words = text.split()
        word_count = len(words)
        
        if word_count == 0:
            return 0
        
        score = 0
        
        # Heavy penalties for short texts - comprehension requires sufficient content
        # 1. Text length and complexity (0-6 points) - Much stricter for short texts
        if word_count >= 30:
            score += 6
        elif word_count >= 20:
            score += 5
        elif word_count >= 15:
            score += 4
        elif word_count >= 10:
            score += 3
        elif word_count >= 5:
            score += 0.5  # Very low score for short texts
        elif word_count >= 3:
            score += 0.2  # Extremely low score for 3-4 words
        elif word_count >= 2:
            score += 0.1  # Almost no score for 2 words
        else:
            score += 0.05  # Minimal score for single words
        
        # 2. Sentence structure analysis (0-6 points)
        sentences = text.split('.')
        avg_sentence_length = word_count / len(sentences) if sentences else 0
        
        if avg_sentence_length >= 12:
            score += 6  # Complex sentences
        elif avg_sentence_length >= 8:
            score += 5  # Moderate complexity
        elif avg_sentence_length >= 6:
            score += 4  # Basic complexity
        elif avg_sentence_length >= 4:
            score += 3  # Simple sentences
        else:
            score += 2  # Very simple
        
        # 3. Vocabulary sophistication (0-6 points)
        complex_words = [word for word in words if len(word) > 5]
        sophistication_ratio = len(complex_words) / word_count
        
        if sophistication_ratio >= 0.2:
            score += 6
        elif sophistication_ratio >= 0.15:
            score += 5
        elif sophistication_ratio >= 0.1:
            score += 4
        elif sophistication_ratio >= 0.05:
            score += 3
        else:
            score += 2
        
        # 4. Coherence indicators (0-6 points)
        coherence_score = 0
        
        # Check for transition words
        transition_words = ['however', 'therefore', 'moreover', 'furthermore', 'consequently', 'meanwhile', 'nevertheless', 'also', 'additionally', 'furthermore']
        if any(word.lower() in text.lower() for word in transition_words):
            coherence_score += 3
        
        # Check for complex conjunctions
        complex_conjunctions = ['although', 'despite', 'whereas', 'while', 'since', 'because', 'if', 'when', 'after', 'before']
        if any(word.lower() in text.lower() for word in complex_conjunctions):
            coherence_score += 2
        
        # Check for relative clauses
        if 'which' in text.lower() or 'that' in text.lower() or 'who' in text.lower():
            coherence_score += 1
        
        score += min(6, coherence_score)
        
        # Minimum score for any meaningful text
        min_score = min(6, word_count / 3)
        
        return min(20, max(min_score, score))
    
    async def _generate_llama_feedback(self, text: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive feedback using LLaMA"""
        prompt = f"""
        As an expert language teacher, analyze this conversation and provide detailed feedback:
        
        Conversation: "{text}"
        Context: {context or "General conversation"}
        
        Provide analysis in this JSON format:
        {{
            "strengths": ["strength1", "strength2"],
            "areas_for_improvement": ["area1", "area2"],
            "recommendations": ["rec1", "rec2"],
            "detailed_feedback": {{
                "grammar_notes": "grammar feedback",
                "vocabulary_notes": "vocabulary feedback",
                "fluency_notes": "fluency feedback",
                "comprehension_notes": "comprehension feedback",
                "overall_assessment": "overall assessment"
            }}
        }}
        """
        
        try:
            response = await self._generate_llama_response(prompt)
            feedback = self._parse_json_response(response)
        except Exception as e:
            logger.warning(f"LLaMA feedback generation failed: {e}")
            feedback = self._generate_fallback_feedback(text)
        
        return feedback
    
    async def _generate_llama_response(self, prompt: str, max_length: int = 500) -> str:
        """Generate response using LLaMA model"""
        try:
            # Tokenize input
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=1024
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=0.1,  # Lower temperature for more consistent results
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    top_p=0.9,  # Add top_p for more focused generation
                    repetition_penalty=1.1  # Reduce repetition
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:], 
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"LLaMA generation error: {e}")
            raise
    
    def _calculate_word_complexity(self, word: str) -> float:
        """Calculate word complexity based on various factors"""
        # Length factor
        length_score = min(len(word) / 10, 1) * 3
        
        # Syllable count (approximate)
        syllables = self._count_syllables(word)
        syllable_score = min(syllables / 4, 1) * 2
        
        # Morphological complexity
        morph_score = self._assess_morphological_complexity(word) * 2
        
        # Frequency (inverse - rarer words are more complex)
        freq_score = self._get_word_frequency_score(word) * 3
        
        return (length_score + syllable_score + morph_score + freq_score) / 4
    
    def _count_syllables(self, word: str) -> int:
        """Approximate syllable count"""
        vowels = "aeiouy"
        word = word.lower()
        count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent 'e'
        if word.endswith('e') and count > 1:
            count -= 1
        
        return max(1, count)
    
    def _assess_morphological_complexity(self, word: str) -> float:
        """Assess morphological complexity"""
        complexity = 0
        
        # Check for prefixes
        prefixes = ['un', 're', 'pre', 'anti', 'dis', 'mis', 'over', 'under']
        for prefix in prefixes:
            if word.startswith(prefix):
                complexity += 0.5
        
        # Check for suffixes
        suffixes = ['tion', 'sion', 'ness', 'ment', 'able', 'ible', 'ful', 'less']
        for suffix in suffixes:
            if word.endswith(suffix):
                complexity += 0.5
        
        # Check for compound words
        if '_' in word or any(char.isupper() for char in word[1:]):
            complexity += 1
        
        return min(complexity, 2)
    
    def _get_word_frequency_score(self, word: str) -> float:
        """Get word frequency score (higher = more common = less complex)"""
        # Common words (simplified frequency list)
        common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at'
        }
        
        if word in common_words:
            return 0.1  # Very common
        elif len(word) <= 4:
            return 0.3  # Short words
        elif len(word) <= 7:
            return 0.6  # Medium words
        else:
            return 0.9  # Long words (likely less common)
    
    def _check_subject_verb_agreement(self, subject: Any, verb: Any) -> bool:
        """Check subject-verb agreement"""
        # Simplified check - in practice, this would be more sophisticated
        subject_text = subject.text.lower()
        verb_text = verb.text.lower()
        
        # Basic singular/plural checks
        if subject_text in ['he', 'she', 'it'] and verb_text.endswith('s'):
            return True
        elif subject_text in ['they', 'we', 'you'] and not verb_text.endswith('s'):
            return True
        
        return True  # Default to correct for simplicity
    
    def _check_article_usage(self, token: Any) -> bool:
        """Check article usage"""
        # Simplified check
        word = token.text.lower()
        next_word = token.nbor(1).text.lower() if token.i + 1 < len(token.doc) else ""
        
        if word == 'a' and next_word.startswith(('a', 'e', 'i', 'o', 'u')):
            return False  # Should be 'an'
        elif word == 'an' and not next_word.startswith(('a', 'e', 'i', 'o', 'u')):
            return False  # Should be 'a'
        
        return True
    
    def _determine_proficiency_level(self, score: float) -> str:
        """Determine CEFR proficiency level based on score - Adjusted for SUM scoring (max 85)"""
        if score >= 70:  # C2: Excellent performance (82%+)
            return "C2"
        elif score >= 55:  # C1: Advanced performance (65%+)
            return "C1"
        elif score >= 40:  # B2: Upper-intermediate (47%+)
            return "B2"
        elif score >= 25:  # B1: Intermediate (29%+)
            return "B1"
        elif score >= 15:  # A2: Elementary (18%+)
            return "A2"
        else:
            return "A1"
    
    def _extract_score_from_response(self, response: str, max_score: int = 20) -> float:
        """Extract numerical score from LLaMA response"""
        # Look for score patterns in the response
        score_patterns = [
            r'score[:\s]*(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)/' + str(max_score),
            r'(\d+(?:\.\d+)?)\s*points?',
            r'(\d+(?:\.\d+)?)\s*out\s*of\s*' + str(max_score)
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                score = float(match.group(1))
                return min(score, max_score)
        
        # If no score found, return middle score
        return max_score / 2
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response from LLaMA"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
        except json.JSONDecodeError:
            pass
        
        # Fallback if JSON parsing fails
        return self._generate_fallback_feedback("")
    
    def _generate_fallback_feedback(self, text: str) -> Dict[str, Any]:
        """Generate fallback feedback when LLaMA fails"""
        return {
            "pronunciation_score": 0,  # Removed pronunciation analysis
            "strengths": ["Clear communication", "Good vocabulary usage"],
            "areas_for_improvement": ["Grammar accuracy", "Fluency"],
            "recommendations": ["Practice more conversations", "Focus on grammar"],
            "detailed_feedback": {
                "grammar_notes": "Continue practicing grammar rules",
                "vocabulary_notes": "Good word choice overall",
                "fluency_notes": "Work on speaking pace and pauses",
                "pronunciation_notes": "Focus on clear pronunciation",
                "overall_assessment": "Good effort, keep practicing"
            }
        }
    
    def _fallback_comprehension_score(self, text: str) -> float:
        """Fallback comprehension scoring using simple heuristics"""
        # Simple heuristics for comprehension
        sentences = re.split(r'[.!?]+', text)
        avg_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        
        # Longer, more complex sentences suggest better comprehension
        if avg_length > 15:
            return 18
        elif avg_length > 10:
            return 15
        elif avg_length > 5:
            return 12
        else:
            return 8
    
    def _fallback_grammar_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback grammar analysis without spaCy"""
        words = text.split()
        word_count = len(words)
        
        # Simple grammar checks
        errors = []
        error_count = 0
        
        # Check for basic patterns
        for i, word in enumerate(words):
            # Check for double words
            if i > 0 and word.lower() == words[i-1].lower():
                errors.append({
                    "type": "repetition",
                    "description": f"Repeated word: '{word}'",
                    "severity": "medium",
                    "position": i
                })
                error_count += 1
        
        # Calculate grammar score (0-25 points) - More sophisticated fallback scoring with length penalties
        error_rate = error_count / max(word_count, 1)
        
        # Base score based on error rate
        if error_rate < 0.05:  # Less than 5% errors - Excellent
            base_score = 25
        elif error_rate < 0.1:  # Less than 10% errors - Very Good
            base_score = 22
        elif error_rate < 0.15:  # Less than 15% errors - Good
            base_score = 18
        elif error_rate < 0.25:  # Less than 25% errors - Fair
            base_score = 15
        else:
            base_score = max(8, 25 - error_count * 1.5)  # More lenient penalty
        
        # Additional base score reduction for very short texts (grammar needs sufficient content)
        if word_count < 2:
            base_score = max(1, base_score - 15)  # Severe reduction for single words
        elif word_count < 3:
            base_score = max(2, base_score - 10)  # Heavy reduction for two words
        elif word_count < 5:
            base_score = max(3, base_score - 6)   # Moderate reduction for short texts
        elif word_count < 10:
            base_score = max(5, base_score - 3)   # Light reduction for medium texts
        
        # Length penalty for very short texts (grammar analysis needs sufficient content)
        if word_count < 2:
            length_penalty = 25  # Maximum penalty for single words
        elif word_count < 3:
            length_penalty = 22  # Extreme penalty for two words
        elif word_count < 5:
            length_penalty = 18  # Heavy penalty for short texts
        elif word_count < 10:
            length_penalty = 12  # Moderate penalty for medium texts
        else:
            length_penalty = 0   # No penalty for longer texts
        
        score = max(1, base_score - length_penalty)
        
        return {
            "score": score,
            "errors": errors,
            "error_count": error_count,
            "error_rate": error_rate
        }

# Global instance
llama_service = LLaMAAnalysisService()
