# AI Configuration for AgroMitra
# Set up your AI provider credentials here

import os
from dotenv import load_dotenv

load_dotenv()

# AI Provider Configuration
AI_CONFIG = {
    # OpenAI Configuration
    'openai': {
        'api_key': os.getenv('OPENAI_API_KEY'),
        'model': 'gpt-4',
        'max_tokens': 2000,
        'temperature': 0.7,
        'enabled': False  # Set to True when you have API key
    },
    
    # Google Gemini Configuration  
    'gemini': {
        'api_key': os.getenv('GEMINI_API_KEY'),
        'model': 'gemini-pro',
        'enabled': True  # Set to True when you have API key
    },
    
    # Local AI Configuration (Free alternatives)
    'local': {
        'provider': 'ollama',  # or 'huggingface'
        'model': 'llama2',
        'endpoint': 'http://localhost:11434/api/generate',
        'enabled': True  # Enable for demo mode
    },
    
    # Default provider to use
    'default_provider': 'gemini',  # Change to 'openai' or 'gemini' when you have API keys
    
    # Feature flags
    'features': {
        'ai_disease_recommendations': True,
        'ai_chatbot': True, 
        'ai_crop_advice': True,
        'conversation_memory': True,
        'multilingual_ai': True
    }
}

def get_ai_provider():
    """Get the configured AI provider"""
    provider = AI_CONFIG['default_provider']
    config = AI_CONFIG.get(provider, {})
    
    if not config.get('enabled', False):
        print(f"Warning: AI provider '{provider}' is not enabled")
        return None
    
    return provider, config

def is_ai_feature_enabled(feature_name):
    """Check if a specific AI feature is enabled"""
    return AI_CONFIG['features'].get(feature_name, False)

# Example .env file content:
"""
# Add these lines to your .env file to enable AI features:

# OpenAI API Key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API Key (get from https://ai.google.dev/)
GEMINI_API_KEY=your_gemini_api_key_here

# Database URL
DATABASE_URL=sqlite:///agromitra_app.db

# Flask Secret Key
SECRET_KEY=your-secret-key-change-in-production
"""