"""
Download Large Model from Cloud Storage
This script downloads the AI model from cloud storage on app startup
"""

import os
import requests
from pathlib import Path

def download_model_from_cloud():
    """Download model file from cloud storage if not present locally"""
    
    model_path = "best_efficientnet_model.pth"
    
    # Check if model already exists
    if os.path.exists(model_path):
        print(f"✅ Model file already exists: {model_path}")
        return model_path
    
    print("📥 Downloading AI model from OneDrive...")
    
    # OneDrive Direct Download URL
    # Method: Add &download=1 to the sharing link
    
    # Original sharing link
    ONEDRIVE_SHARE_LINK = "https://1drv.ms/u/c/b66c606b71a9276f/ESciq0EPdsxJgS4nUFSyToUBPfZaejIbQ6JkWrfTInjYGg?e=FOphzX"
    
    # Convert to direct download by adding &download=1
    ONEDRIVE_URL = "https://1drv.ms/u/c/b66c606b71a9276f/ESciq0EPdsxJgS4nUFSyToUBPfZaejIbQ6JkWrfTInjYGg?e=FOphzX&download=1"
    download_url = ONEDRIVE_URL
    
    # Alternative Options:
    # Option 2: Google Drive
    # GOOGLE_DRIVE_FILE_ID = "YOUR_FILE_ID_HERE"
    # download_url = f"https://drive.google.com/uc?id={GOOGLE_DRIVE_FILE_ID}&export=download"
    
    # Option 3: Dropbox
    # DROPBOX_URL = "https://www.dropbox.com/s/YOUR_FILE_ID/best_efficientnet_model.pth?dl=1"
    
    try:
        # Download with progress
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(model_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"Progress: {percent:.1f}%", end='\r')
        
        print(f"\n✅ Model downloaded successfully: {model_path}")
        return model_path
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        print("⚠️ App will run without disease detection feature")
        return None


if __name__ == "__main__":
    download_model_from_cloud()
