#!/usr/bin/env python3
"""
AgroMitra Application Runner
Run this file to start the Flask development server
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.app import app

if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"\n🌾 AgroMitra Flask Server Starting...")
    print(f"📍 Server URL: http://{host}:{port}")
    print(f"🔗 Health Check: http://{host}:{port}/api/health")
    print(f"📊 States API: http://{host}:{port}/api/price/states")
    print(f"🧪 Test Page: http://{host}:{port}/test")
    print(f"🔧 Debug Mode: {debug}")
    print("Press Ctrl+C to stop\n")
    
    app.run(host=host, port=port, debug=debug)
