"""
Application Configuration

Centralized configuration management using Pydantic settings.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Language Teacher"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Database
    DATABASE_URL: str = Field(default="postgresql://postgres:postgres@localhost:5432/language_teacher", env="DATABASE_URL")
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Security
    SECRET_KEY: str = Field(default="your_secret_key_here_minimum_32_characters_change_this_in_production", env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(default="your_jwt_secret_key_here_minimum_32_characters_change_this_in_production", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        env="CORS_ORIGINS"
    )
    
    # File Upload
    MAX_FILE_SIZE_MB: int = Field(default=100, env="MAX_FILE_SIZE_MB")
    ALLOWED_AUDIO_FORMATS: List[str] = Field(
        default=["mp3", "wav", "webm", "ogg"],
        env="ALLOWED_AUDIO_FORMATS"
    )
    
    # LLaMA Model
    LLAMA_MODEL_NAME: str = Field(
        default="meta-llama/Llama-2-7b-chat-hf",
        env="LLAMA_MODEL_NAME"
    )
    LLAMA_MAX_LENGTH: int = Field(default=1024, env="LLAMA_MAX_LENGTH")
    LLAMA_TEMPERATURE: float = Field(default=0.7, env="LLAMA_TEMPERATURE")
    
    # GPT Configuration
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    GPT_MODEL: str = Field(default="gpt-3.5-turbo", env="GPT_MODEL")
    USE_GPT_ANALYSIS: bool = Field(default=True, env="USE_GPT_ANALYSIS")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Analysis Settings
    ANALYSIS_TIMEOUT_SECONDS: int = Field(default=300, env="ANALYSIS_TIMEOUT_SECONDS")
    CACHE_ANALYSIS_RESULTS: bool = Field(default=True, env="CACHE_ANALYSIS_RESULTS")
    CACHE_TTL_HOURS: int = Field(default=24, env="CACHE_TTL_HOURS")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
