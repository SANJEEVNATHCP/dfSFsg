from flask import Blueprint, request, jsonify, render_template
from models import db, User, FarmerProfile, Product, DiseaseDetection
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import func

profile_bp = Blueprint('profile', __name__)

SECRET_KEY = 'your-secret-key-change-in-production'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'success': False, 'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except:
            return jsonify({'success': False, 'error': 'Token is invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@profile_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    """
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        phone=data.get('phone', ''),
        language_preference=data.get('language', 'en')
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Create farmer profile
    profile = FarmerProfile(user_id=user.id)
    db.session.add(profile)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201

@profile_bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT token
    """
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, SECRET_KEY, algorithm='HS256')
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }), 200

@profile_bp.route('/me', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    Get current user profile
    """
    profile = FarmerProfile.query.filter_by(user_id=current_user.id).first()
    
    return jsonify({
        'success': True,
        'user': current_user.to_dict(),
        'profile': profile.to_dict() if profile else None
    }), 200

@profile_bp.route('/update', methods=['PUT'])
@token_required
def update_profile(current_user):
    """
    Update user profile
    """
    data = request.get_json()
    
    # Update user data
    if 'phone' in data:
        current_user.phone = data['phone']
    if 'language_preference' in data:
        current_user.language_preference = data['language_preference']
    
    # Update or create farmer profile
    profile = FarmerProfile.query.filter_by(user_id=current_user.id).first()
    
    if not profile:
        profile = FarmerProfile(user_id=current_user.id)
        db.session.add(profile)
    
    if 'full_name' in data:
        profile.full_name = data['full_name']
    if 'farm_location' in data:
        profile.farm_location = data['farm_location']
    if 'farm_size' in data:
        profile.farm_size = data['farm_size']
    if 'crops_grown' in data:
        profile.crops_grown = data['crops_grown']
    if 'state' in data:
        profile.state = data['state']
    if 'district' in data:
        profile.district = data['district']
    if 'pin_code' in data:
        profile.pin_code = data['pin_code']
    if 'aadhar_number' in data:
        profile.aadhar_number = data['aadhar_number']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully',
        'user': current_user.to_dict(),
        'profile': profile.to_dict()
    }), 200

@profile_bp.route('/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """
    Change user password
    """
    data = request.get_json()
    
    if not data or not data.get('old_password') or not data.get('new_password'):
        return jsonify({'success': False, 'error': 'Old and new passwords required'}), 400
    
    if not check_password_hash(current_user.password_hash, data['old_password']):
        return jsonify({'success': False, 'error': 'Incorrect old password'}), 401
    
    current_user.password_hash = generate_password_hash(data['new_password'])
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Password changed successfully'
    }), 200

@profile_bp.route('/delete', methods=['DELETE'])
@token_required
def delete_account(current_user):
    """
    Delete user account
    """
    # Delete profile
    profile = FarmerProfile.query.filter_by(user_id=current_user.id).first()
    if profile:
        db.session.delete(profile)
    
    # Delete user
    db.session.delete(current_user)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Account deleted successfully'
    }), 200

@profile_bp.route('/page')
@profile_bp.route('/page/<username>')
def profile_page(username=None):
    """
    Render the GitHub-style profile page
    """
    # For demo purposes, use a default user or create sample data
    if username:
        user = User.query.filter_by(username=username).first()
        if not user:
            return "Profile not found", 404
    else:
        # Get first user or create a demo user
        user = User.query.first()
        if not user:
            # Create a demo user for the profile page
            user = User(
                username="farmer_demo",
                email="demo@agromitra.com",
                password_hash=generate_password_hash("demo123"),
                phone="9876543210",
                language_preference="en"
            )
            db.session.add(user)
            db.session.commit()
    
    # Get or create farmer profile
    profile = FarmerProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        profile = FarmerProfile(
            user_id=user.id,
            full_name="Demo Farmer",
            farm_location="Punjab, India",
            farm_size=25.5,
            crops_grown="Wheat, Rice, Vegetables",
            state="Punjab",
            district="Amritsar",
            pin_code="143001"
        )
        db.session.add(profile)
        db.session.commit()
    
    # Calculate statistics
    products_count = Product.query.filter_by(seller_id=user.id).count()
    detections_count = DiseaseDetection.query.filter_by(user_id=user.id).count()
    total_revenue = db.session.query(func.sum(Product.price_per_unit * Product.quantity)).filter_by(seller_id=user.id).scalar() or 0
    
    stats = {
        'products_count': products_count,
        'detections_count': detections_count,
        'total_revenue': int(total_revenue),
        'success_rate': 95,  # Demo value
        'crops_variety': len(profile.crops_grown.split(',')) if profile.crops_grown else 0,
        'avg_yield': 85,  # Demo value
        'sustainability_score': 92  # Demo value
    }
    
    # Generate recent activities based on user data
    activities = []
    
    # Add marketplace activities if user has products
    if products_count > 0:
        activities.append({
            'icon': '🛒',
            'title': f'Listed {products_count} products in marketplace',
            'time': '2 hours ago'
        })
        activities.append({
            'icon': '💰',
            'title': 'Received payment for crop sale',
            'time': '1 day ago'
        })
    
    # Add detection activities if user has detections
    if detections_count > 0:
        activities.append({
            'icon': '🔍',
            'title': 'Performed disease detection scan',
            'time': '5 hours ago'
        })
    
    # Always show these general activities
    activities.extend([
        {
            'icon': '🌱',
            'title': 'Updated crop planting schedule',
            'time': '2 days ago'
        },
        {
            'icon': '📋',
            'title': 'Profile information updated',
            'time': '3 days ago'
        },
        {
            'icon': '🌾',
            'title': 'Added new crops to farm profile',
            'time': '1 week ago'
        }
    ])
    
    # If no activities at all, add welcome message
    if not activities:
        activities.append({
            'icon': '📝',
            'title': 'Welcome! Start using the app to see your activity here',
            'time': 'Get started today'
        })
    
    return render_template('profile_agricultural.html', user=user, profile=profile, stats=stats, activities=activities)

@profile_bp.route('/update-info', methods=['POST'])
def update_profile_info():
    """
    Update user profile information
    """
    try:
        data = request.get_json()
        
        # For demo, use first user or create if none exists
        user = User.query.first()
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Update user information
        if data.get('email'):
            user.email = data['email']
        if data.get('phone'):
            user.phone = data['phone']
        if data.get('language'):
            user.language_preference = data['language']
        
        # Get or create farmer profile
        profile = FarmerProfile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = FarmerProfile(user_id=user.id)
            db.session.add(profile)
        
        # Update profile information
        if data.get('fullName'):
            profile.full_name = data['fullName']
        if data.get('farmSize'):
            try:
                profile.farm_size = float(data['farmSize'])
            except (ValueError, TypeError):
                pass
        if data.get('farmLocation'):
            profile.farm_location = data['farmLocation']
        if data.get('state'):
            profile.state = data['state']
        if data.get('district'):
            profile.district = data['district']
        if data.get('pinCode'):
            profile.pin_code = data['pinCode']
        if data.get('cropsGrown'):
            profile.crops_grown = data['cropsGrown']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
