from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
import os
import json

farmstories_bp = Blueprint('farmstories', __name__)

# Sample FarmStories data
SAMPLE_STORIES = [
    {
        'id': 1,
        'username': 'RajeshFarmer',
        'profile_pic': '👨‍🌾',
        'title': 'Organic Tomato Harvest',
        'description': 'My first organic tomato harvest! 50kg in 2 months. No chemicals, just natural farming. 🍅',
        'video_thumbnail': '🎥',
        'likes': 245,
        'views': 1203,
        'comments': 34,
        'duration': '0:45',
        'location': 'Punjab',
        'crop': 'Tomatoes',
        'timestamp': '2 hours ago',
        'tags': ['organic', 'tomatoes', 'success']
    },
    {
        'id': 2,
        'username': 'PriyaAgri',
        'profile_pic': '👩‍🌾',
        'title': 'Smart Irrigation Technique',
        'description': 'Saved 40% water with drip irrigation. Best decision for my farm! 💧',
        'video_thumbnail': '🎥',
        'likes': 189,
        'views': 892,
        'comments': 28,
        'duration': '1:20',
        'location': 'Maharashtra',
        'crop': 'Cotton',
        'timestamp': '5 hours ago',
        'tags': ['irrigation', 'water-saving', 'tips']
    },
    {
        'id': 3,
        'username': 'KumarFarms',
        'profile_pic': '👨‍🌾',
        'title': 'Rice Transplantation Day',
        'description': 'Team work makes the dream work! Rice transplantation completed in 3 days. 🌾',
        'video_thumbnail': '🎥',
        'likes': 312,
        'views': 1567,
        'comments': 45,
        'duration': '0:58',
        'location': 'Tamil Nadu',
        'crop': 'Rice',
        'timestamp': '1 day ago',
        'tags': ['rice', 'teamwork', 'farming']
    },
    {
        'id': 4,
        'username': 'GreenThumbGita',
        'profile_pic': '👩‍🌾',
        'title': 'Natural Pest Control',
        'description': 'Using neem oil spray to control pests naturally. No chemicals needed! 🌿',
        'video_thumbnail': '🎥',
        'likes': 428,
        'views': 2134,
        'comments': 67,
        'duration': '1:45',
        'location': 'Gujarat',
        'crop': 'Vegetables',
        'timestamp': '2 days ago',
        'tags': ['organic', 'pest-control', 'neem']
    },
    {
        'id': 5,
        'username': 'SunnyHarvest',
        'profile_pic': '👨‍🌾',
        'title': 'Wheat Harvest Success',
        'description': 'Record breaking wheat harvest this season! Hard work pays off. 🌾✨',
        'video_thumbnail': '🎥',
        'likes': 567,
        'views': 3421,
        'comments': 89,
        'duration': '2:10',
        'location': 'Haryana',
        'crop': 'Wheat',
        'timestamp': '3 days ago',
        'tags': ['wheat', 'harvest', 'success']
    },
    {
        'id': 6,
        'username': 'BioFarmBharat',
        'profile_pic': '👨‍🌾',
        'title': 'Composting Tutorial',
        'description': 'How I make organic compost from farm waste. Free fertilizer! ♻️',
        'video_thumbnail': '🎥',
        'likes': 391,
        'views': 1876,
        'comments': 52,
        'duration': '3:05',
        'location': 'Kerala',
        'crop': 'Mixed',
        'timestamp': '4 days ago',
        'tags': ['compost', 'organic', 'tutorial']
    },
    {
        'id': 7,
        'username': 'ModernKisan',
        'profile_pic': '👨‍🌾',
        'title': 'Drone Spraying Demo',
        'description': 'Using drone technology for pesticide spraying. Future of farming! 🚁',
        'video_thumbnail': '🎥',
        'likes': 623,
        'views': 4152,
        'comments': 112,
        'duration': '1:30',
        'location': 'Karnataka',
        'crop': 'Cotton',
        'timestamp': '5 days ago',
        'tags': ['technology', 'drone', 'modern-farming']
    },
    {
        'id': 8,
        'username': 'OrganicOdisha',
        'profile_pic': '👩‍🌾',
        'title': 'Vermicompost Making',
        'description': 'Step by step guide to vermicompost production. Worms are farmers best friends! 🪱',
        'video_thumbnail': '🎥',
        'likes': 276,
        'views': 1345,
        'comments': 41,
        'duration': '2:45',
        'location': 'Odisha',
        'crop': 'Vegetables',
        'timestamp': '1 week ago',
        'tags': ['vermicompost', 'organic', 'tutorial']
    }
]

@farmstories_bp.route('/feed')
def get_feed():
    """
    Get FarmStories feed
    """
    try:
        # In a real app, this would fetch from database with pagination
        return jsonify({
            'success': True,
            'stories': SAMPLE_STORIES,
            'total': len(SAMPLE_STORIES)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@farmstories_bp.route('/story/<int:story_id>')
def get_story(story_id):
    """
    Get a specific story
    """
    try:
        story = next((s for s in SAMPLE_STORIES if s['id'] == story_id), None)
        if story:
            return jsonify({
                'success': True,
                'story': story
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Story not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@farmstories_bp.route('/like/<int:story_id>', methods=['POST'])
def like_story(story_id):
    """
    Like a story
    """
    try:
        story = next((s for s in SAMPLE_STORIES if s['id'] == story_id), None)
        if story:
            story['likes'] += 1
            return jsonify({
                'success': True,
                'likes': story['likes']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Story not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@farmstories_bp.route('/upload', methods=['POST'])
def upload_story():
    """
    Upload a new FarmStory
    """
    try:
        data = request.get_json()
        
        new_story = {
            'id': len(SAMPLE_STORIES) + 1,
            'username': data.get('username', 'Anonymous'),
            'profile_pic': '👨‍🌾',
            'title': data.get('title', 'Untitled'),
            'description': data.get('description', ''),
            'video_thumbnail': '🎥',
            'likes': 0,
            'views': 0,
            'comments': 0,
            'duration': data.get('duration', '0:30'),
            'location': data.get('location', 'India'),
            'crop': data.get('crop', 'General'),
            'timestamp': 'Just now',
            'tags': data.get('tags', [])
        }
        
        SAMPLE_STORIES.insert(0, new_story)
        
        return jsonify({
            'success': True,
            'message': 'FarmStory uploaded successfully!',
            'story': new_story
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@farmstories_bp.route('/trending')
def get_trending():
    """
    Get trending FarmStories (sorted by views)
    """
    try:
        trending = sorted(SAMPLE_STORIES, key=lambda x: x['views'], reverse=True)[:5]
        return jsonify({
            'success': True,
            'stories': trending
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@farmstories_bp.route('/search')
def search_stories():
    """
    Search FarmStories by tag, crop, or location
    """
    try:
        query = request.args.get('q', '').lower()
        crop = request.args.get('crop', '').lower()
        location = request.args.get('location', '').lower()
        
        filtered_stories = SAMPLE_STORIES
        
        if query:
            filtered_stories = [s for s in filtered_stories 
                              if query in s['title'].lower() 
                              or query in s['description'].lower()
                              or any(query in tag for tag in s['tags'])]
        
        if crop:
            filtered_stories = [s for s in filtered_stories if crop in s['crop'].lower()]
        
        if location:
            filtered_stories = [s for s in filtered_stories if location in s['location'].lower()]
        
        return jsonify({
            'success': True,
            'stories': filtered_stories,
            'total': len(filtered_stories)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
