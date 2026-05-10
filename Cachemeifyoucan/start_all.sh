#!/bin/bash

# Cache Me If You Can - Start All Script
# This script starts the DB, Backend, and Frontend.

set -e

# --- Configuration ---
BACKEND_PORT=8000
FRONTEND_PORT=3000
BACKEND_URL="http://localhost:$BACKEND_PORT"

# --- Utility Functions ---

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0 # Port is in use
    else
        return 1 # Port is free
    fi
}

# Function to handle cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo "🐳 Stopping Vector Database..."
    docker compose down 2>/dev/null || true
    echo "✅ Cleanup complete."
    exit
}

# --- Initialization ---

# Ensure we are in the project root
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory."
    exit 1
fi

trap cleanup SIGINT SIGTERM

# Check if ports are available
if check_port $BACKEND_PORT; then
    echo "❌ Error: Port $BACKEND_PORT (Backend) is already in use."
    exit 1
fi

if check_port $FRONTEND_PORT; then
    echo "❌ Error: Port $FRONTEND_PORT (Frontend) is already in use."
    exit 1
fi

echo "🐳 Starting Vector Database (Docker)..."
docker compose up db -d

# Start Backend
echo "🐍 Starting Backend (FastAPI)..."
export PYTHONPATH="$(pwd):$PYTHONPATH"
source backend/venv/bin/activate
# Pipe logs to file and background
uvicorn backend.main:app --reload --port $BACKEND_PORT > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for Backend to be ready
echo "⏳ Waiting for backend to be ready at $BACKEND_URL..."
MAX_RETRIES=30
RETRY_COUNT=0
until $(curl --output /dev/null --silent --fail "$BACKEND_URL/health"); do
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo ""
        echo "❌ Error: Backend failed to start after $MAX_RETRIES seconds."
        echo "Check backend.log for details."
        cleanup
    fi
    printf '.'
    sleep 1
    ((RETRY_COUNT++))
done
echo " ✅ Backend is up!"

# Start Frontend
echo "⚛️  Starting Frontend (Next.js)..."
cd frontend
# Check if .env.local exists, if not warn
if [ ! -f ".env.local" ]; then
    echo "⚠️  Warning: frontend/.env.local not found. Frontend might fail."
fi

# Run npm run dev and background
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo ""
echo "🚀 Application is running!"
echo "📡 Backend API: $BACKEND_URL"
echo "🌐 Frontend UI: http://localhost:$FRONTEND_PORT"
echo "📝 Logs are being written to backend.log and frontend.log"
echo "💡 Press Ctrl+C to stop all servers."

# Keep script running to maintain processes
wait
