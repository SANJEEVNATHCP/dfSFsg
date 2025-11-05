"""
Firebase Configuration for AgroMitra
This file handles Firebase Admin SDK initialization and database operations
"""

import os
import json
from datetime import datetime

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, db
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️ Firebase Admin SDK not installed")

class FirebaseDB:
    def __init__(self):
        self.initialized = False
        self.firestore_db = None
        self.realtime_db = None
        
    def initialize(self, service_account_path=None, database_url=None):
        """
        Initialize Firebase with service account credentials
        
        Args:
            service_account_path: Path to Firebase service account JSON file
            database_url: Firebase Realtime Database URL (optional)
        """
        if not FIREBASE_AVAILABLE:
            print("❌ Firebase Admin SDK not available")
            return False
            
        try:
            # Check if already initialized
            if firebase_admin._apps:
                print("✅ Firebase already initialized")
                self.initialized = True
                self.firestore_db = firestore.client()
                return True
            
            # Use service account file if provided
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                
                if database_url:
                    firebase_admin.initialize_app(cred, {
                        'databaseURL': database_url
                    })
                    self.realtime_db = db.reference()
                else:
                    firebase_admin.initialize_app(cred)
                    
                self.firestore_db = firestore.client()
                self.initialized = True
                print("✅ Firebase initialized successfully")
                return True
            else:
                print("⚠️ Firebase service account file not found")
                print("📝 To use Firebase:")
                print("   1. Go to Firebase Console: https://console.firebase.google.com/")
                print("   2. Create a new project or select existing")
                print("   3. Go to Project Settings > Service Accounts")
                print("   4. Click 'Generate New Private Key'")
                print("   5. Save the JSON file as 'firebase-service-account.json' in the project root")
                return False
                
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            return False
    
    # Firestore Operations
    def add_document(self, collection, data, document_id=None):
        """Add a document to Firestore collection"""
        if not self.initialized or not self.firestore_db:
            return None
            
        try:
            data['created_at'] = datetime.utcnow()
            data['updated_at'] = datetime.utcnow()
            
            if document_id:
                doc_ref = self.firestore_db.collection(collection).document(document_id)
                doc_ref.set(data)
                return document_id
            else:
                doc_ref = self.firestore_db.collection(collection).add(data)
                return doc_ref[1].id
        except Exception as e:
            print(f"Error adding document: {e}")
            return None
    
    def get_document(self, collection, document_id):
        """Get a document from Firestore"""
        if not self.initialized or not self.firestore_db:
            return None
            
        try:
            doc = self.firestore_db.collection(collection).document(document_id).get()
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting document: {e}")
            return None
    
    def get_all_documents(self, collection, limit=None, order_by=None):
        """Get all documents from a Firestore collection"""
        if not self.initialized or not self.firestore_db:
            return []
            
        try:
            query = self.firestore_db.collection(collection)
            
            if order_by:
                query = query.order_by(order_by, direction=firestore.Query.DESCENDING)
            
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            print(f"Error getting documents: {e}")
            return []
    
    def update_document(self, collection, document_id, data):
        """Update a document in Firestore"""
        if not self.initialized or not self.firestore_db:
            return False
            
        try:
            data['updated_at'] = datetime.utcnow()
            self.firestore_db.collection(collection).document(document_id).update(data)
            return True
        except Exception as e:
            print(f"Error updating document: {e}")
            return False
    
    def delete_document(self, collection, document_id):
        """Delete a document from Firestore"""
        if not self.initialized or not self.firestore_db:
            return False
            
        try:
            self.firestore_db.collection(collection).document(document_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
    
    def query_documents(self, collection, field, operator, value):
        """Query documents in Firestore"""
        if not self.initialized or not self.firestore_db:
            return []
            
        try:
            docs = self.firestore_db.collection(collection).where(field, operator, value).stream()
            return [{'id': doc.id, **doc.to_dict()} for doc in docs]
        except Exception as e:
            print(f"Error querying documents: {e}")
            return []
    
    # Realtime Database Operations (if configured)
    def set_realtime_data(self, path, data):
        """Set data in Firebase Realtime Database"""
        if not self.initialized or not self.realtime_db:
            return False
            
        try:
            ref = self.realtime_db.child(path)
            ref.set(data)
            return True
        except Exception as e:
            print(f"Error setting realtime data: {e}")
            return False
    
    def get_realtime_data(self, path):
        """Get data from Firebase Realtime Database"""
        if not self.initialized or not self.realtime_db:
            return None
            
        try:
            ref = self.realtime_db.child(path)
            return ref.get()
        except Exception as e:
            print(f"Error getting realtime data: {e}")
            return None
    
    def push_realtime_data(self, path, data):
        """Push data to Firebase Realtime Database"""
        if not self.initialized or not self.realtime_db:
            return None
            
        try:
            ref = self.realtime_db.child(path)
            return ref.push(data)
        except Exception as e:
            print(f"Error pushing realtime data: {e}")
            return None


# Global Firebase instance
firebase_db = FirebaseDB()

# Try to initialize on import
SERVICE_ACCOUNT_FILE = 'firebase-service-account.json'
DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')  # Optional

if os.path.exists(SERVICE_ACCOUNT_FILE):
    firebase_db.initialize(SERVICE_ACCOUNT_FILE, DATABASE_URL)
else:
    print("\n" + "="*60)
    print("📝 Firebase Setup Instructions:")
    print("="*60)
    print("1. Go to: https://console.firebase.google.com/")
    print("2. Create a new project (or select existing)")
    print("3. Click on Project Settings (⚙️ icon)")
    print("4. Go to 'Service Accounts' tab")
    print("5. Click 'Generate New Private Key'")
    print("6. Save the JSON file as 'firebase-service-account.json'")
    print("7. Place it in the project root directory")
    print("="*60 + "\n")
