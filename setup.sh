#!/bin/bash

# Language Teacher Application - Quick Start Script

echo "🚀 Starting Language Teacher Application with LLaMA..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.9+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 16+"
    exit 1
fi

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "⚠️  PostgreSQL is not running. Please start PostgreSQL first."
    echo "   On Ubuntu/Debian: sudo systemctl start postgresql"
    echo "   On macOS: brew services start postgresql"
    echo "   On Windows: Start PostgreSQL service"
fi

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment configuration..."
    cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/language_teacher
REDIS_URL=redis://localhost:6379

# Security Configuration
SECRET_KEY=your_secret_key_here_minimum_32_characters_change_this_in_production
JWT_SECRET_KEY=your_jwt_secret_key_here_minimum_32_characters_change_this_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# LLaMA Model Configuration
LLAMA_MODEL_NAME=meta-llama/Llama-2-7b-chat-hf
LLAMA_MAX_LENGTH=1024
LLAMA_TEMPERATURE=0.7

# Analysis Settings
ANALYSIS_TIMEOUT_SECONDS=300
CACHE_ANALYSIS_RESULTS=True
CACHE_TTL_HOURS=24

# File Upload Limits
MAX_FILE_SIZE_MB=100
ALLOWED_AUDIO_FORMATS=mp3,wav,webm,ogg
EOF
    echo "✅ Environment file created. Please edit .env with your configuration."
fi

# Setup backend
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create database if it doesn't exist
echo "Creating database..."
createdb language_teacher 2>/dev/null || echo "Database already exists"

# Run database migrations (if alembic is set up)
if [ -d "alembic" ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

cd ..

# Setup frontend
echo "📦 Setting up React frontend..."
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the application:"
echo "1. Backend:  cd backend && source venv/bin/activate && uvicorn app.main:app --reload --port 8000"
echo "2. Frontend: cd frontend && npm start"
echo ""
echo "Or use Docker: docker-compose up -d"
echo ""
echo "📚 Documentation: Check the docs/ directory for detailed information"
echo "🔧 Configuration: Edit .env file for your specific setup"
echo ""
echo "⚠️  Note: LLaMA model will be downloaded on first run (several GB)"
echo "   Make sure you have sufficient disk space and internet connection"
