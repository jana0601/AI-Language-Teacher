"""
GPT-based conversation analysis service
Provides intelligent language analysis using OpenAI GPT models
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import json
import re

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available. Install with: pip install openai")

logger = logging.getLogger(__name__)

@dataclass
class GPTAnalysisResult:
    """Result of GPT-based conversation analysis"""
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
    detailed_feedback: Dict[str, Any]
    grammar_errors: List[Dict[str, Any]]
    vocabulary_analysis: List[Dict[str, Any]]

class GPTAnalysisService:
    """GPT-based conversation analysis service using OpenAI models"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.client = None
        
        if OPENAI_AVAILABLE and api_key:
            openai.api_key = api_key
            self.client = openai.AsyncOpenAI(api_key=api_key)
            logger.info(f"GPT Analysis Service initialized with model: {model}")
        else:
            logger.warning("GPT Analysis Service not available - no API key provided")
    
    async def analyze_conversation(
        self, 
        transcript: str, 
        context: str = "General conversation",
        audio_duration: Optional[float] = None
    ) -> GPTAnalysisResult:
        """
        Analyze conversation using GPT model
        """
        if not self.client:
            raise RuntimeError("GPT client not initialized. Please provide OpenAI API key.")
        
        try:
            # Create analysis prompt
            prompt = self._create_analysis_prompt(transcript, context, audio_duration)
            
            # Get GPT analysis
            analysis_text = await self._get_gpt_analysis(prompt)
            
            # Parse GPT response
            analysis_data = self._parse_gpt_response(analysis_text)
            
            # Create result object
            result = GPTAnalysisResult(
                overall_score=analysis_data.get('overall_score', 0),
                grammar_score=analysis_data.get('grammar_score', 0),
                vocabulary_score=analysis_data.get('vocabulary_score', 0),
                fluency_score=analysis_data.get('fluency_score', 0),
                pronunciation_score=analysis_data.get('pronunciation_score', 0),
                comprehension_score=analysis_data.get('comprehension_score', 0),
                proficiency_level=analysis_data.get('proficiency_level', 'A1'),
                strengths=analysis_data.get('strengths', []),
                areas_for_improvement=analysis_data.get('areas_for_improvement', []),
                recommendations=analysis_data.get('recommendations', []),
                detailed_feedback=analysis_data.get('detailed_feedback', {}),
                grammar_errors=analysis_data.get('grammar_errors', []),
                vocabulary_analysis=analysis_data.get('vocabulary_analysis', [])
            )
            
            logger.info(f"GPT analysis completed successfully for transcript: {transcript[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error in GPT analysis: {e}")
            raise
    
    def _create_analysis_prompt(self, transcript: str, context: str, audio_duration: Optional[float]) -> str:
        """Create a detailed prompt for GPT analysis"""
        
        prompt = f"""
You are an expert English language teacher and assessor. Please analyze the following English conversation transcript and provide a comprehensive evaluation.

TRANSCRIPT: "{transcript}"
CONTEXT: {context}
AUDIO DURATION: {audio_duration or 'Not specified'} seconds

Please provide your analysis in the following JSON format:

{{
    "overall_score": <number between 0-100>,
    "grammar_score": <number between 0-25>,
    "vocabulary_score": <number between 0-20>,
    "fluency_score": <number between 0-20>,
    "pronunciation_score": <number between 0-15>,
    "comprehension_score": <number between 0-20>,
    "proficiency_level": "<A1|A2|B1|B2|C1|C2>",
    "strengths": [
        "<specific strength 1>",
        "<specific strength 2>",
        "<specific strength 3>"
    ],
    "areas_for_improvement": [
        "<specific area 1>",
        "<specific area 2>",
        "<specific area 3>"
    ],
    "recommendations": [
        "<specific recommendation 1>",
        "<specific recommendation 2>",
        "<specific recommendation 3>"
    ],
    "detailed_feedback": {{
        "grammar_notes": "<detailed grammar analysis>",
        "vocabulary_notes": "<detailed vocabulary analysis>",
        "fluency_notes": "<detailed fluency analysis>",
        "pronunciation_notes": "<detailed pronunciation analysis>",
        "comprehension_notes": "<detailed comprehension analysis>"
    }},
    "grammar_errors": [
        {{
            "type": "<error type>",
            "description": "<error description>",
            "severity": "<low|medium|high>",
            "position": <character position>
        }}
    ],
    "vocabulary_analysis": [
        {{
            "word": "<word>",
            "complexity_score": <number>,
            "is_advanced": <true|false>,
            "frequency": <number>
        }}
    ]
}}

EVALUATION CRITERIA:
- Grammar (0-25): Sentence structure, verb tenses, articles, prepositions, subject-verb agreement
- Vocabulary (0-20): Word choice, complexity, appropriateness, range
- Fluency (0-20): Flow, coherence, naturalness, hesitation
- Pronunciation (0-15): Clarity, stress, intonation (inferred from text patterns)
- Comprehension (0-20): Understanding, relevance, coherence

CEFR LEVELS:
- A1: Basic user, familiar expressions, simple sentences
- A2: Elementary user, routine tasks, simple past/present
- B1: Intermediate user, clear standard input, familiar matters
- B2: Upper-intermediate user, complex text, spontaneous interaction
- C1: Advanced user, demanding texts, flexible language use
- C2: Proficient user, virtually everything, precise expression

Please be thorough, accurate, and constructive in your analysis. Focus on specific, actionable feedback.
"""
        return prompt
    
    async def _get_gpt_analysis(self, prompt: str) -> str:
        """Get analysis from GPT model"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert English language teacher and assessor. Always respond with valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=2000,
                timeout=30
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling GPT API: {e}")
            raise
    
    def _parse_gpt_response(self, response_text: str) -> Dict[str, Any]:
        """Parse GPT response and extract analysis data"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                # Fallback parsing if JSON extraction fails
                return self._fallback_parse(response_text)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse GPT response as JSON: {e}")
            return self._fallback_parse(response_text)
    
    def _fallback_parse(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON parsing fails"""
        # Extract scores using regex
        scores = {}
        
        # Extract overall score
        overall_match = re.search(r'overall[_\s]*score[:\s]*(\d+(?:\.\d+)?)', response_text, re.IGNORECASE)
        if overall_match:
            scores['overall_score'] = float(overall_match.group(1))
        
        # Extract individual scores
        for score_type in ['grammar', 'vocabulary', 'fluency', 'pronunciation', 'comprehension']:
            pattern = rf'{score_type}[_\s]*score[:\s]*(\d+(?:\.\d+)?)'
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                scores[f'{score_type}_score'] = float(match.group(1))
        
        # Extract proficiency level
        level_match = re.search(r'proficiency[_\s]*level[:\s]*([A-C][1-2])', response_text, re.IGNORECASE)
        if level_match:
            scores['proficiency_level'] = level_match.group(1).upper()
        
        # Default values
        return {
            'overall_score': scores.get('overall_score', 50.0),
            'grammar_score': scores.get('grammar_score', 12.5),
            'vocabulary_score': scores.get('vocabulary_score', 10.0),
            'fluency_score': scores.get('fluency_score', 10.0),
            'pronunciation_score': scores.get('pronunciation_score', 7.5),
            'comprehension_score': scores.get('comprehension_score', 10.0),
            'proficiency_level': scores.get('proficiency_level', 'B1'),
            'strengths': ['Good communication effort', 'Clear expression'],
            'areas_for_improvement': ['Continue practicing', 'Expand vocabulary'],
            'recommendations': ['Keep practicing regularly', 'Read more English texts'],
            'detailed_feedback': {
                'grammar_notes': 'Basic grammar structure observed',
                'vocabulary_notes': 'Appropriate word choice',
                'fluency_notes': 'Clear communication',
                'pronunciation_notes': 'Text-based analysis',
                'comprehension_notes': 'Good understanding demonstrated'
            },
            'grammar_errors': [],
            'vocabulary_analysis': []
        }
    
    async def generate_conversation_response(
        self, 
        user_message: str, 
        analysis: GPTAnalysisResult, 
        topic: str,
        conversation_history: List[Dict[str, Any]] = None
    ) -> str:
        """Generate intelligent conversation response based on analysis"""
        
        if not self.client:
            return self._fallback_response(user_message, analysis, topic)
        
        try:
            # Create conversation prompt
            prompt = self._create_conversation_prompt(user_message, analysis, topic, conversation_history)
            
            # Get GPT response
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an intelligent English language teacher. Provide engaging, educational responses that help students improve their English."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300,
                timeout=20
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating conversation response: {e}")
            return self._fallback_response(user_message, analysis, topic)
    
    def _create_conversation_prompt(self, user_message: str, analysis: GPTAnalysisResult, topic: str, history: List[Dict[str, Any]] = None) -> str:
        """Create prompt for conversation response"""
        
        proficiency_level = analysis.proficiency_level
        strengths = ', '.join(analysis.strengths[:2])
        improvements = ', '.join(analysis.areas_for_improvement[:2])
        
        prompt = f"""
You are an intelligent English language teacher having a conversation with a student.

STUDENT MESSAGE: "{user_message}"
TOPIC: {topic}
STUDENT LEVEL: {proficiency_level}
STUDENT STRENGTHS: {strengths}
AREAS TO IMPROVE: {improvements}

Generate a natural, engaging response that:
1. Acknowledges their message appropriately
2. Provides educational value
3. Asks a follow-up question related to the topic
4. Adapts to their proficiency level ({proficiency_level})
5. Is encouraging and supportive

Keep your response conversational, natural, and educational. Ask a question that will help them practice more.
"""
        return prompt
    
    def _fallback_response(self, user_message: str, analysis: GPTAnalysisResult, topic: str) -> str:
        """Fallback response when GPT is not available"""
        
        proficiency_level = analysis.proficiency_level
        responses = {
            'A1': f"That's great! You're doing well with your English. What do you like most about {topic.lower()}?",
            'A2': f"Good job! I can see you're improving. Tell me more about your experience with {topic.lower()}.",
            'B1': f"Interesting point! Your English is getting better. What's your perspective on {topic.lower()}?",
            'B2': f"Excellent! You're expressing yourself well. How do you think {topic.lower()} has changed recently?",
            'C1': f"Sophisticated response! Your English is very good. What are your thoughts on the future of {topic.lower()}?",
            'C2': f"Outstanding! Your command of English is excellent. What's your assessment of current trends in {topic.lower()}?"
        }
        
        return responses.get(proficiency_level, f"That's interesting! Tell me more about {topic.lower()}.")
