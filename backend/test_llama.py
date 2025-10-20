"""
Simple test script to verify LLaMA service works
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.llama_analysis import llama_service

async def test_llama_service():
    """Test the LLaMA analysis service"""
    print("Testing LLaMA Analysis Service...")
    
    try:
        # Test with a simple conversation
        test_transcript = """
        Hello, I am practicing my English conversation skills. 
        I enjoy learning new languages and meeting people from different cultures. 
        Today I want to discuss the importance of education and how it shapes our future.
        """
        
        print("Analyzing test conversation...")
        result = await llama_service.analyze_conversation(
            transcript=test_transcript,
            context="General conversation practice",
            audio_duration=30.0
        )
        
        print("Analysis completed successfully!")
        print(f"Overall Score: {result.overall_score:.1f}/100")
        print(f"Proficiency Level: {result.proficiency_level}")
        print(f"Grammar Score: {result.grammar_score}/25")
        print(f"Vocabulary Score: {result.vocabulary_score}/20")
        print(f"Fluency Score: {result.fluency_score}/20")
        print(f"Pronunciation Score: {result.pronunciation_score}/15")
        print(f"Comprehension Score: {result.comprehension_score}/20")
        
        print("\nStrengths:")
        for strength in result.strengths:
            print(f"  - {strength}")
        
        print("\nAreas for Improvement:")
        for area in result.areas_for_improvement:
            print(f"  - {area}")
        
        print("\nRecommendations:")
        for rec in result.recommendations:
            print(f"  - {rec}")
        
        return True
        
    except Exception as e:
        print(f"Error testing LLaMA service: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_llama_service())
    if success:
        print("\nLLaMA service is working correctly!")
    else:
        print("\nLLaMA service has issues, but fallback mode should work.")
    
    print("\nStarting FastAPI server...")
    print("You can now access the API at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
