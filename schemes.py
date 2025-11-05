from flask import Blueprint, request, jsonify
from datetime import datetime

schemes_bp = Blueprint('schemes', __name__)

# Government schemes data
SCHEMES_DATA = [
    {
        'id': 1,
        'name': 'PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)',
        'description': 'Income support of ₹6000 per year to all farmer families in three equal installments',
        'benefits': '₹2000 per installment (3 installments per year)',
        'eligibility': [
            'All landholding farmer families',
            'Small and marginal farmers prioritized',
            'Aadhar card mandatory'
        ],
        'how_to_apply': 'Apply online at pmkisan.gov.in or through local agriculture office',
        'documents': ['Land records', 'Aadhar card', 'Bank account details'],
        'category': 'Income Support',
        'ministry': 'Ministry of Agriculture & Farmers Welfare'
    },
    {
        'id': 2,
        'name': 'Pradhan Mantri Fasal Bima Yojana (PMFBY)',
        'description': 'Crop insurance scheme providing financial support to farmers in case of crop loss',
        'benefits': 'Insurance coverage for crop loss due to natural calamities',
        'eligibility': [
            'All farmers growing notified crops',
            'Compulsory for loanee farmers',
            'Voluntary for non-loanee farmers'
        ],
        'how_to_apply': 'Apply through banks, CSCs, or online portal',
        'documents': ['Land records', 'Sowing certificate', 'Bank account'],
        'category': 'Insurance',
        'ministry': 'Ministry of Agriculture & Farmers Welfare'
    },
    {
        'id': 3,
        'name': 'Soil Health Card Scheme',
        'description': 'Provides farmers with soil health cards containing crop-wise recommendations',
        'benefits': 'Free soil testing and nutrient recommendations',
        'eligibility': ['All farmers'],
        'how_to_apply': 'Contact local agriculture department',
        'documents': ['Land records', 'Farmer ID'],
        'category': 'Advisory',
        'ministry': 'Ministry of Agriculture & Farmers Welfare'
    },
    {
        'id': 4,
        'name': 'Kisan Credit Card (KCC)',
        'description': 'Credit facility for farmers to meet agricultural expenses',
        'benefits': 'Short-term credit at subsidized interest rates',
        'eligibility': [
            'Farmers owning or cultivating land',
            'Share croppers and tenant farmers',
            'Good credit history'
        ],
        'how_to_apply': 'Apply through any bank',
        'documents': ['Land records', 'Aadhar card', 'Photo', 'Application form'],
        'category': 'Credit',
        'ministry': 'Ministry of Agriculture & Farmers Welfare'
    },
    {
        'id': 5,
        'name': 'National Mission for Sustainable Agriculture (NMSA)',
        'description': 'Promotes sustainable agriculture practices and soil health management',
        'benefits': 'Technical and financial support for sustainable farming',
        'eligibility': ['All farmers interested in sustainable agriculture'],
        'how_to_apply': 'Contact state agriculture department',
        'documents': ['Land records', 'Project proposal'],
        'category': 'Development',
        'ministry': 'Ministry of Agriculture & Farmers Welfare'
    },
    {
        'id': 6,
        'name': 'Paramparagat Krishi Vikas Yojana (PKVY)',
        'description': 'Supports organic farming through financial assistance',
        'benefits': '₹50,000 per hectare for 3 years',
        'eligibility': [
            'Farmers wanting to adopt organic farming',
            'Cluster approach (minimum 50 farmers)'
        ],
        'how_to_apply': 'Apply through district agriculture office',
        'documents': ['Land records', 'Group formation documents'],
        'category': 'Organic Farming',
        'ministry': 'Ministry of Agriculture & Farmers Welfare'
    },
    {
        'id': 7,
        'name': 'National Agriculture Market (e-NAM)',
        'description': 'Online trading platform for agricultural commodities',
        'benefits': 'Better price discovery and market access',
        'eligibility': ['All farmers'],
        'how_to_apply': 'Register on enam.gov.in',
        'documents': ['Aadhar card', 'Bank account', 'Mobile number'],
        'category': 'Marketing',
        'ministry': 'Ministry of Agriculture & Farmers Welfare'
    },
    {
        'id': 8,
        'name': 'Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)',
        'description': 'Irrigation scheme to expand cultivable area with assured irrigation',
        'benefits': 'Financial assistance for micro-irrigation and water conservation',
        'eligibility': ['All farmers'],
        'how_to_apply': 'Contact district agriculture office',
        'documents': ['Land records', 'Project details'],
        'category': 'Irrigation',
        'ministry': 'Ministry of Agriculture & Farmers Welfare'
    }
]

@schemes_bp.route('/all', methods=['GET'])
def get_all_schemes():
    """
    Get all government schemes
    """
    category = request.args.get('category')
    
    if category:
        filtered_schemes = [s for s in SCHEMES_DATA if s['category'].lower() == category.lower()]
        return jsonify({
            'success': True,
            'count': len(filtered_schemes),
            'schemes': filtered_schemes
        }), 200
    
    return jsonify({
        'success': True,
        'count': len(SCHEMES_DATA),
        'schemes': SCHEMES_DATA
    }), 200

@schemes_bp.route('/<int:scheme_id>', methods=['GET'])
def get_scheme(scheme_id):
    """
    Get specific scheme details
    """
    scheme = next((s for s in SCHEMES_DATA if s['id'] == scheme_id), None)
    
    if not scheme:
        return jsonify({'success': False, 'error': 'Scheme not found'}), 404
    
    return jsonify({
        'success': True,
        'scheme': scheme
    }), 200

@schemes_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Get all scheme categories
    """
    categories = list(set([s['category'] for s in SCHEMES_DATA]))
    
    return jsonify({
        'success': True,
        'categories': sorted(categories)
    }), 200

@schemes_bp.route('/check-eligibility', methods=['POST'])
def check_eligibility():
    """
    Check eligibility for schemes based on farmer profile
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    # Basic eligibility check
    has_land = data.get('has_land', False)
    farm_size = data.get('farm_size', 0)
    interested_in_organic = data.get('interested_in_organic', False)
    needs_credit = data.get('needs_credit', False)
    
    eligible_schemes = []
    
    for scheme in SCHEMES_DATA:
        is_eligible = True
        reasons = []
        
        if scheme['id'] == 1:  # PM-KISAN
            if has_land:
                reasons.append('You own agricultural land')
            else:
                is_eligible = False
        
        elif scheme['id'] == 4:  # KCC
            if needs_credit and has_land:
                reasons.append('You need credit and own land')
            elif not needs_credit:
                is_eligible = False
        
        elif scheme['id'] == 6:  # PKVY
            if interested_in_organic and farm_size > 0:
                reasons.append('You are interested in organic farming')
            elif not interested_in_organic:
                is_eligible = False
        
        if is_eligible:
            eligible_schemes.append({
                'scheme': scheme,
                'reasons': reasons if reasons else ['General eligibility criteria met']
            })
    
    return jsonify({
        'success': True,
        'eligible_schemes_count': len(eligible_schemes),
        'eligible_schemes': eligible_schemes
    }), 200

@schemes_bp.route('/search', methods=['GET'])
def search_schemes():
    """
    Search schemes by keyword
    """
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({'success': False, 'error': 'Search query required'}), 400
    
    results = []
    for scheme in SCHEMES_DATA:
        if (query in scheme['name'].lower() or 
            query in scheme['description'].lower() or
            query in scheme['category'].lower()):
            results.append(scheme)
    
    return jsonify({
        'success': True,
        'count': len(results),
        'results': results
    }), 200
