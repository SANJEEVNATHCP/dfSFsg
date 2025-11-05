from flask import Blueprint, request, jsonify
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import os

price_bp = Blueprint('price', __name__)

# Indian States and their major agricultural markets
INDIAN_STATES_MARKETS = {
    'Andhra Pradesh': ['Vijayawada', 'Visakhapatnam', 'Guntur', 'Tirupati', 'Rajahmundry'],
    'Arunachal Pradesh': ['Itanagar', 'Naharlagun', 'Pasighat', 'Tezpur'],
    'Assam': ['Guwahati', 'Dibrugarh', 'Silchar', 'Jorhat', 'Tezpur'],
    'Bihar': ['Patna', 'Muzaffarpur', 'Bhagalpur', 'Darbhanga', 'Gaya'],
    'Chhattisgarh': ['Raipur', 'Bilaspur', 'Durg', 'Korba', 'Jagdalpur'],
    'Goa': ['Panaji', 'Margao', 'Vasco da Gama', 'Mapusa'],
    'Gujarat': ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot', 'Junagadh'],
    'Haryana': ['Faridabad', 'Gurgaon', 'Panipat', 'Ambala', 'Karnal'],
    'Himachal Pradesh': ['Shimla', 'Mandi', 'Kullu', 'Kangra', 'Solan'],
    'Jharkhand': ['Ranchi', 'Jamshedpur', 'Dhanbad', 'Bokaro', 'Deoghar'],
    'Karnataka': ['Bangalore', 'Mysore', 'Hubli', 'Belgaum', 'Mangalore'],
    'Kerala': ['Thiruvananthapuram', 'Kochi', 'Kozhikode', 'Thrissur', 'Kollam'],
    'Madhya Pradesh': ['Bhopal', 'Indore', 'Gwalior', 'Jabalpur', 'Ujjain'],
    'Maharashtra': ['Mumbai', 'Pune', 'Nagpur', 'Nashik', 'Aurangabad'],
    'Manipur': ['Imphal', 'Thoubal', 'Bishnupur', 'Churachandpur'],
    'Meghalaya': ['Shillong', 'Tura', 'Jowai', 'Nongstoin'],
    'Mizoram': ['Aizawl', 'Lunglei', 'Saiha', 'Champhai'],
    'Nagaland': ['Kohima', 'Dimapur', 'Mokokchung', 'Tuensang'],
    'Odisha': ['Bhubaneswar', 'Cuttack', 'Rourkela', 'Berhampur', 'Sambalpur'],
    'Punjab': ['Ludhiana', 'Amritsar', 'Jalandhar', 'Patiala', 'Bathinda'],
    'Rajasthan': ['Jaipur', 'Jodhpur', 'Kota', 'Bikaner', 'Udaipur'],
    'Sikkim': ['Gangtok', 'Namchi', 'Gyalshing', 'Mangan'],
    'Tamil Nadu': ['Chennai', 'Coimbatore', 'Madurai', 'Tiruchirappalli', 'Salem'],
    'Telangana': ['Hyderabad', 'Warangal', 'Nizamabad', 'Karimnagar', 'Khammam'],
    'Tripura': ['Agartala', 'Dharmanagar', 'Udaipur', 'Kailashahar'],
    'Uttar Pradesh': ['Lucknow', 'Kanpur', 'Agra', 'Varanasi', 'Meerut'],
    'Uttarakhand': ['Dehradun', 'Haridwar', 'Roorkee', 'Haldwani', 'Rishikesh'],
    'West Bengal': ['Kolkata', 'Howrah', 'Durgapur', 'Asansol', 'Siliguri'],
    # Union Territories
    'Delhi': ['New Delhi', 'Azadpur Mandi', 'Okhla', 'Ghazipur'],
    'Chandigarh': ['Chandigarh Sector 26', 'Chandigarh Sector 19'],
    'Puducherry': ['Puducherry', 'Karaikal', 'Mahe', 'Yanam']
}

# Market-specific price variations (percentage difference from base price)
MARKET_PRICE_VARIATIONS = {
    'Mumbai': {'factor': 1.15, 'reason': 'Metropolitan demand'},
    'Delhi': {'factor': 1.12, 'reason': 'Capital city premium'},
    'Bangalore': {'factor': 1.10, 'reason': 'IT hub demand'},
    'Chennai': {'factor': 1.08, 'reason': 'Port city advantage'},
    'Pune': {'factor': 1.06, 'reason': 'Industrial center'},
    'Hyderabad': {'factor': 1.05, 'reason': 'Tech city growth'},
    'Kolkata': {'factor': 1.04, 'reason': 'Eastern hub'},
    'Ahmedabad': {'factor': 1.03, 'reason': 'Commercial center'},
    # Agricultural markets with lower prices due to proximity to production
    'Guntur': {'factor': 0.92, 'reason': 'Chili production hub'},
    'Nashik': {'factor': 0.94, 'reason': 'Onion and grape center'},
    'Kota': {'factor': 0.90, 'reason': 'Agricultural belt'},
    'Mandi': {'factor': 0.88, 'reason': 'Apple production area'},
    'Muzaffarpur': {'factor': 0.85, 'reason': 'Litchi belt'},
    'Malda': {'factor': 0.87, 'reason': 'Mango hub'},
    'Salem': {'factor': 0.91, 'reason': 'Turmeric market'},
    'Indore': {'factor': 0.93, 'reason': 'Soybean center'}
}

# Sample historical price data for common crops
SAMPLE_PRICE_DATA = {
    # Fruits
    'apples': {'current': 80, 'trend': 'up', 'prediction_30days': 85},
    'bananas': {'current': 40, 'trend': 'stable', 'prediction_30days': 40},
    'grapes': {'current': 70, 'trend': 'up', 'prediction_30days': 75},
    'lemons': {'current': 45, 'trend': 'stable', 'prediction_30days': 45},
    'limes': {'current': 50, 'trend': 'up', 'prediction_30days': 53},
    'mangoes': {'current': 60, 'trend': 'up', 'prediction_30days': 65},
    'oranges': {'current': 55, 'trend': 'stable', 'prediction_30days': 55},
    'papayas': {'current': 35, 'trend': 'down', 'prediction_30days': 33},
    'pears': {'current': 85, 'trend': 'up', 'prediction_30days': 88},
    'pineapples': {'current': 65, 'trend': 'stable', 'prediction_30days': 65},
    'strawberries': {'current': 120, 'trend': 'up', 'prediction_30days': 125},
    
    # Vegetables
    'asparagus': {'current': 150, 'trend': 'up', 'prediction_30days': 155},
    'broccoli_bunches': {'current': 40, 'trend': 'stable', 'prediction_30days': 40},
    'broccoli_crowns': {'current': 45, 'trend': 'stable', 'prediction_30days': 45},
    'carrots': {'current': 30, 'trend': 'stable', 'prediction_30days': 30},
    'cauliflower': {'current': 35, 'trend': 'up', 'prediction_30days': 37},
    'celery': {'current': 32, 'trend': 'stable', 'prediction_30days': 32},
    'green_leaf_lettuce': {'current': 25, 'trend': 'down', 'prediction_30days': 23},
    'iceberg_lettuce': {'current': 28, 'trend': 'stable', 'prediction_30days': 28},
    'potatoes': {'current': 20, 'trend': 'stable', 'prediction_30days': 20},
    'red_leaf_lettuce': {'current': 26, 'trend': 'stable', 'prediction_30days': 26},
    'romaine_lettuce': {'current': 27, 'trend': 'up', 'prediction_30days': 29},
    'tomatoes': {'current': 25, 'trend': 'up', 'prediction_30days': 28}
}

class PricePredictor:
    def __init__(self):
        self.kaggle_kernel = 'missahhh3074/visualisation-of-fruits-and-veggies'
        
    def fetch_kaggle_data(self):
        """
        Fetch data from Kaggle kernel output
        """
        try:
            # This would typically use Kaggle API
            # For now, using sample data
            return SAMPLE_PRICE_DATA
        except Exception as e:
            print(f"Error fetching Kaggle data: {e}")
            return SAMPLE_PRICE_DATA
    
    def predict_price(self, crop_name, days=30, state=None, market=None):
        """
        Predict future price for a crop with location-specific adjustments
        """
        crop_name = crop_name.lower()
        data = self.fetch_kaggle_data()
        
        if crop_name in data:
            crop_data = data[crop_name]
            
            # Apply market-specific price adjustments
            market_factor = 1.0
            market_info = ""
            if market and market in MARKET_PRICE_VARIATIONS:
                market_factor = MARKET_PRICE_VARIATIONS[market]['factor']
                market_info = MARKET_PRICE_VARIATIONS[market]['reason']
            elif state and market:
                # Default adjustment for unlisted markets
                market_factor = 0.95  # Slightly lower for rural markets
                market_info = "Rural market adjustment"
            
            # Calculate adjusted base price
            adjusted_base_price = crop_data['current'] * market_factor
            
            # Generate price prediction for specified days
            predictions = []
            trend = crop_data['trend']
            
            for day in range(1, days + 1):
                if trend == 'up':
                    price = adjusted_base_price + (day * 0.5)
                elif trend == 'down':
                    price = adjusted_base_price - (day * 0.3)
                else:
                    price = adjusted_base_price + ((-1) ** day * 0.2)
                
                predictions.append({
                    'day': day,
                    'date': (datetime.now() + timedelta(days=day)).strftime('%Y-%m-%d'),
                    'predicted_price': round(price, 2)
                })
            
            # Calculate min, max, and modal price from predictions
            price_values = [p['predicted_price'] for p in predictions]
            min_price = min(price_values)
            max_price = max(price_values)
            
            # Calculate modal price (most frequent, rounded to nearest rupee)
            from collections import Counter
            rounded_prices = [round(p) for p in price_values]
            price_counter = Counter(rounded_prices)
            modal_price = price_counter.most_common(1)[0][0] if price_counter else round(adjusted_base_price)
            
            # Calculate average predicted price
            avg_predicted_price = round(sum(price_values) / len(price_values), 2)
            
            return {
                'success': True,
                'crop': crop_name,
                'state': state,
                'market': market,
                'current_price': round(adjusted_base_price, 2),
                'base_price': crop_data['current'],
                'market_factor': round(market_factor, 2),
                'market_info': market_info,
                'trend': crop_data['trend'],
                'predictions': predictions,
                'average_predicted_price': avg_predicted_price,
                'min_price': min_price,
                'max_price': max_price,
                'modal_price': modal_price
            }
        else:
            return {
                'success': False,
                'error': 'Crop not found in database'
            }
    
    def get_market_prices(self, state=None, market=None):
        """
        Get current market prices for various crops with location-specific adjustments
        """
        data = self.fetch_kaggle_data()
        
        # Determine market factor
        market_factor = 1.0
        market_info = "National average"
        if market and market in MARKET_PRICE_VARIATIONS:
            market_factor = MARKET_PRICE_VARIATIONS[market]['factor']
            market_info = MARKET_PRICE_VARIATIONS[market]['reason']
        elif state and market:
            market_factor = 0.95  # Default rural market adjustment
            market_info = "Rural market prices"
        
        market_prices = []
        for crop, info in data.items():
            # Format crop name properly
            crop_display = crop.replace('_', ' ').title()
            adjusted_price = round(info['current'] * market_factor, 2)
            
            market_prices.append({
                'crop': crop_display,
                'base_price': info['current'],
                'market_price': adjusted_price,
                'price': adjusted_price,  # For backward compatibility
                'unit': 'per kg',
                'trend': info['trend'],
                'market_factor': round(market_factor, 2),
                'last_updated': datetime.now().strftime('%Y-%m-%d')
            })
        
        # Sort by crop name
        market_prices.sort(key=lambda x: x['crop'])
        
        return {
            'success': True,
            'state': state,
            'market': market,
            'market_info': market_info,
            'market_factor': round(market_factor, 2),
            'prices': market_prices
        }

# Initialize predictor
predictor = PricePredictor()

@price_bp.route('/predict', methods=['POST'])
def predict_price():
    """
    Predict future price for a crop with state and market consideration
    """
    data = request.get_json()
    
    if not data or 'crop' not in data:
        return jsonify({'success': False, 'error': 'Crop name is required'}), 400
    
    crop_name = data['crop']
    days = data.get('days', 30)
    state = data.get('state')
    market = data.get('market')
    
    result = predictor.predict_price(crop_name, days, state, market)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 404

@price_bp.route('/market-prices', methods=['GET'])
def get_market_prices():
    """
    Get current market prices with state and market filtering
    """
    state = request.args.get('state')
    market = request.args.get('market')
    
    result = predictor.get_market_prices(state, market)
    return jsonify(result), 200

@price_bp.route('/states', methods=['GET'])
def get_states():
    """
    Get list of all Indian states
    """
    states = list(INDIAN_STATES_MARKETS.keys())
    return jsonify({
        'success': True,
        'states': sorted(states)
    }), 200

@price_bp.route('/markets/<state>', methods=['GET'])
def get_markets_by_state(state):
    """
    Get list of markets for a specific state
    """
    if state in INDIAN_STATES_MARKETS:
        markets = INDIAN_STATES_MARKETS[state]
        return jsonify({
            'success': True,
            'state': state,
            'markets': sorted(markets)
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': f'State "{state}" not found'
        }), 404

@price_bp.route('/crops', methods=['GET'])
def get_available_crops():
    """
    Get list of all crops available for price prediction
    """
    crops = list(SAMPLE_PRICE_DATA.keys())
    return jsonify({
        'success': True,
        'crops': [crop.capitalize() for crop in crops]
    }), 200

@price_bp.route('/compare', methods=['POST'])
def compare_prices():
    """
    Compare prices across multiple crops
    """
    data = request.get_json()
    
    if not data or 'crops' not in data:
        return jsonify({'success': False, 'error': 'Crops list is required'}), 400
    
    crops = data['crops']
    comparison = []
    
    for crop in crops:
        result = predictor.predict_price(crop, 30)
        if result['success']:
            comparison.append({
                'crop': crop,
                'current_price': result['current_price'],
                'predicted_price': result['average_predicted_price'],
                'trend': result['trend']
            })
    
    return jsonify({
        'success': True,
        'comparison': comparison
    }), 200
