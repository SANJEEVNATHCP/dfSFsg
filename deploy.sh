#!/bin/bash
# Quick deployment script for Linux/Mac

echo "🌾 AgroMitra - Quick Deploy Script"
echo "===================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo "✅ Please edit .env file with your configuration"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "💾 Initializing database..."
python -c "from working_app import app, db; app.app_context().push(); db.create_all(); print('✅ Database initialized')"

# Run with Gunicorn
echo "🚀 Starting production server with Gunicorn..."
echo "📍 Server will run on: http://0.0.0.0:5000"
echo "Press Ctrl+C to stop"
echo ""

gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 wsgi:app
