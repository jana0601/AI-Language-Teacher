#!/usr/bin/env python3
"""
GPT Configuration Setup Script
Helps users set up GPT models for the Language Teacher application
"""

import os
import sys
from pathlib import Path

def setup_gpt_config():
    """Interactive setup for GPT configuration"""
    
    print("GPT Configuration Setup for Language Teacher")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path("backend/.env")
    if env_file.exists():
        print(f"Found existing .env file at {env_file}")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower().strip()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    
    # Get OpenAI API key
    print("\nOpenAI API Key Setup")
    print("You can get your API key from: https://platform.openai.com/api-keys")
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("No API key provided. GPT analysis will be disabled.")
        use_gpt = False
    else:
        use_gpt = True
    
    # Choose GPT model
    if use_gpt:
        print("\nGPT Model Selection")
        print("Available models:")
        print("1. gpt-3.5-turbo (recommended, cost-effective)")
        print("2. gpt-4 (more accurate, more expensive)")
        print("3. gpt-4-turbo (latest, most capable)")
        
        model_choice = input("Choose model (1-3, default: 1): ").strip()
        
        models = {
            "1": "gpt-3.5-turbo",
            "2": "gpt-4", 
            "3": "gpt-4-turbo"
        }
        
        gpt_model = models.get(model_choice, "gpt-3.5-turbo")
        print(f"Selected model: {gpt_model}")
    
    # Create .env file
    env_content = f"""# Language Teacher Application Environment Configuration

# Application Settings
DEBUG=false
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/language_teacher
REDIS_URL=redis://localhost:6379

# Security Keys (CHANGE THESE IN PRODUCTION!)
SECRET_KEY=your_secret_key_here_minimum_32_characters_change_this_in_production
JWT_SECRET_KEY=your_jwt_secret_key_here_minimum_32_characters_change_this_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001"]

# File Upload Settings
MAX_FILE_SIZE_MB=100
ALLOWED_AUDIO_FORMATS=["mp3", "wav", "webm", "ogg"]

# AI Model Configuration
USE_GPT_ANALYSIS={str(use_gpt).lower()}

# GPT Configuration (OpenAI)
OPENAI_API_KEY={api_key if api_key else "your_openai_api_key_here"}
GPT_MODEL={gpt_model if use_gpt else "gpt-3.5-turbo"}

# LLaMA Configuration (fallback)
LLAMA_MODEL_NAME=microsoft/DialoGPT-medium
LLAMA_MAX_LENGTH=1024
LLAMA_TEMPERATURE=0.7

# Analysis Settings
ANALYSIS_TIMEOUT_SECONDS=300
CACHE_ANALYSIS_RESULTS=true
CACHE_TTL_HOURS=24
"""
    
    # Write .env file
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"\nConfiguration saved to {env_file}")
        
        if use_gpt:
            print("\nGPT Setup Complete!")
            print(f"   Using GPT model: {gpt_model}")
            print(f"   API key configured")
            print("   GPT analysis enabled")
        else:
            print("\nGPT Setup Skipped")
            print("   LLaMA fallback will be used")
            print("   Add OPENAI_API_KEY to enable GPT")
        
        print("\nNext Steps:")
        print("   1. Restart the backend server")
        print("   2. Test the analysis in the frontend")
        print("   3. Check server status indicator")
        
    except Exception as e:
        print(f"Error writing configuration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Language Teacher - GPT Setup")
    print("=" * 30)
    setup_gpt_config()
