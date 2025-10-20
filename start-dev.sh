#!/bin/bash

# Language Teacher Application - Development Start Script

echo "🚀 Starting Language Teacher Application in development mode..."

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Check if ports are available
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Please stop the service using this port."
    exit 1
fi

if check_port 3000; then
    echo "⚠️  Port 3000 is already in use. Please stop the service using this port."
    exit 1
fi

# Start Redis if not running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "🔄 Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi

# Start backend
echo "🐍 Starting FastAPI backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 --host 0.0.0.0 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Start frontend
echo "📦 Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 Application started!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    redis-cli shutdown 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for processes
wait
