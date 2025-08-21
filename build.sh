#!/bin/bash
set -e

echo "🚀 Starting build process..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Navigate to backend directory
cd process_monitor/backend

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build completed successfully!" 