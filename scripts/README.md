# Language Teacher Application - Development Scripts

## Setup Scripts

### setup-dev.sh
```bash
#!/bin/bash
# Development environment setup script

echo "Setting up Language Teacher Application..."

# Check prerequisites
echo "Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "Node.js is required but not installed. Aborting." >&2; exit 1; }
command -v psql >/dev/null 2>&1 || { echo "PostgreSQL is required but not installed. Aborting." >&2; exit 1; }
command -v redis-server >/dev/null 2>&1 || { echo "Redis is required but not installed. Aborting." >&2; exit 1; }

# Backend setup
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Frontend setup
echo "Setting up frontend..."
cd frontend
npm install
cd ..

# Database setup
echo "Setting up database..."
createdb language_teacher 2>/dev/null || echo "Database already exists"
cd backend
source venv/bin/activate
alembic upgrade head
cd ..

# Environment setup
echo "Setting up environment..."
if [ ! -f .env ]; then
    cp env.example .env
    echo "Please edit .env file with your API keys and configuration"
fi

echo "Setup complete! Run 'npm run dev' to start development servers."
```

### start-dev.sh
```bash
#!/bin/bash
# Start development servers

echo "Starting Language Teacher Application..."

# Start Redis
echo "Starting Redis..."
redis-server --daemonize yes

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "Development servers started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"

# Wait for user to stop
echo "Press Ctrl+C to stop all servers"
trap "kill $BACKEND_PID $FRONTEND_PID; redis-cli shutdown; exit" INT
wait
```

## Database Scripts

### init-db.sql
```sql
-- Initialize database with basic data

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Insert default achievements
INSERT INTO achievements (id, name, description, icon_url, criteria, points, category) VALUES
    (uuid_generate_v4(), 'First Conversation', 'Complete your first conversation', '/icons/first-conversation.png', '{"conversations": 1}', 10, 'milestone'),
    (uuid_generate_v4(), 'Grammar Master', 'Achieve 90% grammar score', '/icons/grammar-master.png', '{"grammar_score": 22.5}', 25, 'skill'),
    (uuid_generate_v4(), 'Vocabulary Builder', 'Use 50 advanced words', '/icons/vocabulary-builder.png', '{"advanced_words": 50}', 30, 'skill'),
    (uuid_generate_v4(), 'Fluency Champion', 'Maintain 95% fluency score', '/icons/fluency-champion.png', '{"fluency_score": 19}', 20, 'skill'),
    (uuid_generate_v4(), 'Pronunciation Pro', 'Achieve 90% pronunciation score', '/icons/pronunciation-pro.png', '{"pronunciation_score": 13.5}', 15, 'skill'),
    (uuid_generate_v4(), 'Comprehension Expert', 'Score 95% on comprehension', '/icons/comprehension-expert.png', '{"comprehension_score": 19}', 20, 'skill'),
    (uuid_generate_v4(), 'Level Up', 'Reach next proficiency level', '/icons/level-up.png', '{"level_progression": true}', 50, 'milestone'),
    (uuid_generate_v4(), 'Streak Master', 'Practice for 7 consecutive days', '/icons/streak-master.png', '{"consecutive_days": 7}', 40, 'consistency'),
    (uuid_generate_v4(), 'Speed Talker', 'Speak at optimal pace', '/icons/speed-talker.png', '{"wpm_range": [120, 180]}', 15, 'fluency'),
    (uuid_generate_v4(), 'Perfect Session', 'Achieve 100% overall score', '/icons/perfect-session.png', '{"overall_score": 100}', 100, 'achievement');

-- Insert sample conversation topics
INSERT INTO conversation_topics (id, name, description, difficulty_level, category) VALUES
    (uuid_generate_v4(), 'Introductions', 'Basic self-introduction and greetings', 'A1', 'social'),
    (uuid_generate_v4(), 'Daily Routine', 'Describing daily activities and schedules', 'A2', 'personal'),
    (uuid_generate_v4(), 'Food and Cooking', 'Discussing food preferences and cooking', 'B1', 'lifestyle'),
    (uuid_generate_v4(), 'Travel and Tourism', 'Planning trips and describing destinations', 'B2', 'travel'),
    (uuid_generate_v4(), 'Technology and Innovation', 'Discussing modern technology and its impact', 'C1', 'academic'),
    (uuid_generate_v4(), 'Environmental Issues', 'Debating environmental challenges and solutions', 'C2', 'academic');

-- Insert sample practice exercises
INSERT INTO practice_exercises (id, title, description, type, difficulty_level, duration_minutes, instructions) VALUES
    (uuid_generate_v4(), 'Role Play: Job Interview', 'Practice answering common interview questions', 'roleplay', 'B2', 15, 'You are applying for a software developer position. Answer the interviewer''s questions professionally.'),
    (uuid_generate_v4(), 'Storytelling: Childhood Memory', 'Tell a story about a memorable childhood experience', 'storytelling', 'B1', 10, 'Describe a childhood memory in detail. Include emotions, sensory details, and the impact it had on you.'),
    (uuid_generate_v4(), 'Debate: Social Media Impact', 'Argue for or against the impact of social media on society', 'debate', 'C1', 20, 'Take a position on social media''s impact and support your argument with examples and reasoning.'),
    (uuid_generate_v4(), 'Description: Your Hometown', 'Describe your hometown to someone who has never been there', 'description', 'A2', 8, 'Describe your hometown including its location, population, main attractions, and what makes it special.'),
    (uuid_generate_v4(), 'Problem Solving: Planning a Party', 'Plan a birthday party with specific constraints', 'problem_solving', 'B1', 12, 'Plan a birthday party for 20 people with a budget of $200. Consider venue, food, entertainment, and decorations.');
```

### reset-db.sh
```bash
#!/bin/bash
# Reset database to clean state

echo "Resetting database..."

# Drop and recreate database
dropdb language_teacher
createdb language_teacher

# Run migrations
cd backend
source venv/bin/activate
alembic upgrade head

# Seed with initial data
psql -d language_teacher -f ../scripts/init-db.sql

echo "Database reset complete!"
```

## Testing Scripts

### run-tests.sh
```bash
#!/bin/bash
# Run all tests

echo "Running Language Teacher Application tests..."

# Backend tests
echo "Running backend tests..."
cd backend
source venv/bin/activate
pytest --cov=app --cov-report=html --cov-report=term
cd ..

# Frontend tests
echo "Running frontend tests..."
cd frontend
npm test -- --coverage --watchAll=false
cd ..

echo "All tests completed!"
```

### test-api.sh
```bash
#!/bin/bash
# Test API endpoints

echo "Testing API endpoints..."

# Start backend if not running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "Starting backend..."
    cd backend
    source venv/bin/activate
    uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    sleep 5
    cd ..
fi

# Test endpoints
echo "Testing health endpoint..."
curl -f http://localhost:8000/health || echo "Health check failed"

echo "Testing API documentation..."
curl -f http://localhost:8000/docs || echo "API docs not accessible"

echo "Testing authentication..."
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123","first_name":"Test","last_name":"User"}' \
  || echo "Registration test failed"

echo "API tests completed!"
```

## Deployment Scripts

### deploy.sh
```bash
#!/bin/bash
# Deploy application to production

echo "Deploying Language Teacher Application..."

# Build frontend
echo "Building frontend..."
cd frontend
npm run build
cd ..

# Build backend Docker image
echo "Building backend Docker image..."
docker build -t language-teacher-backend ./backend

# Deploy with Docker Compose
echo "Deploying with Docker Compose..."
docker-compose -f docker-compose.prod.yml up -d

echo "Deployment complete!"
```

### backup-db.sh
```bash
#!/bin/bash
# Backup database

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/language_teacher_$DATE.sql"

echo "Creating database backup..."

mkdir -p $BACKUP_DIR
pg_dump language_teacher > $BACKUP_FILE

echo "Backup created: $BACKUP_FILE"
```

## Utility Scripts

### check-deps.sh
```bash
#!/bin/bash
# Check system dependencies

echo "Checking system dependencies..."

# Check Python
if command -v python3 >/dev/null 2>&1; then
    echo "✓ Python 3: $(python3 --version)"
else
    echo "✗ Python 3: Not installed"
fi

# Check Node.js
if command -v node >/dev/null 2>&1; then
    echo "✓ Node.js: $(node --version)"
else
    echo "✗ Node.js: Not installed"
fi

# Check PostgreSQL
if command -v psql >/dev/null 2>&1; then
    echo "✓ PostgreSQL: $(psql --version)"
else
    echo "✗ PostgreSQL: Not installed"
fi

# Check Redis
if command -v redis-server >/dev/null 2>&1; then
    echo "✓ Redis: $(redis-server --version)"
else
    echo "✗ Redis: Not installed"
fi

# Check Docker
if command -v docker >/dev/null 2>&1; then
    echo "✓ Docker: $(docker --version)"
else
    echo "✗ Docker: Not installed"
fi

echo "Dependency check complete!"
```

### clean.sh
```bash
#!/bin/bash
# Clean up development files

echo "Cleaning up development files..."

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Remove Node.js cache
rm -rf frontend/node_modules
rm -rf frontend/build

# Remove Python virtual environment
rm -rf backend/venv

# Remove logs
rm -rf logs/*.log

# Remove temporary files
rm -rf .pytest_cache
rm -rf backend/.coverage
rm -rf frontend/coverage

echo "Cleanup complete!"
```
