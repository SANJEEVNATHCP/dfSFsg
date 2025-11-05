"""
Firebase Database Initialization Script
Populates Firebase with sample data for AgroMitra
"""

from firebase_config import firebase_db
from datetime import datetime, timedelta
import random

# Sample FarmStories data to populate Firebase
SAMPLE_STORIES = [
    {
        'username': 'RajeshFarmer',
        'profile_pic': '👨‍🌾',
        'title': 'Organic Tomato Harvest',
        'description': 'My first organic tomato harvest! 50kg in 2 months. No chemicals, just natural farming. 🍅',
        'video_thumbnail': '🎥',
        'video_url': '',
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
        'username': 'PriyaAgri',
        'profile_pic': '👩‍🌾',
        'title': 'Smart Irrigation Technique',
        'description': 'Saved 40% water with drip irrigation. Best decision for my farm! 💧',
        'video_thumbnail': '🎥',
        'video_url': '',
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
        'username': 'KumarFarms',
        'profile_pic': '👨‍🌾',
        'title': 'Rice Transplantation Day',
        'description': 'Team work makes the dream work! Rice transplantation completed in 3 days. 🌾',
        'video_thumbnail': '🎥',
        'video_url': '',
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
        'username': 'GreenThumbGita',
        'profile_pic': '👩‍🌾',
        'title': 'Natural Pest Control',
        'description': 'Using neem oil spray to control pests naturally. No chemicals needed! 🌿',
        'video_thumbnail': '🎥',
        'video_url': '',
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
        'username': 'SunnyHarvest',
        'profile_pic': '👨‍🌾',
        'title': 'Wheat Harvest Success',
        'description': 'Record breaking wheat harvest this season! Hard work pays off. 🌾✨',
        'video_thumbnail': '🎥',
        'video_url': '',
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
        'username': 'BioFarmBharat',
        'profile_pic': '👨‍🌾',
        'title': 'Composting Tutorial',
        'description': 'How I make organic compost from farm waste. Free fertilizer! ♻️',
        'video_thumbnail': '🎥',
        'video_url': '',
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
        'username': 'ModernKisan',
        'profile_pic': '👨‍🌾',
        'title': 'Drone Spraying Demo',
        'description': 'Using drone technology for pesticide spraying. Future of farming! 🚁',
        'video_thumbnail': '🎥',
        'video_url': '',
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
        'username': 'OrganicOdisha',
        'profile_pic': '👩‍🌾',
        'title': 'Vermicompost Making',
        'description': 'Step by step guide to vermicompost production. Worms are farmers best friends! 🪱',
        'video_thumbnail': '🎥',
        'video_url': '',
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

def initialize_firebase_data():
    """
    Initialize Firebase with sample data
    """
    print("\n" + "="*60)
    print("🔥 Firebase Database Initialization")
    print("="*60)
    
    if not firebase_db.initialized:
        print("❌ Firebase not initialized. Please configure Firebase first.")
        print("\nSetup Instructions:")
        print("1. Go to: https://console.firebase.google.com/")
        print("2. Create a new project")
        print("3. Enable Firestore Database")
        print("4. Download service account JSON")
        print("5. Save as 'firebase-service-account.json'")
        return False
    
    print("\n📊 Initializing FarmStories collection...")
    
    stories_added = 0
    for story in SAMPLE_STORIES:
        try:
            story_id = firebase_db.add_document('farmstories', story)
            if story_id:
                stories_added += 1
                print(f"✅ Added story: {story['title']}")
            else:
                print(f"❌ Failed to add: {story['title']}")
        except Exception as e:
            print(f"❌ Error adding {story['title']}: {e}")
    
    print(f"\n✅ Successfully added {stories_added}/{len(SAMPLE_STORIES)} stories")
    
    # Initialize other collections
    print("\n📊 Initializing Users collection...")
    sample_users = [
        {
            'username': 'RajeshFarmer',
            'email': 'rajesh@example.com',
            'full_name': 'Rajesh Kumar',
            'location': 'Punjab',
            'farm_size': 5.5,
            'crops': ['Wheat', 'Rice', 'Tomatoes']
        },
        {
            'username': 'PriyaAgri',
            'email': 'priya@example.com',
            'full_name': 'Priya Sharma',
            'location': 'Maharashtra',
            'farm_size': 3.2,
            'crops': ['Cotton', 'Sugarcane']
        }
    ]
    
    users_added = 0
    for user in sample_users:
        try:
            user_id = firebase_db.add_document('users', user, user['username'])
            if user_id:
                users_added += 1
                print(f"✅ Added user: {user['username']}")
        except Exception as e:
            print(f"❌ Error adding user: {e}")
    
    print(f"\n✅ Successfully added {users_added}/{len(sample_users)} users")
    
    print("\n" + "="*60)
    print("🎉 Firebase initialization complete!")
    print("="*60)
    
    return True

def test_firebase_operations():
    """
    Test Firebase CRUD operations
    """
    print("\n" + "="*60)
    print("🧪 Testing Firebase Operations")
    print("="*60)
    
    if not firebase_db.initialized:
        print("❌ Firebase not initialized")
        return
    
    # Test: Read all stories
    print("\n1️⃣ Testing: Read all stories")
    stories = firebase_db.get_all_documents('farmstories', limit=5)
    print(f"✅ Retrieved {len(stories)} stories")
    
    # Test: Query by location
    print("\n2️⃣ Testing: Query stories by location")
    punjab_stories = firebase_db.query_documents('farmstories', 'location', '==', 'Punjab')
    print(f"✅ Found {len(punjab_stories)} stories from Punjab")
    
    # Test: Update a story
    if stories:
        print("\n3️⃣ Testing: Update story")
        first_story_id = stories[0]['id']
        success = firebase_db.update_document('farmstories', first_story_id, {'views': 9999})
        if success:
            print("✅ Successfully updated story views")
        else:
            print("❌ Failed to update story")
    
    print("\n" + "="*60)
    print("✅ Tests complete!")
    print("="*60)

if __name__ == '__main__':
    print("\n🌾 AgroMitra - Firebase Database Setup")
    print("="*60)
    
    choice = input("\nWhat would you like to do?\n1. Initialize sample data\n2. Test Firebase operations\n3. Both\n\nChoice (1/2/3): ")
    
    if choice == '1':
        initialize_firebase_data()
    elif choice == '2':
        test_firebase_operations()
    elif choice == '3':
        if initialize_firebase_data():
            test_firebase_operations()
    else:
        print("Invalid choice")
