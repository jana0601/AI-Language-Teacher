# Database Schema Design

## Overview

The database schema supports a comprehensive language learning application with conversation analysis, user management, and progress tracking capabilities.

## Database Technology
- **Primary Database**: PostgreSQL 14+
- **Cache Layer**: Redis 6+
- **Search Engine**: Elasticsearch 8+ (for conversation search)
- **File Storage**: AWS S3 or similar (for audio/video files)

## Core Tables

### 1. Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role user_role NOT NULL DEFAULT 'student',
    language_preference VARCHAR(10) NOT NULL DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'UTC',
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TYPE user_role AS ENUM ('student', 'teacher', 'admin');
```

### 2. User Profiles Table
```sql
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    learning_goals TEXT[],
    current_level VARCHAR(10),
    target_level VARCHAR(10),
    learning_style VARCHAR(50),
    availability JSONB,
    preferences JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. Classes Table
```sql
CREATE TABLE classes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    teacher_id UUID REFERENCES users(id) ON DELETE CASCADE,
    language VARCHAR(10) NOT NULL,
    level VARCHAR(10) NOT NULL,
    max_students INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. Class Enrollments Table
```sql
CREATE TABLE class_enrollments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID REFERENCES classes(id) ON DELETE CASCADE,
    student_id UUID REFERENCES users(id) ON DELETE CASCADE,
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status enrollment_status DEFAULT 'active',
    UNIQUE(class_id, student_id)
);

CREATE TYPE enrollment_status AS ENUM ('active', 'inactive', 'suspended', 'completed');
```

### 5. Conversations Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    class_id UUID REFERENCES classes(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    topic VARCHAR(100),
    difficulty_level VARCHAR(10) NOT NULL,
    duration_seconds INTEGER,
    language VARCHAR(10) NOT NULL,
    audio_file_url TEXT,
    video_file_url TEXT,
    transcript TEXT,
    status conversation_status DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE TYPE conversation_status AS ENUM ('draft', 'recording', 'processing', 'completed', 'failed');
```

### 6. Conversation Evaluations Table
```sql
CREATE TABLE conversation_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    evaluator_id UUID REFERENCES users(id) ON DELETE SET NULL,
    overall_score DECIMAL(5,2) NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    grammar_score DECIMAL(5,2) NOT NULL CHECK (grammar_score >= 0 AND grammar_score <= 25),
    vocabulary_score DECIMAL(5,2) NOT NULL CHECK (vocabulary_score >= 0 AND vocabulary_score <= 20),
    fluency_score DECIMAL(5,2) NOT NULL CHECK (fluency_score >= 0 AND fluency_score <= 20),
    pronunciation_score DECIMAL(5,2) NOT NULL CHECK (pronunciation_score >= 0 AND pronunciation_score <= 15),
    comprehension_score DECIMAL(5,2) NOT NULL CHECK (comprehension_score >= 0 AND comprehension_score <= 20),
    proficiency_level VARCHAR(10) NOT NULL,
    strengths TEXT[],
    areas_for_improvement TEXT[],
    recommendations TEXT[],
    detailed_feedback JSONB,
    is_ai_generated BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 7. Conversation Segments Table
```sql
CREATE TABLE conversation_segments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    segment_number INTEGER NOT NULL,
    start_time DECIMAL(10,3) NOT NULL,
    end_time DECIMAL(10,3) NOT NULL,
    speaker VARCHAR(50) NOT NULL,
    text_content TEXT NOT NULL,
    confidence_score DECIMAL(5,2),
    language_detected VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 8. Grammar Errors Table
```sql
CREATE TABLE grammar_errors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    segment_id UUID REFERENCES conversation_segments(id) ON DELETE CASCADE,
    error_type VARCHAR(100) NOT NULL,
    error_description TEXT NOT NULL,
    suggested_correction TEXT,
    severity error_severity NOT NULL,
    start_position INTEGER NOT NULL,
    end_position INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE error_severity AS ENUM ('low', 'medium', 'high', 'critical');
```

### 9. Vocabulary Analysis Table
```sql
CREATE TABLE vocabulary_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    word VARCHAR(200) NOT NULL,
    frequency INTEGER NOT NULL,
    complexity_score DECIMAL(5,2),
    appropriateness_score DECIMAL(5,2),
    context VARCHAR(500),
    is_advanced BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 10. Assignments Table
```sql
CREATE TABLE assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    class_id UUID REFERENCES classes(id) ON DELETE CASCADE,
    teacher_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    instructions TEXT NOT NULL,
    topic VARCHAR(100),
    difficulty_level VARCHAR(10) NOT NULL,
    duration_minutes INTEGER,
    due_date TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 11. Assignment Submissions Table
```sql
CREATE TABLE assignment_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    assignment_id UUID REFERENCES assignments(id) ON DELETE CASCADE,
    student_id UUID REFERENCES users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status submission_status DEFAULT 'submitted',
    teacher_feedback TEXT,
    teacher_score DECIMAL(5,2),
    UNIQUE(assignment_id, student_id)
);

CREATE TYPE submission_status AS ENUM ('submitted', 'graded', 'returned', 'resubmitted');
```

### 12. Progress Tracking Table
```sql
CREATE TABLE progress_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,2) NOT NULL,
    metric_unit VARCHAR(50),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    context JSONB
);
```

### 13. Achievements Table
```sql
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    icon_url TEXT,
    criteria JSONB NOT NULL,
    points INTEGER DEFAULT 0,
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 14. User Achievements Table
```sql
CREATE TABLE user_achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    achievement_id UUID REFERENCES achievements(id) ON DELETE CASCADE,
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);
```

### 15. Practice Sessions Table
```sql
CREATE TABLE practice_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_type VARCHAR(50) NOT NULL,
    topic VARCHAR(100),
    difficulty_level VARCHAR(10),
    duration_minutes INTEGER,
    score DECIMAL(5,2),
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_data JSONB
);
```

## Indexes for Performance

```sql
-- User indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);

-- Conversation indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_class_id ON conversations(class_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_created_at ON conversations(created_at);
CREATE INDEX idx_conversations_language ON conversations(language);

-- Evaluation indexes
CREATE INDEX idx_evaluations_conversation_id ON conversation_evaluations(conversation_id);
CREATE INDEX idx_evaluations_overall_score ON conversation_evaluations(overall_score);
CREATE INDEX idx_evaluations_proficiency_level ON conversation_evaluations(proficiency_level);

-- Segment indexes
CREATE INDEX idx_segments_conversation_id ON conversation_segments(conversation_id);
CREATE INDEX idx_segments_speaker ON conversation_segments(speaker);

-- Progress tracking indexes
CREATE INDEX idx_progress_user_id ON progress_tracking(user_id);
CREATE INDEX idx_progress_metric_name ON progress_tracking(metric_name);
CREATE INDEX idx_progress_recorded_at ON progress_tracking(recorded_at);
```

## Database Views

### 1. User Progress Summary View
```sql
CREATE VIEW user_progress_summary AS
SELECT 
    u.id as user_id,
    u.username,
    u.first_name,
    u.last_name,
    COUNT(c.id) as total_conversations,
    AVG(ce.overall_score) as average_score,
    MAX(ce.proficiency_level) as current_level,
    MAX(c.created_at) as last_conversation_date
FROM users u
LEFT JOIN conversations c ON u.id = c.user_id
LEFT JOIN conversation_evaluations ce ON c.id = ce.conversation_id
WHERE u.role = 'student'
GROUP BY u.id, u.username, u.first_name, u.last_name;
```

### 2. Class Performance View
```sql
CREATE VIEW class_performance AS
SELECT 
    cl.id as class_id,
    cl.name as class_name,
    cl.language,
    cl.level,
    COUNT(DISTINCT ce.student_id) as enrolled_students,
    COUNT(c.id) as total_conversations,
    AVG(ce.overall_score) as average_class_score,
    COUNT(DISTINCT a.id) as total_assignments
FROM classes cl
LEFT JOIN class_enrollments ce ON cl.id = ce.class_id
LEFT JOIN conversations c ON ce.student_id = c.user_id
LEFT JOIN assignments a ON cl.id = a.class_id
GROUP BY cl.id, cl.name, cl.language, cl.level;
```

## Data Retention Policies

### Conversation Data
- **Audio/Video Files**: Retained for 2 years, then archived
- **Transcripts**: Retained indefinitely for analysis
- **Evaluations**: Retained indefinitely for progress tracking

### User Data
- **Inactive Accounts**: Archived after 2 years of inactivity
- **Progress Data**: Retained indefinitely
- **Personal Information**: Can be deleted upon request (GDPR compliance)

## Backup Strategy

### Automated Backups
- **Daily Incremental**: PostgreSQL WAL archiving
- **Weekly Full**: Complete database dump
- **Monthly Archive**: Long-term storage backup

### Disaster Recovery
- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 1 hour
- **Cross-region Replication**: For critical data

## Security Considerations

### Data Encryption
- **At Rest**: AES-256 encryption for sensitive data
- **In Transit**: TLS 1.3 for all connections
- **Database**: Transparent Data Encryption (TDE)

### Access Control
- **Role-based Access**: Granular permissions
- **Audit Logging**: All database operations logged
- **Connection Limits**: Per-user connection limits

### Compliance
- **GDPR**: Right to be forgotten, data portability
- **FERPA**: Educational records protection
- **SOC 2**: Security and availability controls
