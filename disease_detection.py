from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import torch
import torchvision.transforms as transforms
from PIL import Image
import os
import json

# Import AI integration module
try:
    from ai_integration import enhance_disease_detection_with_ai
    AI_AVAILABLE = True
    print("✅ AI integration module loaded successfully!")
except ImportError as e:
    AI_AVAILABLE = False
    print(f"AI integration module not available - using basic recommendations. Error: {e}")

disease_bp = Blueprint('disease', __name__)

# Disease information and recommendations - Comprehensive database covering 14 crops
DISEASE_INFO = {
    # ========== APPLE DISEASES ==========
    'Apple___Apple_scab': {
        'disease': 'Apple Scab',
        'severity': 'Moderate',
        'recommendations': [
            'Remove and destroy infected leaves and fruit',
            'Apply fungicides like Captan or Myclobutanil',
            'Ensure good air circulation by pruning',
            'Use resistant apple varieties',
            'Apply preventive sprays in early spring'
        ],
        'prevention': 'Keep the orchard clean, prune regularly, and use disease-resistant varieties'
    },
    'Apple___Black_rot': {
        'disease': 'Black Rot',
        'severity': 'High',
        'recommendations': [
            'Remove infected fruit and mummified apples',
            'Prune out dead wood and cankers',
            'Apply fungicides during pink and petal fall stages',
            'Maintain good sanitation practices',
            'Remove leaf litter in fall'
        ],
        'prevention': 'Regular pruning and sanitation are crucial'
    },
    'Apple___Cedar_apple_rust': {
        'disease': 'Cedar Apple Rust',
        'severity': 'Moderate',
        'recommendations': [
            'Remove nearby cedar trees if possible',
            'Apply fungicides from pink bud through to early summer',
            'Use resistant apple varieties',
            'Monitor for orange spots on leaves'
        ],
        'prevention': 'Plant resistant varieties and manage nearby cedar trees'
    },
    'Apple___healthy': {
        'disease': 'Healthy',
        'severity': 'None',
        'recommendations': [
            'Continue regular monitoring',
            'Maintain proper irrigation and fertilization',
            'Practice preventive disease management',
            'Ensure proper pruning and sanitation'
        ],
        'prevention': 'Keep following good agricultural practices'
    },
    
    # ========== BLUEBERRY DISEASES ==========
    'Blueberry___healthy': {
        'disease': 'Healthy',
        'severity': 'None',
        'recommendations': [
            'Continue regular monitoring',
            'Maintain acidic soil (pH 4.5-5.5)',
            'Ensure proper drainage',
            'Practice preventive pruning for air circulation'
        ],
        'prevention': 'Maintain proper soil conditions and good drainage'
    },
    'Blueberry___Mummy_berry': {
        'disease': 'Mummy Berry',
        'severity': 'High',
        'recommendations': [
            'Remove and destroy mummified berries',
            'Apply fungicides during bloom period',
            'Mulch to prevent spore release from soil',
            'Practice good sanitation',
            'Prune to improve air circulation'
        ],
        'prevention': 'Remove infected berries and apply preventive fungicides'
    },
    
    # ========== CHERRY DISEASES ==========
    'Cherry___Powdery_mildew': {
        'disease': 'Powdery Mildew',
        'severity': 'Moderate',
        'recommendations': [
            'Apply sulfur or potassium bicarbonate fungicides',
            'Prune to improve air circulation',
            'Remove infected shoots and leaves',
            'Avoid overhead watering',
            'Use resistant varieties'
        ],
        'prevention': 'Ensure good air circulation and apply preventive treatments'
    },
    'Cherry___healthy': {
        'disease': 'Healthy',
        'severity': 'None',
        'recommendations': [
            'Continue regular monitoring',
            'Maintain proper pruning schedule',
            'Ensure adequate nutrition',
            'Practice preventive pest management'
        ],
        'prevention': 'Keep following good orchard practices'
    },
    
    # ========== CORN (MAIZE) DISEASES ==========
    'Corn___Cercospora_leaf_spot': {
        'disease': 'Cercospora Leaf Spot (Gray Leaf Spot)',
        'severity': 'Moderate to High',
        'recommendations': [
            'Use resistant hybrid varieties',
            'Practice crop rotation (2-3 years)',
            'Apply fungicides if disease is severe',
            'Reduce plant density for better air flow',
            'Bury crop residue by deep plowing'
        ],
        'prevention': 'Plant resistant varieties and rotate crops regularly'
    },
    'Corn___Common_rust': {
        'disease': 'Common Rust',
        'severity': 'Moderate',
        'recommendations': [
            'Plant resistant hybrids',
            'Apply fungicides when pustules appear',
            'Monitor fields regularly during humid weather',
            'Ensure adequate plant spacing',
            'Remove volunteer corn plants'
        ],
        'prevention': 'Use resistant varieties and monitor during wet conditions'
    },
    'Corn___Northern_Leaf_Blight': {
        'disease': 'Northern Leaf Blight',
        'severity': 'High',
        'recommendations': [
            'Use resistant corn hybrids',
            'Practice minimum 2-year crop rotation',
            'Apply foliar fungicides preventively',
            'Till under crop debris after harvest',
            'Avoid excessive nitrogen fertilization'
        ],
        'prevention': 'Plant resistant varieties and manage crop residues'
    },
    'Corn___healthy': {
        'disease': 'Healthy',
        'severity': 'None',
        'recommendations': [
            'Continue regular field monitoring',
            'Maintain balanced fertilization',
            'Ensure proper irrigation',
            'Practice preventive pest management'
        ],
        'prevention': 'Keep following good agricultural practices'
    },
    
    # ========== GRAPE DISEASES ==========
    'Grape___Black_rot': {
        'disease': 'Black Rot',
        'severity': 'High',
        'recommendations': [
            'Remove and destroy mummified fruit',
            'Apply fungicides from bloom through harvest',
            'Prune for good air circulation',
            'Remove infected leaves and shoots',
            'Practice good vineyard sanitation'
        ],
        'prevention': 'Sanitation and preventive fungicide applications are critical'
    },
    'Grape___Esca_Black_Measles': {
        'disease': 'Esca (Black Measles)',
        'severity': 'High',
        'recommendations': [
            'Remove and burn infected wood',
            'Avoid pruning wounds during wet weather',
            'Apply wound protectants after pruning',
            'Remove dead or dying vines',
            'Improve soil drainage'
        ],
        'prevention': 'Protect pruning wounds and remove infected plants promptly'
    },
    'Grape___Leaf_blight_Isariopsis_Leaf_Spot': {
        'disease': 'Leaf Blight (Isariopsis Leaf Spot)',
        'severity': 'Moderate',
        'recommendations': [
            'Apply copper-based fungicides',
            'Remove infected leaves',
            'Ensure proper canopy management',
            'Avoid overhead irrigation',
            'Improve air circulation through pruning'
        ],
        'prevention': 'Maintain good canopy management and apply preventive sprays'
    },
    'Grape___healthy': {
        'disease': 'Healthy',
        'severity': 'None',
        'recommendations': [
            'Continue regular vineyard monitoring',
            'Maintain proper pruning and training',
            'Ensure balanced nutrition',
            'Practice preventive disease management'
        ],
        'prevention': 'Keep following good viticulture practices'
    },
    
    # ========== ORANGE (CITRUS) DISEASES ==========
    'Orange___Haunglongbing_Citrus_greening': {
        'disease': 'Huanglongbing (Citrus Greening)',
        'severity': 'Very High',
        'recommendations': [
            'Remove and destroy infected trees immediately',
            'Control psyllid vectors with insecticides',
            'Use certified disease-free nursery stock',
            'Monitor trees regularly for symptoms',
            'Report suspected cases to authorities'
        ],
        'prevention': 'This is a devastating disease - early detection and removal are critical'
    },
    'Orange___healthy': {
        'disease': 'Healthy',
        'severity': 'None',
        'recommendations': [
            'Continue regular monitoring for pests and diseases',
            'Maintain proper nutrition and irrigation',
            'Practice preventive pest management',
            'Ensure proper pruning and sanitation'
        ],
        'prevention': 'Keep following good citrus management practices'
    },
    
    # ========== PEACH DISEASES ==========
    'Peach___Bacterial_spot': {
        'disease': 'Bacterial Spot',
        'severity': 'High',
        'recommendations': [
            'Apply copper-based bactericides',
            'Use resistant varieties',
            'Avoid overhead irrigation',
            'Remove infected fruit and leaves',
            'Apply preventive sprays before symptoms appear'
        ],
        'prevention': 'Use resistant varieties and apply preventive copper sprays'
    },
    'Peach___healthy': {
        'disease': 'Healthy',
        'severity': 'None',
        'recommendations': [
            'Continue regular orchard monitoring',
            'Maintain proper pruning schedule',
            'Ensure adequate nutrition',
            'Practice preventive pest and disease management'
        ],
        'prevention': 'Keep following good orchard practices'
    },
    
    # ========== PEPPER (BELL PEPPER) DISEASES ===========
    'Pepper,_bell___Bacterial_spot': {
        'disease': 'Bacterial Spot',
        'severity': 'High',
        'recommendations': [
            'Use copper-based bactericides and mancozeb',
            'Plant disease-free seeds and transplants',
            'Remove and destroy infected plants',
            'Avoid overhead irrigation',
            'Practice 2-3 year crop rotation'
        ],
        'prevention': 'Use certified seeds and practice proper sanitation'
    },
    'Pepper,_bell___healthy': {
        'disease': 'Healthy',
        'severity': 'None',
        'recommendations': [
            'Continue regular monitoring',
            'Maintain proper watering and fertilization',
            'Practice good garden hygiene',
            'Monitor for early signs of pests or diseases'
        ],
        'prevention': 'Keep following good agricultural practices'
    },
    'Pepper,_bell___Powdery_mildew': {
        'disease': 'Powdery Mildew',
        'severity': 'Moderate',
        'recommendations': [
            'Apply sulfur or potassium bicarbonate fungicides',
            'Improve air circulation',
            'Remove infected leaves',
            'Avoid excessive nitrogen fertilization',
            'Water at the base of plants'
        ],
        'prevention': 'Ensure good air circulation and apply preventive treatments'
    },
    
    # ========== POTATO DISEASES ==========
    'Potato___Early_blight': {
        'disease': 'Early Blight',
        'severity': 'Moderate',
        'recommendations': [
            'Apply fungicides containing chlorothalonil or mancozeb',
            'Hill up soil around plants',
            'Remove infected lower leaves',
            'Practice 3-4 year crop rotation',
            'Use certified disease-free seed potatoes'
        ],
        'prevention': 'Use certified seeds and practice crop rotation'
    },
    'Potato___Late_blight': {
        'disease': 'Late Blight',
        'severity': 'Very High',
        'recommendations': [
            'Apply fungicides immediately (chlorothalonil or copper-based)',
            'Destroy infected plants completely',
            'Avoid irrigation during cool, humid weather',
            'Harvest tubers before blight affects them',
            'Use resistant varieties'
        ],
        'prevention': 'Monitor closely during cool, wet weather and act quickly'
    },
    'Potato___Potato_Virus_Y': {
        'disease': 'Potato Virus Y (PVY)',
        'severity': 'High',
        'recommendations': [
            'Use certified virus-free seed potatoes',
            'Control aphid vectors with insecticides',
            'Remove infected plants immediately',
            'Practice strict roguing in seed production',
            'Avoid planting near tobacco or tomato fields'
        ],
        'prevention': 'Use certified seed and control aphid populations'
    },
    'Potato___healthy': {
        'disease': 'Healthy',
        'severity': 'None',
        'recommendations': [
            'Continue monitoring regularly',
            'Maintain proper fertilization',
            'Ensure adequate hilling',
            'Practice preventive measures'
        ],
        'prevention': 'Keep following good agricultural practices'
    },
    
    # ========== RASPBERRY DISEASES ==========
    'Raspberry___healthy': {
        'disease': 'Healthy',
        'severity': 'None',
        'recommendations': [
            'Continue regular monitoring',
            'Maintain proper pruning and thinning',
            'Ensure good air circulation',
            'Practice preventive pest and disease management'
        ],
        'prevention': 'Keep following good raspberry management practices'
    },
    'Raspberry___Anthracnose': {
        'disease': 'Anthracnose',
        'severity': 'Moderate to High',
        'recommendations': [
            'Remove and destroy infected canes',
            'Apply lime sulfur or copper fungicides',
            'Prune for good air circulation',
            'Avoid overhead irrigation',
            'Use resistant varieties'
        ],
        'prevention': 'Prune out infected canes and apply preventive fungicides'
    },
    
    # ========== SOYBEAN DISEASES ==========
    'Soybean___healthy': {
        'disease': 'Healthy',
        'severity': 'None',
        'recommendations': [
            'Continue regular field monitoring',
            'Maintain balanced fertilization',
            'Ensure proper drainage',
            'Practice preventive pest management'
        ],
        'prevention': 'Keep following good agricultural practices'
    },
    'Soybean___Frogeye_Leaf_Spot': {
        'disease': 'Frogeye Leaf Spot',
        'severity': 'Moderate to High',
        'recommendations': [
            'Plant resistant varieties',
            'Practice 2-3 year crop rotation',
            'Apply foliar fungicides if severe',
            'Use disease-free certified seed',
            'Bury crop residue by tillage'
        ],
        'prevention': 'Use resistant varieties and practice crop rotation'
    },
    
    # ========== SQUASH DISEASES ==========
    'Squash___Powdery_mildew': {
        'disease': 'Powdery Mildew',
        'severity': 'Moderate',
        'recommendations': [
            'Apply sulfur or potassium bicarbonate fungicides',
            'Plant resistant varieties',
            'Ensure adequate plant spacing',
            'Remove infected leaves',
            'Avoid overhead watering late in the day'
        ],
        'prevention': 'Use resistant varieties and maintain good air circulation'
    },
    'Squash___Downy_mildew': {
        'disease': 'Downy Mildew',
        'severity': 'High',
        'recommendations': [
            'Apply copper-based or systemic fungicides',
            'Improve air circulation and drainage',
            'Remove infected plants',
            'Water in the morning to allow foliage to dry',
            'Practice crop rotation'
        ],
        'prevention': 'Apply preventive fungicides and ensure good drainage'
    },
    'Squash___healthy': {
        'disease': 'Healthy',
        'severity': 'None',
        'recommendations': [
            'Continue regular monitoring',
            'Maintain proper watering and fertilization',
            'Ensure good pollination',
            'Practice preventive pest management'
        ],
        'prevention': 'Keep following good agricultural practices'
    },
    
    # ========== STRAWBERRY DISEASES ==========
    'Strawberry___Leaf_scorch': {
        'disease': 'Leaf Scorch',
        'severity': 'Moderate',
        'recommendations': [
            'Remove and destroy infected leaves',
            'Apply fungicides during renovation',
            'Use disease-free planting stock',
            'Avoid overhead irrigation',
            'Maintain proper plant spacing'
        ],
        'prevention': 'Use certified plants and maintain good air circulation'
    },
    'Strawberry___Powdery_mildew': {
        'disease': 'Powdery Mildew',
        'severity': 'Moderate',
        'recommendations': [
            'Apply sulfur-based fungicides',
            'Plant resistant varieties',
            'Improve air circulation',
            'Remove infected leaves',
            'Avoid excessive nitrogen fertilization'
        ],
        'prevention': 'Use resistant varieties and ensure good air flow'
    },
    'Strawberry___healthy': {
        'disease': 'Healthy',
        'severity': 'None',
        'recommendations': [
            'Continue regular monitoring',
            'Maintain proper irrigation and fertilization',
            'Practice preventive disease management',
            'Ensure good plant spacing'
        ],
        'prevention': 'Keep following good strawberry management practices'
    },
    
    # ========== TOMATO DISEASES ==========
    'Tomato___Bacterial_spot': {
        'disease': 'Bacterial Spot',
        'severity': 'High',
        'recommendations': [
            'Use copper-based bactericides',
            'Remove and destroy infected plants',
            'Avoid overhead irrigation',
            'Use disease-free seeds and transplants',
            'Rotate crops with non-host plants'
        ],
        'prevention': 'Use certified disease-free seeds and practice crop rotation'
    },
    'Tomato___Early_blight': {
        'disease': 'Early Blight',
        'severity': 'Moderate',
        'recommendations': [
            'Apply fungicides containing chlorothalonil or mancozeb',
            'Remove lower leaves that touch the soil',
            'Mulch around plants to prevent soil splash',
            'Practice crop rotation',
            'Ensure proper spacing for air circulation'
        ],
        'prevention': 'Mulch plants and remove infected lower leaves promptly'
    },
    'Tomato___Late_blight': {
        'disease': 'Late Blight',
        'severity': 'Very High',
        'recommendations': [
            'Apply fungicides immediately (copper-based or chlorothalonil)',
            'Remove and destroy infected plants completely',
            'Avoid overhead watering',
            'Improve air circulation',
            'Monitor weather for favorable disease conditions'
        ],
        'prevention': 'This is a serious disease - act quickly and use resistant varieties'
    },
    'Tomato___Leaf_Mold': {
        'disease': 'Leaf Mold',
        'severity': 'Moderate',
        'recommendations': [
            'Improve air circulation and reduce humidity',
            'Apply fungicides containing chlorothalonil',
            'Remove infected leaves',
            'Avoid overhead watering',
            'Use resistant varieties'
        ],
        'prevention': 'Maintain low humidity and good air circulation in greenhouses'
    },
    'Tomato___Septoria_leaf_spot': {
        'disease': 'Septoria Leaf Spot',
        'severity': 'Moderate',
        'recommendations': [
            'Apply fungicides containing chlorothalonil or mancozeb',
            'Remove and destroy infected leaves',
            'Mulch to prevent soil splash',
            'Practice crop rotation',
            'Avoid overhead irrigation'
        ],
        'prevention': 'Mulch plants and apply preventive fungicides'
    },
    'Tomato___Spider_mites': {
        'disease': 'Spider Mites (Two-spotted)',
        'severity': 'Moderate',
        'recommendations': [
            'Apply miticides or insecticidal soap',
            'Increase humidity around plants',
            'Remove heavily infested leaves',
            'Use predatory mites for biological control',
            'Avoid excessive nitrogen fertilization'
        ],
        'prevention': 'Monitor regularly and maintain adequate moisture'
    },
    'Tomato___Target_Spot': {
        'disease': 'Target Spot',
        'severity': 'Moderate to High',
        'recommendations': [
            'Apply fungicides containing chlorothalonil or azoxystrobin',
            'Remove infected leaves',
            'Improve air circulation',
            'Avoid overhead irrigation',
            'Practice crop rotation'
        ],
        'prevention': 'Apply preventive fungicides and maintain good sanitation'
    },
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': {
        'disease': 'Tomato Yellow Leaf Curl Virus (TYLCV)',
        'severity': 'Very High',
        'recommendations': [
            'Remove and destroy infected plants immediately',
            'Control whitefly vectors with insecticides',
            'Use virus-resistant varieties',
            'Use reflective mulches to repel whiteflies',
            'Screen greenhouse vents'
        ],
        'prevention': 'Use resistant varieties and control whitefly populations aggressively'
    },
    'Tomato___Tomato_mosaic_virus': {
        'disease': 'Tomato Mosaic Virus',
        'severity': 'High',
        'recommendations': [
            'Remove and destroy infected plants',
            'Disinfect tools and hands between plants',
            'Use virus-resistant varieties',
            'Control aphid vectors',
            'Avoid tobacco products near plants'
        ],
        'prevention': 'Use certified disease-free seeds and practice strict sanitation'
    },
    'Tomato___healthy': {
        'disease': 'Healthy',
        'severity': 'None',
        'recommendations': [
            'Continue regular monitoring',
            'Maintain proper watering and fertilization',
            'Practice good garden hygiene',
            'Monitor for early signs of diseases'
        ],
        'prevention': 'Keep following good agricultural practices'
    }
}

class DiseaseDetector:
    def __init__(self, model_path='best_efficientnet_model.pth'):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        # Use the class list that matches your model's training order
        self.class_names = [
            'Apple___Apple_scab',
            'Apple___Black_rot',
            'Apple___Cedar_apple_rust',
            'Apple___healthy',
            'Blueberry___healthy',
            'Cherry_(including_sour)___Powdery_mildew',
            'Cherry_(including_sour)___healthy',
            'Corn_(maize)___Cercospora_leaf_spot__Gray_leaf_spot',
            'Corn_(maize)___Common_rust',
            'Corn_(maize)___Northern_Leaf_Blight',
            'Corn_(maize)___healthy',
            'Grape___Black_rot',
            'Grape___Esca_(Black_Measles)',
            'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
            'Grape___healthy',
            'Orange___Haunglongbing_(Citrus_greening)',
            'Peach___Bacterial_spot',
            'Peach___healthy',
            'Pepper,_bell___Bacterial_spot',
            'Pepper,_bell___healthy',
            'Potato___Early_blight',
            'Potato___Late_blight',
            'Potato___healthy',
            'Raspberry___healthy',
            'Soybean___healthy',
            'Squash___Powdery_mildew',
            'Strawberry___Leaf_scorch',
            'Strawberry___healthy',
            'Tomato___Bacterial_spot',
            'Tomato___Early_blight',
            'Tomato___healthy',
            'Tomato___Late_blight',
            'Tomato___Leaf_Mold',
            'Tomato___Septoria_leaf_spot',
            'Tomato___Spider_mites__Two-spotted_spider_mite',
            'Tomato___Target_Spot',
            'Tomato___Tomato_mosaic_virus',
            'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
        ]
        self.load_model(model_path)
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def load_model(self, model_path):
        try:
            import torchvision.models as models
            from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
            # Create EfficientNet architecture (no pretrained weights)
            self.model = efficientnet_b0(weights=None)
            num_classes = len(self.class_names)
            in_features = self.model.classifier[1].in_features
            self.model.classifier[1] = torch.nn.Linear(in_features, num_classes)
            # Load the state dictionary
            state_dict = torch.load(model_path, map_location=self.device)
            print("\n=== Loaded state_dict keys ===")
            print(list(state_dict.keys())[:20])
            print(f"Total keys: {len(state_dict.keys())}")
            print("\n=== Model state_dict keys ===")
            print(list(self.model.state_dict().keys())[:20])
            print(f"Total keys: {len(self.model.state_dict().keys())}")
            # If state_dict is wrapped, unwrap it
            if isinstance(state_dict, dict) and 'state_dict' in state_dict:
                state_dict = state_dict['state_dict']
            self.model.load_state_dict(state_dict, strict=False)
            self.model.to(self.device)
            self.model.eval()
            print(f"EfficientNet model loaded successfully from {model_path}")
        except Exception as e:
            print(f"Error loading EfficientNet model: {e}")
            # Create a dummy model for testing if actual model fails to load
            self.model = models.resnet18(weights=None)
            self.model.to(self.device)
            self.model.eval()
            print("Using dummy model for testing")
    
    def predict(self, image_path):
        try:
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
                
            predicted_class = self.class_names[predicted.item()] if predicted.item() < len(self.class_names) else 'Unknown'
            confidence_score = confidence.item()
            
            # Robust mapping: try direct, then fallback to best match
            disease_data = DISEASE_INFO.get(predicted_class)
            if not disease_data:
                # Try to find a close match by normalizing names
                norm_pred = predicted_class.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace('__', '_').lower()
                for k, v in DISEASE_INFO.items():
                    norm_key = k.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace('__', '_').lower()
                    if norm_pred == norm_key:
                        disease_data = v
                        break
            if not disease_data:
                # Fallback: create a placeholder
                disease_data = {
                    'disease': predicted_class.replace('_', ' '),
                    'severity': 'Unknown',
                    'recommendations': ['Consult with an agricultural expert'],
                    'prevention': 'Unable to determine'
                }
            
            return {
                'success': True,
                'predicted_class': predicted_class,
                'disease_name': disease_data['disease'],
                'confidence': round(confidence_score * 100, 2),
                'severity': disease_data['severity'],
                'recommendations': disease_data['recommendations'],
                'prevention': disease_data['prevention']
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Initialize detector
detector = DiseaseDetector()

@disease_bp.route('/detect', methods=['POST'])
def detect_disease():
    """
    Endpoint to detect plant disease from uploaded image
    Enhanced with AI-powered recommendations
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if file:
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join('uploads', filename)
            file.save(filepath)
            
            # Detect disease using ML model
            result = detector.predict(filepath)
            
            # Add image path to result
            result['image_path'] = filepath
            
            # Enhance with AI recommendations if available
            if AI_AVAILABLE and result.get('success', False):
                # Get farmer context from request (optional)
                farmer_context = {
                    'location': request.form.get('location', 'Unknown'),
                    'farm_size': request.form.get('farm_size', 'Unknown'),
                    'climate': request.form.get('climate', 'Unknown'),
                    'treatment_history': request.form.get('previous_treatments', 'None')
                }
                
                # Enhance with AI-powered recommendations
                try:
                    enhanced_result = enhance_disease_detection_with_ai(result, farmer_context)
                    enhanced_result['ai_enhanced'] = True
                    enhanced_result['ai_available'] = True
                    return jsonify(enhanced_result), 200
                except Exception as e:
                    print(f"AI enhancement failed: {e}")
                    result['ai_enhancement_error'] = str(e)
                    result['ai_enhanced'] = False
            
            # Return basic result if AI not available
            result['ai_enhanced'] = False
            result['ai_available'] = AI_AVAILABLE
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return jsonify({'success': False, 'error': 'Invalid file'}), 400

@disease_bp.route('/diseases', methods=['GET'])
def get_all_diseases():
    """
    Get information about all detectable diseases
    """
    return jsonify({
        'success': True,
        'diseases': DISEASE_INFO
    }), 200

@disease_bp.route('/disease/<disease_name>', methods=['GET'])
def get_disease_info(disease_name):
    """
    Get information about a specific disease
    """
    disease_data = DISEASE_INFO.get(disease_name)
    
    if disease_data:
        return jsonify({
            'success': True,
            'disease': disease_name,
            'data': disease_data
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': 'Disease not found'
        }), 404
