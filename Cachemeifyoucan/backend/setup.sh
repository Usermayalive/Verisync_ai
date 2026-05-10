#!/bin/bash

# Cache Me If You Can - Setup Script
# This script automates the environment setup for the project.

set -e

echo "🚀 Starting setup for Cache Me If You Can..."

# 1. System Dependency Check
echo "🔍 Checking system dependencies..."

check_cmd() {
    if ! command -v "$1" &> /dev/null; then
        echo "⚠️  Warning: $1 is not installed. $2"
    else
        echo "✅ $1 is installed."
    fi
}

check_cmd "tesseract" "Required for OCR (image processing)."
check_cmd "ffmpeg" "Required for audio processing (podcasts)."
check_cmd "docker" "Required for the vector database."
check_cmd "node" "Required for the frontend."
check_cmd "python3" "Required for the backend."

# 2. Backend Setup
echo "🐍 Setting up Python virtual environment..."
cd "$(dirname "$0")" # Go to backend directory

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created."
fi

source venv/bin/activate
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Python dependencies installed."

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "📄 Created .env from .env.example (Don't forget to add your GOOGLE_API_KEY!)"
else
    echo "📄 .env already exists."
fi

# 3. Frontend Setup
echo "⚛️  Setting up Frontend..."
cd ../frontend

if [ ! -f ".env.local" ]; then
    cp .env.local.example .env.local
    echo "📄 Created .env.local from .env.local.example"
fi

echo "📦 Installing Node dependencies..."
npm install
echo "✅ Node dependencies installed."

echo ""
echo "✨ Setup complete!"
echo "Next steps:"
echo "1. Edit backend/.env and add your GOOGLE_API_KEY."
echo "2. Run './start_all.sh' from the root directory to start the application."
