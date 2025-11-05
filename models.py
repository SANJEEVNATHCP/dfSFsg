from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15))
    language_preference = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    profile = db.relationship('FarmerProfile', backref='user', uselist=False)
    products = db.relationship('Product', backref='seller', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'language_preference': self.language_preference,
            'created_at': self.created_at.isoformat()
        }

class FarmerProfile(db.Model):
    __tablename__ = 'farmer_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(100))
    farm_location = db.Column(db.String(200))
    farm_size = db.Column(db.Float)  # in acres
    crops_grown = db.Column(db.Text)  # JSON string
    state = db.Column(db.String(50))
    district = db.Column(db.String(50))
    pin_code = db.Column(db.String(10))
    aadhar_number = db.Column(db.String(12))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'farm_location': self.farm_location,
            'farm_size': self.farm_size,
            'crops_grown': self.crops_grown,
            'state': self.state,
            'district': self.district,
            'pin_code': self.pin_code
        }

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    quantity = db.Column(db.Float)
    unit = db.Column(db.String(20))
    price_per_unit = db.Column(db.Float)
    image_url = db.Column(db.String(200))
    location = db.Column(db.String(100))
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'quantity': self.quantity,
            'unit': self.unit,
            'price_per_unit': self.price_per_unit,
            'image_url': self.image_url,
            'location': self.location,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat()
        }

class DiseaseDetection(db.Model):
    __tablename__ = 'disease_detections'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_path = db.Column(db.String(200))
    disease_name = db.Column(db.String(100))
    confidence = db.Column(db.Float)
    recommendations = db.Column(db.Text)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'disease_name': self.disease_name,
            'confidence': self.confidence,
            'recommendations': self.recommendations,
            'detected_at': self.detected_at.isoformat()
        }

class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    message = db.Column(db.Text)
    response = db.Column(db.Text)
    language = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'response': self.response,
            'language': self.language,
            'created_at': self.created_at.isoformat()
        }
