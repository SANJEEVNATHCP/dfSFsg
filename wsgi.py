"""
WSGI Entry Point for Production Deployment
Use with Gunicorn, uWSGI, or other WSGI servers
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app

# For Gunicorn: gunicorn backend.wsgi:app
# For uWSGI: uwsgi --http :5000 --wsgi-file backend/wsgi.py --callable app

if __name__ == "__main__":
    app.run()
