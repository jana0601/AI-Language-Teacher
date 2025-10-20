# Language Teacher Application - Project Setup

## Quick Start Guide

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL 14+
- Redis 6+
- Docker (optional)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd language_teacher
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Database Setup**
```bash
# Create database
createdb language_teacher

# Run migrations
cd backend
alembic upgrade head
```

5. **Environment Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
```

6. **Start Development Servers**
```bash
# Backend (Terminal 1)
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm run dev

# Redis (Terminal 3)
redis-server
```

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/language_teacher
REDIS_URL=redis://localhost:6379

# API Keys
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CLOUD_API_KEY=your_google_cloud_api_key
AZURE_API_KEY=your_azure_api_key
WATSON_API_KEY=your_watson_api_key

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your_s3_bucket_name
AWS_REGION=us-east-1

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Docker Setup (Alternative)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
pytest tests/integration/
```

### Production Deployment

1. **Build Frontend**
```bash
cd frontend
npm run build
```

2. **Deploy Backend**
```bash
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

3. **Database Migration**
```bash
alembic upgrade head
```

### Monitoring & Logging

- **Application Logs**: Check `logs/` directory
- **Database Monitoring**: PostgreSQL logs
- **API Monitoring**: Built-in FastAPI metrics
- **Error Tracking**: Sentry integration (optional)

### Troubleshooting

#### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Ensure database exists

2. **API Key Errors**
   - Verify all API keys are valid
   - Check rate limits
   - Ensure proper permissions

3. **Audio Processing Issues**
   - Check FFmpeg installation
   - Verify audio file formats
   - Check file size limits

4. **Frontend Build Errors**
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify environment variables

#### Getting Help

- Check the documentation in `/docs`
- Review error logs
- Open an issue on GitHub
- Contact the development team

### Development Workflow

1. **Feature Development**
   - Create feature branch
   - Write tests first
   - Implement feature
   - Run tests and linting
   - Submit pull request

2. **Code Quality**
   - Follow PEP 8 (Python)
   - Follow ESLint rules (JavaScript/TypeScript)
   - Write comprehensive tests
   - Document new features

3. **Database Changes**
   - Create migration files
   - Test migrations locally
   - Review migration scripts
   - Apply to staging before production

### Performance Optimization

1. **Database**
   - Use proper indexes
   - Optimize queries
   - Monitor slow queries
   - Use connection pooling

2. **API**
   - Implement caching
   - Use async operations
   - Monitor response times
   - Implement rate limiting

3. **Frontend**
   - Code splitting
   - Lazy loading
   - Image optimization
   - Bundle analysis

### Security Considerations

1. **Authentication**
   - Use strong passwords
   - Implement 2FA
   - JWT token security
   - Session management

2. **Data Protection**
   - Encrypt sensitive data
   - Secure file uploads
   - Input validation
   - SQL injection prevention

3. **API Security**
   - Rate limiting
   - CORS configuration
   - Input sanitization
   - Error handling

### Backup Strategy

1. **Database Backups**
   - Daily automated backups
   - Point-in-time recovery
   - Cross-region replication
   - Backup testing

2. **File Backups**
   - S3 versioning
   - Cross-region replication
   - Lifecycle policies
   - Access logging

### Scaling Considerations

1. **Horizontal Scaling**
   - Load balancers
   - Multiple app instances
   - Database read replicas
   - CDN for static assets

2. **Vertical Scaling**
   - CPU optimization
   - Memory management
   - Storage optimization
   - Network optimization

### Maintenance

1. **Regular Tasks**
   - Update dependencies
   - Security patches
   - Performance monitoring
   - Log rotation

2. **Monitoring**
   - Application metrics
   - Error rates
   - Response times
   - Resource usage

### Contributing

1. **Code Style**
   - Follow project conventions
   - Use type hints (Python)
   - Use TypeScript (Frontend)
   - Write clear comments

2. **Testing**
   - Unit tests for new features
   - Integration tests for APIs
   - End-to-end tests for UI
   - Performance tests for critical paths

3. **Documentation**
   - Update README for new features
   - Document API changes
   - Add code examples
   - Update deployment guides
