#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🔨 Starting build process..."

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p media/avatars
mkdir -p media/documents

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Node.js dependencies and build Tailwind CSS
echo "🎨 Installing Node dependencies and building Tailwind CSS..."
npm install
npm run build

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --no-input

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate --no-input

echo "✅ Build completed successfully!"
