"""
FarmStories with Firebase Backend
This replaces the in-memory storage with Firebase Firestore
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from firebase_config import firebase_db

farmstories_firebase_bp = Blueprint('farmstories_firebase', __name__)

# Collection name in Firestore
STORIES_COLLECTION = 'farmstories'
LIKES_COLLECTION = 'story_likes'
COMMENTS_COLLECTION = 'story_comments'

@farmstories_firebase_bp.route('/feed')
def get_feed():
    """
    Get FarmStories feed from Firebase
    """
    try:
        if not firebase_db.initialized:
            return jsonify({
                'success': False,
                'error': 'Firebase not configured'
            }), 503
        
        # Get all stories ordered by created_at
        stories = firebase_db.get_all_documents(
            STORIES_COLLECTION, 
            limit=50, 
            order_by='created_at'
        )
        
        return jsonify({
            'success': True,
            'stories': stories,
            'total': len(stories)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@farmstories_firebase_bp.route('/story/<story_id>')
def get_story(story_id):
    """
    Get a specific story from Firebase
    """
    try:
        if not firebase_db.initialized:
            return jsonify({
                'success': False,
                'error': 'Firebase not configured'
            }), 503
        
        story = firebase_db.get_document(STORIES_COLLECTION, story_id)
        
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

@farmstories_firebase_bp.route('/like/<story_id>', methods=['POST'])
def like_story(story_id):
    """
    Like a story in Firebase
    """
    try:
        if not firebase_db.initialized:
            return jsonify({
                'success': False,
                'error': 'Firebase not configured'
            }), 503
        
        story = firebase_db.get_document(STORIES_COLLECTION, story_id)
        
        if story:
            # Increment likes
            new_likes = story.get('likes', 0) + 1
            firebase_db.update_document(
                STORIES_COLLECTION, 
                story_id, 
                {'likes': new_likes}
            )
            
            return jsonify({
                'success': True,
                'likes': new_likes
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

@farmstories_firebase_bp.route('/upload', methods=['POST'])
def upload_story():
    """
    Upload a new FarmStory to Firebase
    """
    try:
        if not firebase_db.initialized:
            return jsonify({
                'success': False,
                'error': 'Firebase not configured'
            }), 503
        
        data = request.get_json()
        
        new_story = {
            'username': data.get('username', 'Anonymous'),
            'profile_pic': '👨‍🌾',
            'title': data.get('title', 'Untitled'),
            'description': data.get('description', ''),
            'video_thumbnail': '🎥',
            'video_url': data.get('video_url', ''),  # Add actual video URL support
            'likes': 0,
            'views': 0,
            'comments': 0,
            'duration': data.get('duration', '0:30'),
            'location': data.get('location', 'India'),
            'crop': data.get('crop', 'General'),
            'timestamp': 'Just now',
            'tags': data.get('tags', [])
        }
        
        # Add to Firebase
        story_id = firebase_db.add_document(STORIES_COLLECTION, new_story)
        
        if story_id:
            new_story['id'] = story_id
            return jsonify({
                'success': True,
                'message': 'FarmStory uploaded successfully!',
                'story': new_story
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to upload story'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@farmstories_firebase_bp.route('/trending')
def get_trending():
    """
    Get trending FarmStories from Firebase (sorted by views)
    """
    try:
        if not firebase_db.initialized:
            return jsonify({
                'success': False,
                'error': 'Firebase not configured'
            }), 503
        
        # Get stories ordered by views
        stories = firebase_db.get_all_documents(
            STORIES_COLLECTION,
            limit=10,
            order_by='views'
        )
        
        return jsonify({
            'success': True,
            'stories': stories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@farmstories_firebase_bp.route('/search')
def search_stories():
    """
    Search FarmStories in Firebase
    """
    try:
        if not firebase_db.initialized:
            return jsonify({
                'success': False,
                'error': 'Firebase not configured'
            }), 503
        
        query = request.args.get('q', '').lower()
        crop = request.args.get('crop', '').lower()
        location = request.args.get('location', '').lower()
        
        # Get all stories (Firebase query limitations)
        all_stories = firebase_db.get_all_documents(STORIES_COLLECTION)
        
        filtered_stories = all_stories
        
        # Filter in Python (for more complex queries, use Firestore indexes)
        if query:
            filtered_stories = [
                s for s in filtered_stories 
                if query in s.get('title', '').lower() 
                or query in s.get('description', '').lower()
                or any(query in tag for tag in s.get('tags', []))
            ]
        
        if crop:
            filtered_stories = [
                s for s in filtered_stories 
                if crop in s.get('crop', '').lower()
            ]
        
        if location:
            filtered_stories = [
                s for s in filtered_stories 
                if location in s.get('location', '').lower()
            ]
        
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

@farmstories_firebase_bp.route('/increment-view/<story_id>', methods=['POST'])
def increment_view(story_id):
    """
    Increment view count for a story
    """
    try:
        if not firebase_db.initialized:
            return jsonify({'success': False}), 503
        
        story = firebase_db.get_document(STORIES_COLLECTION, story_id)
        
        if story:
            new_views = story.get('views', 0) + 1
            firebase_db.update_document(
                STORIES_COLLECTION,
                story_id,
                {'views': new_views}
            )
            return jsonify({'success': True, 'views': new_views})
        
        return jsonify({'success': False}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@farmstories_firebase_bp.route('/my-stories/<username>')
def get_user_stories(username):
    """
    Get all stories by a specific user
    """
    try:
        if not firebase_db.initialized:
            return jsonify({
                'success': False,
                'error': 'Firebase not configured'
            }), 503
        
        stories = firebase_db.query_documents(
            STORIES_COLLECTION,
            'username',
            '==',
            username
        )
        
        return jsonify({
            'success': True,
            'stories': stories,
            'total': len(stories)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
