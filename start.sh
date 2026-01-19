#!/bin/bash

# Cold Chain Dispatch System - Startup Script

echo "🚛 Starting Cold Chain Dispatch System..."
echo ""

# Navigate to backend directory
cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run the following commands first:"
    echo ""
    echo "  cd backend"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo "  pip install -r requirements.txt"
    echo ""
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please copy .env.example to .env and configure your API keys:"
    echo ""
    echo "  cp .env.example .env"
    echo ""
    echo "Required configuration:"
    echo "  - NAVER_MAP_CLIENT_ID (required)"
    echo "  - NAVER_MAP_CLIENT_SECRET (required)"
    echo "  - SECRET_KEY (required)"
    echo ""
    exit 1
fi

# Start the server
echo "🚀 Starting FastAPI server..."
echo ""
echo "📍 Server will be available at: http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py
