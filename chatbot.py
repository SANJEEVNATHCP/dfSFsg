from flask import Blueprint, request, jsonify
import json
from datetime import datetime

# Import AI integration module
try:
    from ai_integration import chat_with_ai_bot
    AI_CHATBOT_AVAILABLE = True
    print("✅ AI chatbot module loaded successfully!")
except ImportError as e:
    AI_CHATBOT_AVAILABLE = False
    print(f"AI chatbot module not available - using rule-based responses. Error: {e}")

chatbot_bp = Blueprint('chatbot', __name__)

# Agricultural knowledge base for chatbot
AGRICULTURE_KB = {
    'disease': {
        'keywords': ['disease', 'pest', 'infection', 'spots', 'yellowing', 'wilting'],
        'responses': {
            'en': 'I can help you identify plant diseases. Please upload a photo of the affected plant using our disease detection feature. Common diseases include blight, rust, and fungal infections.',
            'hi': 'मैं पौधों की बीमारियों की पहचान करने में आपकी मदद कर सकता हूं। कृपया हमारे रोग पहचान सुविधा का उपयोग करके प्रभावित पौधे की तस्वीर अपलोड करें।',
            'ta': 'செடி நோய்களை அடையாளம் காண நான் உங்களுக்கு உதவ முடியும். எங்கள் நோய் கண்டறிதல் அம்சத்தைப் பயன்படுத்தி பாதிக்கப்பட்ட செடியின் புகைப்படத்தை பதிவேற்றவும்.'
        }
    },
    'price': {
        'keywords': ['price', 'rate', 'market', 'sell', 'value', 'cost'],
        'responses': {
            'en': 'I can help you check current market prices and predict future prices. Visit the Price Prediction section for detailed price analysis of various crops.',
            'hi': 'मैं आपको वर्तमान बाजार मूल्य जांचने और भविष्य की कीमतों का अनुमान लगाने में मदद कर सकता हूं। विभिन्न फसलों के विस्तृत मूल्य विश्लेषण के लिए मूल्य पूर्वानुमान अनुभाग देखें।',
            'ta': 'தற்போதைய சந்தை விலைகளை சரிபார்க்கவும் எதிர்கால விலைகளை கணிக்கவும் நான் உங்களுக்கு உதவ முடியும். பல்வேறு பயிர்களின் விரிவான விலை பகுப்பாய்வுக்கு விலை முன்னறிவிப்பு பிரிவைப் பார்வையிடவும்.'
        }
    },
    'irrigation': {
        'keywords': ['water', 'irrigation', 'drip', 'watering', 'rainfall'],
        'responses': {
            'en': 'For water management, consider drip irrigation for efficient water use. Water crops early morning or evening. Check soil moisture before watering. The PMKSY scheme provides support for irrigation.',
            'hi': 'जल प्रबंधन के लिए, कुशल पानी उपयोग के लिए ड्रिप सिंचाई पर विचार करें। सुबह जल्दी या शाम को फसलों को पानी दें। पानी देने से पहले मिट्टी की नमी जांचें।',
            'ta': 'நீர் மேலாண்மைக்கு, திறமையான நீர் பயன்பாட்டிற்கு சொட்டு நீர் பாசனத்தை பரிசீலிக்கவும். காலை அல்லது மாலை பயிர்களுக்கு நீர் பாய்ச்சவும்.'
        }
    },
    'fertilizer': {
        'keywords': ['fertilizer', 'manure', 'nutrients', 'nitrogen', 'organic'],
        'responses': {
            'en': 'Use soil health cards to determine nutrient requirements. Apply fertilizers based on soil test reports. Organic options include compost, vermicompost, and green manure. NPK ratios depend on crop type.',
            'hi': 'पोषक तत्वों की आवश्यकता निर्धारित करने के लिए मृदा स्वास्थ्य कार्ड का उपयोग करें। मिट्टी परीक्षण रिपोर्ट के आधार पर उर्वरक लागू करें। जैविक विकल्पों में खाद, वर्मीकम्पोस्ट शामिल हैं।',
            'ta': 'ஊட்டச்சத்து தேவைகளை தீர்மானிக்க மண் ஆரோக்கிய அட்டைகளைப் பயன்படுத்தவும். மண் சோதனை அறிக்கைகளின் அடிப்படையில் உரங்களைப் பயன்படுத்தவும்.'
        }
    },
    'schemes': {
        'keywords': ['scheme', 'subsidy', 'government', 'loan', 'support', 'yojana'],
        'responses': {
            'en': 'Check the Schemes section for government programs like PM-KISAN (₹6000/year), PMFBY (crop insurance), KCC (credit card), and more. I can help you check eligibility.',
            'hi': 'पीएम-किसान (₹6000/वर्ष), पीएमएफबीवाई (फसल बीमा), केसीसी (क्रेडिट कार्ड) जैसी सरकारी योजनाओं के लिए योजना अनुभाग देखें।',
            'ta': 'PM-KISAN (₹6000/ஆண்டு), PMFBY (பயிர் காப்பீடு), KCC (கடன் அட்டை) போன்ற அரசாங்க திட்டங்களுக்கு திட்டங்கள் பிரிவைச் சரிபார்க்கவும்.'
        }
    },
    'weather': {
        'keywords': ['weather', 'rain', 'temperature', 'climate', 'season'],
        'responses': {
            'en': 'Monitor local weather forecasts regularly. Different crops require different climate conditions. Kharif crops need good monsoon rainfall, while Rabi crops need cooler temperatures.',
            'hi': 'स्थानीय मौसम पूर्वानुमानों की नियमित निगरानी करें। विभिन्न फसलों को अलग-अलग जलवायु परिस्थितियों की आवश्यकता होती है।',
            'ta': 'உள்ளூர் வானிலை முன்னறிவிப்புகளை தவறாமல் கண்காணிக்கவும். வெவ்வேறு பயிர்களுக்கு வெவ்வேறு காலநிலை நிலைமைகள் தேவை.'
        }
    },
    'seed': {
        'keywords': ['seed', 'variety', 'hybrid', 'planting', 'sowing'],
        'responses': {
            'en': 'Always use certified seeds from authorized dealers. Choose varieties suitable for your region. Hybrid seeds offer better yield but require proper care. Check seed treatment requirements before sowing.',
            'hi': 'हमेशा अधिकृत डीलरों से प्रमाणित बीज का उपयोग करें। अपने क्षेत्र के लिए उपयुक्त किस्मों का चयन करें।',
            'ta': 'அங்கீகரிக்கப்பட்ட விற்பனையாளர்களிடமிருந்து எப்போதும் சான்றளிக்கப்பட்ட விதைகளைப் பயன்படுத்தவும்.'
        }
    },
    'organic': {
        'keywords': ['organic', 'natural', 'chemical-free', 'bio'],
        'responses': {
            'en': 'Organic farming is supported by PKVY scheme (₹50,000/hectare). Use organic manure, biopesticides, and natural farming methods. Certification required for organic label. Market premium available.',
            'hi': 'जैविक खेती PKVY योजना (₹50,000/हेक्टेयर) द्वारा समर्थित है। जैविक खाद, जैव कीटनाशकों का उपयोग करें।',
            'ta': 'இயற்கை விவசாயம் PKVY திட்டத்தால் ஆதரிக்கப்படுகிறது (₹50,000/ஹெக்டேர்).'
        }
    }
}

def get_chatbot_response(message, language='en'):
    """
    Generate chatbot response based on message and language
    """
    message_lower = message.lower()
    
    # Check for greetings
    greetings = ['hello', 'hi', 'hey', 'namaste', 'vanakkam']
    if any(greeting in message_lower for greeting in greetings):
        responses = {
            'en': 'Hello! I am your agricultural assistant. I can help you with crop diseases, market prices, government schemes, and farming advice. How can I assist you today?',
            'hi': 'नमस्ते! मैं आपका कृषि सहायक हूं। मैं फसल रोगों, बाजार मूल्यों, सरकारी योजनाओं और खेती सलाह में आपकी मदद कर सकता हूं।',
            'ta': 'வணக்கம்! நான் உங்கள் விவசாய உதவியாளர். பயிர் நோய்கள், சந்தை விலைகள், அரசு திட்டங்கள் மற்றும் விவசாய ஆலோசனைகளில் நான் உங்களுக்கு உதவ முடியும்.'
        }
        return responses.get(language, responses['en'])
    
    # Check knowledge base
    for topic, data in AGRICULTURE_KB.items():
        if any(keyword in message_lower for keyword in data['keywords']):
            return data['responses'].get(language, data['responses']['en'])
    
    # Default response
    default_responses = {
        'en': 'I can help you with: 1) Plant disease detection, 2) Price predictions, 3) Government schemes, 4) Farming advice, 5) Marketplace. Could you please be more specific about what you need help with?',
        'hi': 'मैं आपकी मदद कर सकता हूं: 1) पौधों की बीमारी का पता लगाना, 2) मूल्य पूर्वानुमान, 3) सरकारी योजनाएं, 4) खेती की सलाह, 5) बाजार।',
        'ta': 'நான் உங்களுக்கு உதவ முடியும்: 1) தாவர நோய் கண்டறிதல், 2) விலை கணிப்புகள், 3) அரசு திட்டங்கள், 4) விவசாய ஆலோசனை, 5) சந்தை.'
    }
    return default_responses.get(language, default_responses['en'])

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """
    Chat with AI-enhanced agricultural advisory bot
    """
    data = request.get_json()
    
    if not data or 'message' not in data:
        return jsonify({'success': False, 'error': 'Message is required'}), 400
    
    message = data['message']
    language = data.get('language', 'en')
    user_id = data.get('user_id', 'anonymous')
    
    # Get farmer context for personalized responses
    farmer_context = {
        'location': data.get('location', 'Unknown'),
        'crops': data.get('crops', 'Unknown'),
        'farm_size': data.get('farm_size', 'Unknown'),
        'experience': data.get('experience', 'Unknown')
    }
    
    # Try AI-enhanced response first
    if AI_CHATBOT_AVAILABLE:
        try:
            ai_response = chat_with_ai_bot(message, user_id, language, farmer_context)
            if not ai_response.get('error'):
                return jsonify({
                    'success': True,
                    'message': message,
                    'response': ai_response['response'],
                    'language': language,
                    'ai_powered': ai_response.get('ai_powered', True),
                    'conversation_turn': ai_response.get('conversation_turn', 1),
                    'timestamp': str(datetime.now())
                }), 200
        except Exception as e:
            print(f"AI chatbot error: {e}")
    
    # Fallback to rule-based response
    response = get_chatbot_response(message, language)
    
    return jsonify({
        'success': True,
        'message': message,
        'response': response,
        'language': language,
        'ai_powered': False,
        'fallback_used': True,
        'timestamp': str(datetime.now())
    }), 200

@chatbot_bp.route('/topics', methods=['GET'])
def get_topics():
    """
    Get available chat topics
    """
    topics = {
        'en': list(AGRICULTURE_KB.keys()),
        'topics_details': {
            'disease': 'Plant disease diagnosis and treatment',
            'price': 'Market prices and predictions',
            'irrigation': 'Water management and irrigation',
            'fertilizer': 'Soil health and fertilization',
            'schemes': 'Government schemes and subsidies',
            'weather': 'Weather and climate information',
            'seed': 'Seed selection and planting',
            'organic': 'Organic farming practices'
        }
    }
    
    return jsonify({
        'success': True,
        'topics': topics
    }), 200

@chatbot_bp.route('/languages', methods=['GET'])
def get_languages():
    """
    Get supported languages
    """
    languages = [
        {'code': 'en', 'name': 'English'},
        {'code': 'hi', 'name': 'हिन्दी (Hindi)'},
        {'code': 'ta', 'name': 'தமிழ் (Tamil)'}
    ]
    
    return jsonify({
        'success': True,
        'languages': languages
    }), 200
