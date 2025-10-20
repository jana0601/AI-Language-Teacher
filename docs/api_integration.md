# Language Analysis APIs & Services Integration

## Overview

This document outlines the integration strategy for various language analysis APIs and services to provide comprehensive conversation evaluation capabilities.

## Core API Integrations

### 1. OpenAI Integration

#### GPT-4 for Language Analysis
```python
# Configuration
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-4-turbo-preview"

# Usage for conversation analysis
def analyze_conversation_with_gpt4(transcript, context):
    prompt = f"""
    Analyze this conversation transcript for language learning assessment:
    
    Context: {context}
    Transcript: {transcript}
    
    Provide analysis in JSON format:
    {{
        "grammar_score": 0-25,
        "vocabulary_score": 0-20,
        "fluency_score": 0-20,
        "pronunciation_score": 0-15,
        "comprehension_score": 0-20,
        "overall_score": 0-100,
        "proficiency_level": "A1|A2|B1|B2|C1|C2",
        "strengths": ["strength1", "strength2"],
        "areas_for_improvement": ["area1", "area2"],
        "recommendations": ["rec1", "rec2"],
        "grammar_errors": [
            {{
                "error_type": "verb_tense",
                "description": "Incorrect past tense usage",
                "suggested_correction": "should be 'went' instead of 'goed'",
                "severity": "medium"
            }}
        ],
        "vocabulary_analysis": [
            {{
                "word": "sophisticated",
                "complexity_score": 8.5,
                "appropriateness": 9.0,
                "is_advanced": true
            }}
        ]
    }}
    """
    
    response = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000
    )
    
    return json.loads(response.choices[0].message.content)
```

#### Whisper for Speech-to-Text
```python
def transcribe_audio_with_whisper(audio_file_path):
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai.Audio.transcribe(
            model="whisper-1",
            file=audio_file,
            response_format="verbose_json",
            language="en"  # or detect automatically
        )
    
    return {
        "text": transcript.text,
        "segments": transcript.segments,
        "language": transcript.language,
        "confidence": transcript.confidence
    }
```

### 2. Google Cloud Speech-to-Text

#### Configuration
```python
from google.cloud import speech

def transcribe_with_google_cloud(audio_file_path):
    client = speech.SpeechClient()
    
    with open(audio_file_path, "rb") as audio_file:
        content = audio_file.read()
    
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        sample_rate_hertz=48000,
        language_code="en-US",
        enable_automatic_punctuation=True,
        enable_word_time_offsets=True,
        enable_speaker_diarization=True,
        diarization_speaker_count=2,
        model="latest_long"
    )
    
    response = client.recognize(config=config, audio=audio)
    
    return {
        "transcript": response.results[0].alternatives[0].transcript,
        "confidence": response.results[0].alternatives[0].confidence,
        "words": response.results[0].alternatives[0].words,
        "speakers": extract_speaker_info(response.results[0].alternatives[0].words)
    }
```

### 3. Azure Cognitive Services

#### Language Understanding (LUIS)
```python
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials

def analyze_intent_with_luis(text):
    credentials = CognitiveServicesCredentials("your-subscription-key")
    client = LUISRuntimeClient(
        endpoint="https://your-resource.cognitiveservices.azure.com/",
        credentials=credentials
    )
    
    response = client.prediction.get_slot_prediction(
        app_id="your-app-id",
        slot_name="production",
        prediction_request={"query": text}
    )
    
    return {
        "intent": response.prediction.top_intent,
        "confidence": response.prediction.intents[response.prediction.top_intent].score,
        "entities": response.prediction.entities
    }
```

#### Text Analytics
```python
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

def analyze_sentiment_and_entities(text):
    client = TextAnalyticsClient(
        endpoint="https://your-resource.cognitiveservices.azure.com/",
        credential=AzureKeyCredential("your-api-key")
    )
    
    # Sentiment analysis
    sentiment_response = client.analyze_sentiment([text])
    sentiment = sentiment_response[0]
    
    # Entity recognition
    entities_response = client.recognize_entities([text])
    entities = entities_response[0]
    
    # Key phrase extraction
    key_phrases_response = client.extract_key_phrases([text])
    key_phrases = key_phrases_response[0]
    
    return {
        "sentiment": {
            "overall": sentiment.sentiment,
            "confidence": sentiment.confidence_scores,
            "sentences": [s.sentiment for s in sentiment.sentences]
        },
        "entities": [{"text": e.text, "category": e.category, "confidence": e.confidence_score} for e in entities.entities],
        "key_phrases": key_phrases.key_phrases
    }
```

### 4. IBM Watson Services

#### Natural Language Understanding
```python
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def analyze_with_watson_nlu(text):
    authenticator = IAMAuthenticator("your-api-key")
    nlu = NaturalLanguageUnderstandingV1(
        version="2022-04-07",
        authenticator=authenticator
    )
    nlu.set_service_url("https://api.us-south.natural-language-understanding.watson.cloud.ibm.com")
    
    response = nlu.analyze(
        text=text,
        features={
            "sentiment": {},
            "emotion": {},
            "entities": {"limit": 10},
            "keywords": {"limit": 10},
            "concepts": {"limit": 10},
            "syntax": {
                "tokens": {"lemma": True, "part_of_speech": True},
                "sentences": True
            }
        }
    ).get_result()
    
    return response
```

#### Speech-to-Text
```python
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

def transcribe_with_watson_stt(audio_file_path):
    authenticator = IAMAuthenticator("your-api-key")
    stt = SpeechToTextV1(authenticator=authenticator)
    stt.set_service_url("https://api.us-south.speech-to-text.watson.cloud.ibm.com")
    
    with open(audio_file_path, "rb") as audio_file:
        response = stt.recognize(
            audio=audio_file,
            content_type="audio/webm",
            model="en-US_BroadbandModel",
            timestamps=True,
            word_confidence=True,
            speaker_labels=True
        ).get_result()
    
    return response
```

## Custom Analysis Services

### 1. Grammar Analysis Service
```python
import spacy
from language_tool_python import LanguageTool

class GrammarAnalysisService:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.language_tool = LanguageTool('en-US')
    
    def analyze_grammar(self, text):
        # SpaCy analysis
        doc = self.nlp(text)
        spacy_analysis = {
            "pos_tags": [(token.text, token.pos_, token.tag_) for token in doc],
            "dependencies": [(token.text, token.dep_, token.head.text) for token in doc],
            "sentences": [sent.text for sent in doc.sents]
        }
        
        # LanguageTool analysis
        matches = self.language_tool.check(text)
        grammar_errors = []
        
        for match in matches:
            grammar_errors.append({
                "error_type": match.ruleId,
                "description": match.message,
                "suggested_correction": match.replacements[0] if match.replacements else None,
                "severity": self._get_severity(match.ruleId),
                "start_position": match.offset,
                "end_position": match.offset + match.errorLength
            })
        
        return {
            "spacy_analysis": spacy_analysis,
            "grammar_errors": grammar_errors,
            "grammar_score": self._calculate_grammar_score(text, grammar_errors)
        }
    
    def _get_severity(self, rule_id):
        critical_rules = ["VERB_TENSE", "SUBJECT_VERB_AGREEMENT"]
        high_rules = ["ARTICLE", "PREPOSITION"]
        
        if rule_id in critical_rules:
            return "critical"
        elif rule_id in high_rules:
            return "high"
        else:
            return "medium"
    
    def _calculate_grammar_score(self, text, errors):
        word_count = len(text.split())
        error_count = len(errors)
        
        if word_count == 0:
            return 0
        
        error_rate = error_count / word_count
        base_score = 25
        
        if error_rate < 0.02:  # Less than 2% errors
            return base_score
        elif error_rate < 0.05:  # Less than 5% errors
            return base_score * 0.8
        elif error_rate < 0.1:  # Less than 10% errors
            return base_score * 0.6
        else:
            return base_score * 0.4
```

### 2. Vocabulary Analysis Service
```python
import nltk
from nltk.corpus import wordnet
import requests

class VocabularyAnalysisService:
    def __init__(self):
        self.word_frequency = self._load_word_frequency()
        self.academic_words = self._load_academic_words()
    
    def analyze_vocabulary(self, text):
        words = self._extract_words(text)
        vocabulary_analysis = []
        
        for word in words:
            analysis = {
                "word": word,
                "frequency": self.word_frequency.get(word.lower(), 0),
                "complexity_score": self._calculate_complexity(word),
                "appropriateness_score": self._calculate_appropriateness(word, text),
                "is_advanced": self._is_advanced_word(word),
                "synonyms": self._get_synonyms(word),
                "word_family": self._get_word_family(word)
            }
            vocabulary_analysis.append(analysis)
        
        return {
            "vocabulary_analysis": vocabulary_analysis,
            "vocabulary_score": self._calculate_vocabulary_score(vocabulary_analysis),
            "lexical_diversity": self._calculate_lexical_diversity(words),
            "average_word_length": sum(len(word) for word in words) / len(words) if words else 0
        }
    
    def _calculate_complexity(self, word):
        # Factors: length, frequency, morphological complexity
        length_score = min(len(word) / 10, 1) * 3
        frequency_score = (1 - self.word_frequency.get(word.lower(), 0) / 1000000) * 4
        morphological_score = self._get_morphological_complexity(word) * 3
        
        return (length_score + frequency_score + morphological_score) / 3
    
    def _calculate_appropriateness(self, word, context):
        # Check if word fits the context and topic
        # This would involve topic modeling and context analysis
        return 8.0  # Placeholder implementation
    
    def _is_advanced_word(self, word):
        return word.lower() in self.academic_words or len(word) > 8
    
    def _get_synonyms(self, word):
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name().replace('_', ' '))
        return list(synonyms)[:5]
    
    def _calculate_vocabulary_score(self, analysis):
        if not analysis:
            return 0
        
        complexity_scores = [item["complexity_score"] for item in analysis]
        appropriateness_scores = [item["appropriateness_score"] for item in analysis]
        
        avg_complexity = sum(complexity_scores) / len(complexity_scores)
        avg_appropriateness = sum(appropriateness_scores) / len(appropriateness_scores)
        
        return (avg_complexity + avg_appropriateness) * 2.5  # Scale to 20 points
```

### 3. Fluency Analysis Service
```python
import librosa
import numpy as np

class FluencyAnalysisService:
    def __init__(self):
        self.target_wpm = 150  # Target words per minute
        self.pause_threshold = 0.5  # Seconds
    
    def analyze_fluency(self, audio_file_path, transcript):
        # Load audio
        y, sr = librosa.load(audio_file_path)
        
        # Calculate speaking rate
        words = transcript.split()
        duration = len(y) / sr
        wpm = (len(words) / duration) * 60
        
        # Detect pauses
        pauses = self._detect_pauses(y, sr)
        
        # Calculate fluency metrics
        fluency_metrics = {
            "words_per_minute": wpm,
            "speaking_rate_score": self._calculate_speaking_rate_score(wpm),
            "pause_frequency": len(pauses) / duration,
            "average_pause_length": np.mean([p["duration"] for p in pauses]) if pauses else 0,
            "pause_score": self._calculate_pause_score(pauses, duration),
            "rhythm_score": self._calculate_rhythm_score(y, sr),
            "overall_fluency_score": 0  # Will be calculated
        }
        
        # Calculate overall fluency score
        fluency_metrics["overall_fluency_score"] = (
            fluency_metrics["speaking_rate_score"] * 0.4 +
            fluency_metrics["pause_score"] * 0.3 +
            fluency_metrics["rhythm_score"] * 0.3
        ) * 20  # Scale to 20 points
        
        return fluency_metrics
    
    def _detect_pauses(self, y, sr):
        # Use energy-based pause detection
        frame_length = int(0.025 * sr)  # 25ms frames
        hop_length = int(0.010 * sr)   # 10ms hop
        
        # Calculate RMS energy
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Find pauses (low energy regions)
        pause_threshold = np.percentile(rms, 20)  # Bottom 20% energy
        pause_frames = rms < pause_threshold
        
        # Group consecutive pause frames
        pauses = []
        in_pause = False
        pause_start = 0
        
        for i, is_pause in enumerate(pause_frames):
            if is_pause and not in_pause:
                pause_start = i
                in_pause = True
            elif not is_pause and in_pause:
                pause_duration = (i - pause_start) * hop_length / sr
                if pause_duration > self.pause_threshold:
                    pauses.append({
                        "start": pause_start * hop_length / sr,
                        "end": i * hop_length / sr,
                        "duration": pause_duration
                    })
                in_pause = False
        
        return pauses
    
    def _calculate_speaking_rate_score(self, wpm):
        # Optimal range: 120-180 WPM
        if 120 <= wpm <= 180:
            return 1.0
        elif 100 <= wpm < 120 or 180 < wpm <= 200:
            return 0.8
        elif 80 <= wpm < 100 or 200 < wpm <= 220:
            return 0.6
        else:
            return 0.4
    
    def _calculate_pause_score(self, pauses, duration):
        if not pauses:
            return 1.0
        
        pause_ratio = sum(p["duration"] for p in pauses) / duration
        
        if pause_ratio < 0.1:  # Less than 10% pauses
            return 1.0
        elif pause_ratio < 0.2:  # Less than 20% pauses
            return 0.8
        elif pause_ratio < 0.3:  # Less than 30% pauses
            return 0.6
        else:
            return 0.4
    
    def _calculate_rhythm_score(self, y, sr):
        # Calculate rhythm regularity using tempo analysis
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        if len(beats) < 2:
            return 0.5
        
        # Calculate beat interval consistency
        beat_intervals = np.diff(beats)
        interval_std = np.std(beat_intervals)
        interval_mean = np.mean(beat_intervals)
        
        # Lower coefficient of variation = more regular rhythm
        cv = interval_std / interval_mean if interval_mean > 0 else 1
        
        # Convert to score (lower CV = higher score)
        return max(0, 1 - cv)
```

## API Service Management

### 1. Service Configuration
```python
class APIServiceManager:
    def __init__(self):
        self.services = {
            "openai": {
                "enabled": True,
                "api_key": os.getenv("OPENAI_API_KEY"),
                "rate_limit": 60,  # requests per minute
                "cost_per_request": 0.002
            },
            "google_cloud": {
                "enabled": True,
                "api_key": os.getenv("GOOGLE_CLOUD_API_KEY"),
                "rate_limit": 100,
                "cost_per_request": 0.006
            },
            "azure": {
                "enabled": True,
                "api_key": os.getenv("AZURE_API_KEY"),
                "rate_limit": 50,
                "cost_per_request": 0.001
            },
            "watson": {
                "enabled": True,
                "api_key": os.getenv("WATSON_API_KEY"),
                "rate_limit": 30,
                "cost_per_request": 0.003
            }
        }
    
    def get_available_service(self, service_type):
        for service_name, config in self.services.items():
            if config["enabled"] and service_type in service_name:
                return service_name, config
        return None, None
    
    def track_usage(self, service_name, request_count=1):
        # Track API usage for billing and rate limiting
        pass
```

### 2. Fallback Strategy
```python
class AnalysisServiceOrchestrator:
    def __init__(self):
        self.api_manager = APIServiceManager()
        self.custom_services = {
            "grammar": GrammarAnalysisService(),
            "vocabulary": VocabularyAnalysisService(),
            "fluency": FluencyAnalysisService()
        }
    
    def analyze_conversation(self, audio_file, transcript):
        analysis_results = {}
        
        # Try primary service, fallback to alternatives
        try:
            # Speech-to-text
            service_name, config = self.api_manager.get_available_service("speech")
            if service_name == "openai":
                analysis_results["transcript"] = self._transcribe_with_openai(audio_file)
            elif service_name == "google_cloud":
                analysis_results["transcript"] = self._transcribe_with_google(audio_file)
            
            # Language analysis
            service_name, config = self.api_manager.get_available_service("language")
            if service_name == "openai":
                analysis_results["language_analysis"] = self._analyze_with_openai(transcript)
            elif service_name == "azure":
                analysis_results["language_analysis"] = self._analyze_with_azure(transcript)
            
        except Exception as e:
            # Fallback to custom services
            analysis_results["grammar"] = self.custom_services["grammar"].analyze_grammar(transcript)
            analysis_results["vocabulary"] = self.custom_services["vocabulary"].analyze_vocabulary(transcript)
            analysis_results["fluency"] = self.custom_services["fluency"].analyze_fluency(audio_file, transcript)
        
        return analysis_results
```

## Error Handling & Monitoring

### 1. API Error Handling
```python
import logging
from functools import wraps

def handle_api_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"API Error in {func.__name__}: {str(e)}")
            return {"error": str(e), "fallback_used": True}
    return wrapper

@handle_api_errors
def safe_api_call(api_function, *args, **kwargs):
    return api_function(*args, **kwargs)
```

### 2. Rate Limiting
```python
import time
from collections import defaultdict

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_allowed(self, service_name, rate_limit):
        now = time.time()
        service_requests = self.requests[service_name]
        
        # Remove requests older than 1 minute
        service_requests[:] = [req_time for req_time in service_requests if now - req_time < 60]
        
        if len(service_requests) >= rate_limit:
            return False
        
        service_requests.append(now)
        return True
```

## Cost Optimization

### 1. Caching Strategy
```python
import redis
import json
import hashlib

class AnalysisCache:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.cache_ttl = 3600  # 1 hour
    
    def get_cached_analysis(self, text_hash):
        cached_result = self.redis_client.get(f"analysis:{text_hash}")
        if cached_result:
            return json.loads(cached_result)
        return None
    
    def cache_analysis(self, text_hash, analysis_result):
        self.redis_client.setex(
            f"analysis:{text_hash}",
            self.cache_ttl,
            json.dumps(analysis_result)
        )
    
    def get_text_hash(self, text):
        return hashlib.md5(text.encode()).hexdigest()
```

### 2. Batch Processing
```python
class BatchProcessor:
    def __init__(self, batch_size=10):
        self.batch_size = batch_size
        self.pending_requests = []
    
    def add_request(self, request):
        self.pending_requests.append(request)
        
        if len(self.pending_requests) >= self.batch_size:
            return self.process_batch()
        
        return None
    
    def process_batch(self):
        if not self.pending_requests:
            return []
        
        batch = self.pending_requests[:self.batch_size]
        self.pending_requests = self.pending_requests[self.batch_size:]
        
        # Process batch with single API call
        return self._process_batch_requests(batch)
```
