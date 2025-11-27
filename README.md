# SkillMatchHub Backend

Django REST Framework backend for SkillMatchHub - a skill-based job matching platform.

## Features

- **User Authentication**: JWT-based authentication with email verification and password reset
- **User Profiles**: Comprehensive profiles for job seekers and employers with skills, experience, education, and certifications
- **Job Management**: Job posting, search, filtering, and application tracking
- **Skill-Based Matching**: Advanced matching algorithm that ranks candidates and jobs based on skill compatibility
- **Real-Time Messaging**: WebSocket-based chat system using Django Channels
- **Background Tasks**: Celery integration for email notifications and scheduled tasks
- **Admin Dashboard**: Django admin interface for platform management

## Tech Stack

- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL (with support for MySQL/SQLite)
- **Cache/Queue**: Redis
- **WebSockets**: Django Channels
- **Task Queue**: Celery
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Password Hashing**: Argon2

## Project Structure

```
backend/
├── config/                 # Django project settings
│   ├── settings.py        # Main settings
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py            # WSGI config
│   ├── asgi.py            # ASGI config (for Channels)
│   └── celery.py          # Celery configuration
├── apps/
│   ├── accounts/          # User authentication
│   ├── profiles/          # User profiles and skills
│   ├── jobs/              # Job postings and applications
│   ├── matching/          # Skill-based matching algorithm
│   ├── messaging/         # Real-time chat system
│   └── notifications/     # Email notifications (Celery tasks)
├── media/                 # User-uploaded files
├── staticfiles/           # Collected static files
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Multi-container setup
└── manage.py             # Django management script
```

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or use SQLite for development)
- Redis 7+

### Local Development Setup

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   copy .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**
   ```bash
   python manage.py runserver
   ```

8. **Run Celery worker (in separate terminal)**
   ```bash
   celery -A config worker --loglevel=info
   ```

9. **Run Celery beat (in separate terminal, optional)**
   ```bash
   celery -A config beat --loglevel=info
   ```

The API will be available at `http://localhost:8000/`
Admin interface at `http://localhost:8000/admin/`

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

The API will be available at `http://localhost:8000/`

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/token/` - Get JWT tokens
- `POST /api/auth/token/refresh/` - Refresh JWT token
- `POST /api/auth/verify-email/` - Verify email address
- `POST /api/auth/password/reset/` - Request password reset
- `POST /api/auth/password/reset/confirm/` - Confirm password reset
- `GET /api/auth/profile/` - Get current user profile
- `PUT /api/auth/profile/` - Update current user profile

### Profiles
- `GET /api/profiles/` - List profiles
- `GET /api/profiles/{id}/` - Get profile details
- `GET /api/profiles/me/` - Get current user's profile
- `PUT /api/profiles/me/` - Update current user's profile
- `GET /api/profiles/skills/` - List all skills
- `POST /api/profiles/profile-skills/` - Add skill to profile
- `POST /api/profiles/experiences/` - Add work experience
- `POST /api/profiles/education/` - Add education
- `POST /api/profiles/certifications/` - Add certification

### Jobs
- `GET /api/jobs/` - List jobs (with filters)
- `POST /api/jobs/` - Create job (employers only)
- `GET /api/jobs/{id}/` - Get job details
- `PUT /api/jobs/{id}/` - Update job (employer only)
- `DELETE /api/jobs/{id}/` - Delete job (employer only)
- `GET /api/jobs/my_jobs/` - Get employer's jobs
- `POST /api/jobs/{id}/apply/` - Apply to job
- `GET /api/jobs/applications/` - List applications
- `POST /api/jobs/saved/` - Save a job
- `DELETE /api/jobs/saved/unsave/` - Unsave a job

### Matching
- `GET /api/matching/candidates/{job_id}/` - Get matching candidates for a job (employers)
- `GET /api/matching/jobs/` - Get matching jobs for current user (job seekers)
- `GET /api/matching/skill-gap/{job_id}/` - Get skill gap analysis
- `POST /api/matching/calculate/` - Calculate match score

### Messaging
- `GET /api/messages/conversations/` - List conversations
- `POST /api/messages/conversations/` - Create conversation
- `GET /api/messages/conversations/{id}/messages/` - Get conversation messages
- `POST /api/messages/conversations/{id}/send_message/` - Send message
- `WS /ws/chat/{conversation_id}/` - WebSocket for real-time messaging

## Database Schema

Key models:
- **User**: Custom user model with email authentication
- **Profile**: User profile with bio, location, and settings
- **Skill**: Skills taxonomy
- **ProfileSkill**: M2M relationship with proficiency level and experience
- **Experience**: Work experience entries
- **Education**: Education history
- **Certification**: Professional certifications
- **Job**: Job postings with requirements
- **JobSkill**: M2M relationship with importance weights
- **Application**: Job applications with match scores
- **Conversation**: Chat conversations
- **Message**: Individual messages

## Matching Algorithm

The skill-based matching algorithm considers:
- Skill overlap between requirements and candidate skills
- Importance weight of each required skill (0.1-1.0)
- Candidate's proficiency level (beginner/intermediate/advanced/expert)
- Years of experience with each skill
- Required vs. preferred skills

Formula:
```
score = Σ(importance × skill_value) / Σ(importance)
where skill_value = level_weight + log(1 + years) × 0.15
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest apps/accounts/tests.py
```

## Deployment

### Environment Variables (Production)

```bash
DEBUG=False
SECRET_KEY=<strong-secret-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@host:5432/dbname
REDIS_URL=redis://host:6379/0
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Deployment Checklist

1. Set `DEBUG=False`
2. Set strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Set up production database (PostgreSQL recommended)
5. Configure Redis for Celery and Channels
6. Set up email service (SMTP, SendGrid, etc.)
7. Configure HTTPS/SSL
8. Set up static file serving (nginx, WhiteNoise, or CDN)
9. Set up media file storage (S3, Digital Ocean Spaces, etc.)
10. Configure CORS for frontend domain
11. Set up monitoring and logging
12. Configure backup strategy

### Deployment Options

- **Docker**: Use provided `Dockerfile` and `docker-compose.yml`
- **Heroku**: Add `Procfile` and configure add-ons
- **AWS**: Use Elastic Beanstalk or ECS
- **DigitalOcean**: App Platform or Droplet with Docker
- **Railway/Render**: Direct deployment from Git

## Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details
