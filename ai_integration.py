# AI Integration Module for AgroMitra
# This module provides Generative AI capabilities for recommendations and chatbot

import openai
import google.generativeai as genai
import os
from typing import Dict, List, Optional, Any
import json
import logging
from datetime import datetime

class AIRecommendationEngine:
    """
    Generative AI-powered recommendation engine for agricultural advice
    Supports multiple AI providers: OpenAI GPT, Google Gemini, local models
    """
    
    def __init__(self, provider="openai", api_key=None):
        self.provider = provider
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        self.setup_ai_client()
        
    def setup_ai_client(self):
        """Initialize AI client based on provider"""
        if self.provider == "openai":
            openai.api_key = self.api_key
        elif self.provider == "gemini":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        elif self.provider == "local":
            # For local models like Ollama, Hugging Face Transformers
            pass
            
    def generate_disease_recommendations(self, disease_info: Dict, farmer_context: Dict = None) -> Dict:
        """
        Generate AI-powered disease treatment recommendations
        
        Args:
            disease_info: Disease detection results
            farmer_context: Farmer's location, crops, history
            
        Returns:
            Enhanced recommendations with AI insights
        """
        
        prompt = self._build_disease_prompt(disease_info, farmer_context)
        
        try:
            if self.provider == "openai":
                response = self._call_openai(prompt)
            elif self.provider == "gemini":
                response = self._call_gemini(prompt)
            else:
                response = self._call_local_model(prompt)
                
            return self._parse_disease_response(response)
            
        except Exception as e:
            logging.error(f"AI recommendation generation failed: {e}")
            return self._fallback_recommendations(disease_info)
    
    def generate_crop_recommendations(self, farmer_profile: Dict, season: str, location: Dict) -> Dict:
        """
        Generate AI-powered crop selection recommendations
        
        Args:
            farmer_profile: Farmer's details, farm size, experience
            season: Current season (kharif, rabi, zaid)
            location: Geographic and climate data
            
        Returns:
            Personalized crop recommendations
        """
        
        prompt = f"""
        As an expert agricultural advisor, provide crop recommendations for:
        
        Farmer Profile:
        - Farm Size: {farmer_profile.get('farm_size', 'Unknown')} acres
        - Location: {farmer_profile.get('location', 'Unknown')}
        - Experience: {farmer_profile.get('experience', 'Unknown')}
        - Previous Crops: {farmer_profile.get('crops_grown', 'Unknown')}
        
        Current Season: {season}
        Location Details: {location}
        
        Provide:
        1. Top 5 recommended crops with reasons
        2. Expected yield and profit margins
        3. Water requirements and irrigation tips
        4. Market demand analysis
        5. Risk factors and mitigation strategies
        6. Seed varieties and suppliers
        7. Timeline and key farming activities
        
        Format as JSON with detailed explanations.
        """
        
        try:
            if self.provider == "openai":
                response = self._call_openai(prompt)
            elif self.provider == "gemini":
                response = self._call_gemini(prompt)
            else:
                response = self._call_local_model(prompt)
                
            return self._parse_crop_response(response)
            
        except Exception as e:
            logging.error(f"Crop recommendation generation failed: {e}")
            return self._fallback_crop_recommendations()
    
    def _build_disease_prompt(self, disease_info: Dict, farmer_context: Dict = None) -> str:
        """Build comprehensive prompt for disease recommendations"""
        
        base_prompt = f"""
        As an expert plant pathologist and agricultural advisor, provide comprehensive treatment recommendations for:
        
        Disease Detected: {disease_info.get('disease', 'Unknown')}
        Plant/Crop: {disease_info.get('plant', 'Unknown')}
        Confidence Level: {disease_info.get('confidence', 0)}%
        Severity: {disease_info.get('severity', 'Unknown')}
        
        """
        
        if farmer_context:
            base_prompt += f"""
        Farmer Context:
        - Location: {farmer_context.get('location', 'Unknown')}
        - Farm Size: {farmer_context.get('farm_size', 'Unknown')}
        - Climate Zone: {farmer_context.get('climate', 'Unknown')}
        - Previous Treatments: {farmer_context.get('treatment_history', 'None')}
        
        """
        
        base_prompt += """
        Please provide:
        1. **Immediate Actions** (next 24-48 hours)
        2. **Treatment Plan** (specific fungicides/pesticides with dosages)
        3. **Cultural Practices** (pruning, spacing, sanitation)
        4. **Prevention Strategies** (future occurrences)
        5. **Organic Alternatives** (if farmer prefers)
        6. **Cost Estimation** (treatment costs)
        7. **Timeline** (expected recovery period)
        8. **Monitoring Checklist** (signs of improvement/worsening)
        9. **Emergency Contacts** (local agricultural extension)
        10. **Follow-up Recommendations** (post-treatment care)
        
        Consider:
        - Local availability of treatments
        - Cost-effectiveness for small farmers
        - Environmental impact
        - Resistance management
        - Integration with other crops
        
        Format as structured JSON with clear action items.
        """
        
        return base_prompt
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI GPT API"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert agricultural advisor with deep knowledge of plant pathology, crop management, and sustainable farming practices."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {e}")
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Google Gemini API"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API call failed: {e}")
    
    def _call_local_model(self, prompt: str) -> str:
        """Call local AI model (Ollama, Hugging Face, etc.)"""
        # Placeholder for local model integration
        # You can integrate with Ollama, Hugging Face Transformers, etc.
        return "Local model response placeholder"
    
    def _parse_disease_response(self, response: str) -> Dict:
        """Parse AI response for disease recommendations"""
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                return json.loads(response)
            else:
                # Parse structured text response
                return {
                    "ai_recommendations": response,
                    "generated_at": datetime.now().isoformat(),
                    "confidence": "high",
                    "source": f"AI_{self.provider}"
                }
        except Exception as e:
            return {
                "ai_recommendations": response,
                "parse_error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def _parse_crop_response(self, response: str) -> Dict:
        """Parse AI response for crop recommendations"""
        try:
            if response.strip().startswith('{'):
                return json.loads(response)
            else:
                return {
                    "crop_recommendations": response,
                    "generated_at": datetime.now().isoformat(),
                    "source": f"AI_{self.provider}"
                }
        except Exception as e:
            return {
                "crop_recommendations": response,
                "parse_error": str(e),
                "generated_at": datetime.now().isoformat()
            }
    
    def _fallback_recommendations(self, disease_info: Dict) -> Dict:
        """Fallback recommendations when AI fails"""
        return {
            "recommendations": [
                "Consult with local agricultural extension officer",
                "Remove affected plant parts immediately",
                "Apply appropriate fungicide as per local guidelines",
                "Improve air circulation around plants",
                "Monitor other plants for similar symptoms"
            ],
            "source": "fallback_system",
            "note": "AI recommendations temporarily unavailable"
        }
    
    def _fallback_crop_recommendations(self) -> Dict:
        """Fallback crop recommendations when AI fails"""
        return {
            "recommendations": [
                "Consult local agricultural department for crop selection",
                "Consider climate-appropriate varieties",
                "Check soil health before planting",
                "Review market demand in your area",
                "Start with crops you have experience growing"
            ],
            "source": "fallback_system",
            "note": "AI recommendations temporarily unavailable"
        }


class AIEnhancedChatbot:
    """
    Generative AI-powered chatbot for agricultural assistance
    Provides contextual, intelligent responses to farmer queries
    """
    
    def __init__(self, ai_engine: AIRecommendationEngine):
        self.ai_engine = ai_engine
        self.conversation_history = {}
        self.agricultural_context = self._load_agricultural_context()
    
    def _load_agricultural_context(self) -> Dict:
        """Load agricultural knowledge base for context"""
        return {
            "crops": ["rice", "wheat", "maize", "tomato", "potato", "onion", "cotton", "sugarcane"],
            "seasons": {
                "kharif": "June-October (Monsoon season)",
                "rabi": "November-April (Winter season)", 
                "zaid": "April-June (Summer season)"
            },
            "common_diseases": ["blight", "rust", "mosaic", "wilt", "rot", "mildew"],
            "farming_practices": ["irrigation", "fertilization", "pest_control", "harvesting", "storage"],
            "government_schemes": ["PM-KISAN", "PMFBY", "Soil Health Card", "e-NAM"]
        }
    
    def generate_response(self, message: str, user_id: str, language: str = "en", context: Dict = None) -> Dict:
        """
        Generate AI-powered response to user query
        
        Args:
            message: User's question/message
            user_id: User identifier for conversation tracking
            language: Response language (en, hi, ta)
            context: Additional context (location, crops, etc.)
            
        Returns:
            AI-generated response with metadata
        """
        
        # Build conversation context
        conversation_context = self._get_conversation_context(user_id)
        
        # Create enhanced prompt
        prompt = self._build_chatbot_prompt(message, language, context, conversation_context)
        
        try:
            if self.ai_engine.provider == "openai":
                response = self.ai_engine._call_openai(prompt)
            elif self.ai_engine.provider == "gemini":
                response = self.ai_engine._call_gemini(prompt)
            else:
                response = self.ai_engine._call_local_model(prompt)
            
            # Update conversation history
            self._update_conversation_history(user_id, message, response)
            
            return {
                "response": response,
                "language": language,
                "context_used": bool(context),
                "conversation_turn": len(conversation_context),
                "generated_at": datetime.now().isoformat(),
                "ai_powered": True
            }
            
        except Exception as e:
            logging.error(f"AI chatbot response generation failed: {e}")
            return self._fallback_response(message, language)
    
    def _build_chatbot_prompt(self, message: str, language: str, context: Dict, conversation: List) -> str:
        """Build comprehensive chatbot prompt"""
        
        system_prompt = f"""
        You are AgriBot, an expert agricultural assistant for AgroMitra app. You help farmers with:
        - Crop selection and planning
        - Disease diagnosis and treatment
        - Irrigation and water management
        - Fertilizer recommendations
        - Market prices and selling advice
        - Government schemes and subsidies
        - Weather and climate guidance
        - Organic farming practices
        
        Response Language: {language} ({'English' if language == 'en' else 'Hindi' if language == 'hi' else 'Tamil'})
        
        Guidelines:
        - Be practical and actionable
        - Consider Indian farming conditions
        - Suggest cost-effective solutions
        - Include local resource availability
        - Be empathetic to farmer challenges
        - Provide step-by-step guidance when needed
        
        """
        
        if context:
            system_prompt += f"""
        Farmer Context:
        - Location: {context.get('location', 'Unknown')}
        - Farm Size: {context.get('farm_size', 'Unknown')}
        - Main Crops: {context.get('crops', 'Unknown')}
        - Experience: {context.get('experience', 'Unknown')}
        
        """
        
        if conversation:
            system_prompt += """
        Previous Conversation:
        """
            for turn in conversation[-3:]:  # Last 3 turns for context
                system_prompt += f"User: {turn['user']}\nBot: {turn['bot']}\n"
        
        user_prompt = f"""
        Farmer's Question: {message}
        
        Please provide a helpful, practical response in {language} language.
        If the question is about:
        - Disease: Suggest using the disease detection feature
        - Prices: Refer to price prediction tool
        - Schemes: Direct to government schemes section
        - General advice: Provide detailed guidance
        
        Keep response conversational but informative.
        """
        
        return system_prompt + user_prompt
    
    def _get_conversation_context(self, user_id: str) -> List:
        """Get recent conversation history for context"""
        return self.conversation_history.get(user_id, [])
    
    def _update_conversation_history(self, user_id: str, user_message: str, bot_response: str):
        """Update conversation history"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "user": user_message,
            "bot": bot_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 10 turns
        self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
    
    def _fallback_response(self, message: str, language: str) -> Dict:
        """Fallback response when AI fails"""
        fallback_responses = {
            "en": "I'm here to help with your farming questions! Due to technical issues, I'm using basic responses. Please try asking about specific topics like crop diseases, irrigation, or government schemes.",
            "hi": "मैं आपके कृषि प्रश्नों में मदद के लिए यहाँ हूँ! तकनीकी समस्या के कारण, मैं बुनियादी उत्तर दे रहा हूँ। कृपया फसल रोग, सिंचाई, या सरकारी योजनाओं जैसे विशिष्ट विषयों के बारे में पूछें।",
            "ta": "உங்கள் விவசாய கேள்விகளுக்கு உதவ நான் இங்கே இருக்கிறேன்! தொழில்நுட்ப சிக்கல்களால், நான் அடிப்படை பதில்களைப் பயன்படுத்துகிறேன். தயவுசெய்து பயிர் நோய்கள், நீர்ப்பாசனம் அல்லது அரசாங்க திட்டங்கள் போன்ற குறிப்பிட்ட தலைப்புகளைப் பற்றி கேளுங்கள்."
        }
        
        return {
            "response": fallback_responses.get(language, fallback_responses["en"]),
            "language": language,
            "ai_powered": False,
            "fallback": True,
            "generated_at": datetime.now().isoformat()
        }


# Configuration for different AI providers
AI_PROVIDERS_CONFIG = {
    "openai": {
        "model": "gpt-4",
        "api_key_env": "OPENAI_API_KEY",
        "cost_per_token": 0.00003  # Approximate
    },
    "gemini": {
        "model": "gemini-pro",
        "api_key_env": "GEMINI_API_KEY",
        "cost_per_token": 0.00025
    },
    "local": {
        "model": "llama2",
        "endpoint": "http://localhost:11434/api/generate",
        "cost_per_token": 0  # Free for local
    }
}

# Usage example functions
def initialize_ai_system(provider="gemini"):
    """Initialize AI system with preferred provider"""
    try:
        ai_engine = AIRecommendationEngine(provider=provider)
        chatbot = AIEnhancedChatbot(ai_engine)
        return ai_engine, chatbot
    except Exception as e:
        logging.error(f"Failed to initialize AI system: {e}")
        return None, None

def enhance_disease_detection_with_ai(disease_result: Dict, farmer_context: Dict = None):
    """Enhance disease detection results with AI recommendations"""
    ai_engine, _ = initialize_ai_system()
    if ai_engine:
        enhanced_recommendations = ai_engine.generate_disease_recommendations(
            disease_result, farmer_context
        )
        return {**disease_result, "ai_enhanced": enhanced_recommendations}
    return disease_result

def get_ai_crop_advice(farmer_profile: Dict, season: str, location: Dict):
    """Get AI-powered crop selection advice"""
    ai_engine, _ = initialize_ai_system()
    if ai_engine:
        return ai_engine.generate_crop_recommendations(farmer_profile, season, location)
    return {"error": "AI system not available"}

def chat_with_ai_bot(message: str, user_id: str, language: str = "en", context: Dict = None):
    """Chat with AI-enhanced AgriBot"""
    _, chatbot = initialize_ai_system()
    if chatbot:
        return chatbot.generate_response(message, user_id, language, context)
    return {"error": "AI chatbot not available"}