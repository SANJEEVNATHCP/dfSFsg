#!/usr/bin/env python3
"""
Working Flask app for AgroMitra with state/market price prediction
Production-ready configuration with environment variables
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Set template and static folders to frontend directory
template_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'templates')
static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend', 'static')

app = Flask(__name__, 
            template_folder=template_folder,
            static_folder=static_folder)

# Production-safe configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Database configuration - store in database directory
db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'agromitra.db')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{db_path}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS configuration for production
allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
CORS(app, origins=allowed_origins)

# Initialize database
from backend.models import db
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    # Create database directory if it doesn't exist
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    db.create_all()
    print("✅ Database initialized successfully")

# Import blueprints from backend.routes
from backend.routes.price_prediction import price_bp

# Register the working blueprint
app.register_blueprint(price_bp, url_prefix='/api/price')

# Try to import profile routes
try:
    from backend.routes.profile import profile_bp
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    print("✅ Profile routes loaded successfully")
except Exception as e:
    print(f"⚠️ Profile routes not available: {e}")
    
# Try to import other routes
try:
    from backend.routes.chatbot import chatbot_bp
    app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')
    print("✅ Chatbot routes loaded successfully")
except Exception as e:
    print(f"⚠️ Chatbot routes not available: {e}")

try:
    from backend.routes.schemes import schemes_bp
    app.register_blueprint(schemes_bp, url_prefix='/api/schemes')
    print("✅ Schemes routes loaded successfully")
except Exception as e:
    print(f"⚠️ Schemes routes not available: {e}")

try:
    from backend.routes.farmstories import farmstories_bp
    app.register_blueprint(farmstories_bp, url_prefix='/api/farmstories')
    print("✅ FarmStories routes loaded successfully")
except Exception as e:
    print(f"⚠️ FarmStories routes not available: {e}")

# Add placeholder for disease detection if it's not available
try:
    from backend.routes.disease_detection import disease_bp
    app.register_blueprint(disease_bp, url_prefix='/api/disease')
    print("✅ Disease detection routes loaded successfully")
except Exception as e:
    print(f"⚠️ Disease detection not available (requires PyTorch): {e}")
    # Create simple placeholder endpoint
    from flask import Blueprint
    disease_placeholder = Blueprint('disease_placeholder', __name__)
    
    @disease_placeholder.route('/detect', methods=['POST'])
    def detect_placeholder():
        return jsonify({
            'success': False,
            'error': 'Disease detection is temporarily unavailable. Please ensure PyTorch and model dependencies are installed.'
        }), 503
    
    @disease_placeholder.route('/diseases', methods=['GET'])
    def diseases_placeholder():
        return jsonify({
            'success': True,
            'diseases': ['Feature temporarily unavailable']
        }), 200
    
    app.register_blueprint(disease_placeholder, url_prefix='/api/disease')

@app.route('/')
def index():
    """Serve the main AgroMitra interface"""
    return render_template('index.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'message': 'AgroMitra API is running',
        'features': ['price_prediction', 'state_market_selection']
    }), 200

# Add a simple test endpoint
@app.route('/test')
def test():
    """Simple test page"""
    return """
    <h1>🌾 AgroMitra - Price Prediction Test</h1>
    <p>Server is running! Available endpoints:</p>
    <ul>
        <li><a href="/api/health">Health Check</a></li>
        <li><a href="/api/price/states">Get States</a></li>
        <li><a href="/api/price/markets/Maharashtra">Get Markets for Maharashtra</a></li>
    </ul>
    <p><a href="/">Go to Main App</a></p>
    """

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("🌾 AgroMitra Flask Server Starting...")
    print(f"📍 Server URL: http://{host}:{port}")
    print(f"🔗 Health Check: http://{host}:{port}/api/health")
    print(f"📊 States API: http://{host}:{port}/api/price/states")
    print(f"🧪 Test Page: http://{host}:{port}/test")
    print(f"🔧 Debug Mode: {debug}")
    print("Press Ctrl+C to stop")
    
    app.run(debug=debug, host=host, port=port)