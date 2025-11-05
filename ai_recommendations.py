from flask import Blueprint, request, jsonify
from datetime import datetime
import json

# Import AI integration module
try:
    from ai_integration import get_ai_crop_advice
    AI_RECOMMENDATIONS_AVAILABLE = True
except ImportError:
    AI_RECOMMENDATIONS_AVAILABLE = False
    print("AI recommendations module not available - using basic advice")

ai_recommendations_bp = Blueprint('ai_recommendations', __name__)

@ai_recommendations_bp.route('/crop-advice', methods=['POST'])
def get_crop_recommendations():
    """
    Get AI-powered crop selection recommendations
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'Request data is required'}), 400
    
    # Extract farmer profile information
    farmer_profile = {
        'farm_size': data.get('farm_size', 'Unknown'),
        'location': data.get('location', 'Unknown'),
        'experience': data.get('experience', 'Unknown'),
        'crops_grown': data.get('previous_crops', 'Unknown'),
        'soil_type': data.get('soil_type', 'Unknown'),
        'irrigation_access': data.get('irrigation', 'Unknown'),
        'budget': data.get('budget', 'Unknown')
    }
    
    season = data.get('season', 'current')
    location_details = {
        'state': data.get('state', 'Unknown'),
        'district': data.get('district', 'Unknown'),
        'climate_zone': data.get('climate_zone', 'Unknown'),
        'rainfall': data.get('average_rainfall', 'Unknown'),
        'temperature': data.get('average_temperature', 'Unknown')
    }
    
    # Try AI-powered recommendations first
    if AI_RECOMMENDATIONS_AVAILABLE:
        try:
            ai_advice = get_ai_crop_advice(farmer_profile, season, location_details)
            if not ai_advice.get('error'):
                return jsonify({
                    'success': True,
                    'recommendations': ai_advice,
                    'ai_powered': True,
                    'farmer_profile': farmer_profile,
                    'season': season,
                    'location': location_details,
                    'generated_at': datetime.now().isoformat()
                }), 200
        except Exception as e:
            print(f"AI crop recommendations error: {e}")
    
    # Fallback to basic recommendations
    basic_recommendations = get_basic_crop_recommendations(farmer_profile, season, location_details)
    
    return jsonify({
        'success': True,
        'recommendations': basic_recommendations,
        'ai_powered': False,
        'fallback_used': True,
        'farmer_profile': farmer_profile,
        'season': season,
        'location': location_details,
        'generated_at': datetime.now().isoformat()
    }), 200

@ai_recommendations_bp.route('/seasonal-calendar', methods=['POST'])
def get_seasonal_calendar():
    """
    Get AI-powered seasonal farming calendar
    """
    data = request.get_json()
    
    location = data.get('location', 'India')
    crops = data.get('crops', ['rice', 'wheat'])
    
    # Basic seasonal calendar (can be enhanced with AI)
    calendar = {
        'kharif_season': {
            'months': 'June-October',
            'crops': ['Rice', 'Cotton', 'Sugarcane', 'Pulses'],
            'activities': [
                'Sowing: June-July',
                'Weeding: July-August', 
                'Harvesting: September-October'
            ]
        },
        'rabi_season': {
            'months': 'November-April',
            'crops': ['Wheat', 'Barley', 'Peas', 'Gram'],
            'activities': [
                'Sowing: November-December',
                'Irrigation: January-February',
                'Harvesting: March-April'
            ]
        },
        'zaid_season': {
            'months': 'April-June',
            'crops': ['Fodder', 'Vegetables', 'Watermelon'],
            'activities': [
                'Sowing: April',
                'Intensive irrigation needed',
                'Harvesting: June'
            ]
        }
    }
    
    return jsonify({
        'success': True,
        'seasonal_calendar': calendar,
        'location': location,
        'ai_enhanced': False,
        'generated_at': datetime.now().isoformat()
    }), 200

@ai_recommendations_bp.route('/personalized-tips', methods=['POST'])
def get_personalized_tips():
    """
    Get AI-powered personalized farming tips
    """
    data = request.get_json()
    
    farmer_data = {
        'experience_level': data.get('experience_level', 'beginner'),
        'farm_size': data.get('farm_size', 'small'),
        'main_crops': data.get('main_crops', []),
        'challenges': data.get('challenges', []),
        'goals': data.get('goals', [])
    }
    
    # Generate basic tips (can be enhanced with AI)
    tips = generate_basic_farming_tips(farmer_data)
    
    return jsonify({
        'success': True,
        'personalized_tips': tips,
        'farmer_profile': farmer_data,
        'ai_powered': False,
        'generated_at': datetime.now().isoformat()
    }), 200

def get_basic_crop_recommendations(farmer_profile, season, location):
    """
    Basic crop recommendations when AI is not available
    """
    
    farm_size = farmer_profile.get('farm_size', 'Unknown')
    state = location.get('state', 'Unknown').lower()
    
    # Basic recommendations based on common patterns
    recommendations = {
        'top_crops': [],
        'reasoning': [],
        'market_potential': 'Moderate',
        'investment_required': 'Medium',
        'risk_level': 'Medium'
    }
    
    # Season-based recommendations
    if season.lower() in ['kharif', 'monsoon']:
        recommendations['top_crops'] = ['Rice', 'Cotton', 'Sugarcane', 'Maize', 'Pulses']
        recommendations['reasoning'].append('Monsoon season suitable for water-intensive crops')
    elif season.lower() in ['rabi', 'winter']:
        recommendations['top_crops'] = ['Wheat', 'Barley', 'Gram', 'Peas', 'Mustard']
        recommendations['reasoning'].append('Winter season ideal for grain crops')
    elif season.lower() in ['zaid', 'summer']:
        recommendations['top_crops'] = ['Fodder crops', 'Vegetables', 'Watermelon', 'Cucumber']
        recommendations['reasoning'].append('Summer season requires heat-tolerant crops')
    else:
        recommendations['top_crops'] = ['Rice', 'Wheat', 'Vegetables', 'Pulses']
        recommendations['reasoning'].append('Year-round suitable crops')
    
    # State-specific adjustments
    if 'punjab' in state or 'haryana' in state:
        recommendations['top_crops'].extend(['Wheat', 'Rice'])
        recommendations['reasoning'].append('Punjab/Haryana: Wheat-Rice belt')
    elif 'maharashtra' in state:
        recommendations['top_crops'].extend(['Cotton', 'Sugarcane', 'Onion'])
        recommendations['reasoning'].append('Maharashtra: Cotton and horticulture state')
    elif 'kerala' in state or 'tamil nadu' in state:
        recommendations['top_crops'].extend(['Rice', 'Coconut', 'Spices'])
        recommendations['reasoning'].append('South India: Rice and plantation crops')
    
    # Farm size adjustments
    if 'small' in str(farm_size).lower() or ('2' in str(farm_size) and 'acre' in str(farm_size).lower()):
        recommendations['top_crops'] = ['Vegetables', 'Pulses', 'Spices', 'Flowers']
        recommendations['reasoning'].append('Small farms: High-value crops recommended')
        recommendations['investment_required'] = 'Low to Medium'
    
    return recommendations

def generate_basic_farming_tips(farmer_data):
    """
    Generate basic farming tips based on farmer profile
    """
    experience = farmer_data.get('experience_level', 'beginner')
    farm_size = farmer_data.get('farm_size', 'small')
    
    tips = {
        'soil_management': [
            'Test soil pH regularly',
            'Add organic matter like compost',
            'Practice crop rotation',
            'Use cover crops to improve soil health'
        ],
        'water_management': [
            'Install drip irrigation for efficiency',
            'Harvest rainwater when possible',
            'Mulch around plants to retain moisture',
            'Water early morning or evening'
        ],
        'pest_management': [
            'Practice integrated pest management (IPM)',
            'Use neem-based organic pesticides',
            'Encourage beneficial insects',
            'Regular monitoring of crops'
        ],
        'market_strategies': [
            'Research local market prices',
            'Consider contract farming',
            'Build relationships with buyers',
            'Value addition through processing'
        ]
    }
    
    if experience == 'beginner':
        tips['beginner_focus'] = [
            'Start with easy-to-grow crops',
            'Learn from experienced farmers',
            'Attend agricultural training programs',
            'Keep detailed farming records'
        ]
    
    return tips