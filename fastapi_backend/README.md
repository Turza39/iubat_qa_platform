# FastAPI Backend - IUBAT Q&A Platform

A modern, production-ready FastAPI implementation of the IUBAT Q&A Platform backend with JWT authentication, user verification, dynamic tag creation, and a comprehensive voting system.

---

## 📌 Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Server](#-running-the-server)
- [API Endpoints](#-api-endpoints)
- [Authentication & JWT](#-authentication--jwt)
- [Database Setup](#-database-setup)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)
- [Contributing](#-contributing)

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.9+**
- **pip** (for dependency management)
- **PostgreSQL** (for database)

### Installation (5 minutes)

```bash
# 1. Navigate to the backend directory
cd fastapi_backend

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup PostgreSQL database (see Database Setup section)

# 5. Create environment file and configure
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 6. Run the development server
uvicorn main:app --reload
```

**Access the API:**
- API: `http://127.0.0.1:8000`
- Swagger UI (Interactive docs): `http://127.0.0.1:8000/docs`
- ReDoc (Alternative docs): `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

---

## 📋 Features

### 🔐 Authentication & User Management
- **JWT-based authentication** with access tokens
- **User registration** with email validation
- **Login/logout** functionality
- **ID verification system** with image uploads
- **User profiles** with public/private viewing options
- **Password hashing** using bcrypt

### ❓ Questions & Answers
- **CRUD operations** for questions (Create, Read, Update, Delete)
- **Dynamic tag system** - Users create their own tags, no predefined list
- **Full-text search** on question titles and content
- **Answer creation** with author-only editing/deletion
- **Tag management** - Automatic tag creation and reuse

### 🗳️ Voting System
- **Upvote/Downvote** on questions and answers
- **Toggle voting** without creating duplicate votes
- **Vote statistics** and trending calculations
- **Vote persistence** across requests

### 💾 Database
- **SQLAlchemy ORM** for database abstraction
- **PostgreSQL** for reliable data storage
- **Relationship management** (one-to-many, many-to-many)
- **Automatic table creation** on startup

---

## 📁 Project Structure

```
fastapi_backend/
├── main.py                      # FastAPI app entry point and configuration
├── config.py                    # Environment settings and configuration
├── database.py                  # Database connection and session management
├── requirements.txt             # Python package dependencies
├── .env.example                 # Environment template
├── .env                         # Environment variables (local - git ignored)
│
├── models/                      # SQLAlchemy database models
│   ├── __init__.py
│   ├── user.py                 # User model with verification
│   ├── question.py             # Question model
│   ├── answer.py               # Answer model
│   ├── vote.py                 # Vote model
│   └── tag.py                  # Tag model
│
├── schemas/                     # Pydantic request/response models
│   ├── __init__.py
│   ├── user.py                 # User DTOs (Data Transfer Objects)
│   ├── question.py             # Question DTOs
│   ├── answer.py               # Answer DTOs
│   ├── vote.py                 # Vote DTOs
│   └── tag.py                  # Tag DTOs
│
├── routes/                      # API endpoint handlers
│   ├── __init__.py
│   ├── users.py                # User endpoints (register, login, profile)
│   ├── questions.py            # Question endpoints (CRUD, search, tags)
│   ├── answers.py              # Answer endpoints (CRUD)
│   └── votes.py                # Vote endpoints (toggle, stats)
│
├── dependencies/               # Dependency injection for FastAPI
│   ├── __init__.py
│   └── auth.py                 # JWT authentication and authorization
│
├── utils/                       # Utility functions
│   ├── __init__.py
│   └── password.py             # Password hashing and validation
│
├── media/                       # Uploaded files (images, documents)
│   └── verification_images/    # User verification images
│
└── static/                      # Static files (CSS, JS, images)
```

---

## 🛠️ Installation

### Step 1: Navigate to Backend

```bash
cd fastapi_backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Key dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - ORM
- `pydantic` - Data validation
- `python-jose` & `bcrypt` - JWT & password hashing
- `psycopg2-binary` - PostgreSQL adapter
- `email-validator` - Email validation

### Step 4: Setup Environment Variables

```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials
```

---

## ⚙️ Configuration

### Environment Variables (.env)

```ini
# ============================================================
# DATABASE CONFIGURATION (PostgreSQL)
# ============================================================
DB_ENGINE=postgresql
DB_NAME=iubat_qa_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# ============================================================
# SECURITY & JWT CONFIGURATION
# ============================================================
# IMPORTANT: Change this to a random 32+ character string in production
SECRET_KEY=your-super-secret-key-change-in-production

# JWT algorithm
ALGORITHM=HS256

# Token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES=1440    # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================================
# APPLICATION CONFIGURATION
# ============================================================
DEBUG=True      # Set to False in production

ALLOWED_HOSTS=localhost,127.0.0.1

# ============================================================
# CORS CONFIGURATION (Frontend Access)
# ============================================================
# Comma-separated list of allowed frontend domains
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173

# ============================================================
# FILE UPLOAD CONFIGURATION
# ============================================================
MEDIA_ROOT=./media
MEDIA_URL=/media/

STATIC_ROOT=./static
STATIC_URL=/static/

# ============================================================
# APPLICATION SETTINGS
# ============================================================
TIMEZONE=Asia/Dhaka

# Redis and Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Optional SMTP configuration for async background emails
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=no-reply@iubatqa.local
```

### Configuration Priority

1. **Environment variables (.env file)**
2. **System environment variables**
3. **Default values in config.py**

---

## ▶️ Running the Server

### Development Mode (with auto-reload)

```bash
uvicorn main:app --reload
```

- Auto-reloads when you save files
- Debug mode enabled
- Access at: `http://localhost:8000`

### Start Celery Worker

Run Celery side-by-side with the app for async background tasks and Redis queue handling:

```bash
celery -A celery_app.celery worker --loglevel=info
```

### Custom Host/Port

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "timezone": "Asia/Dhaka"
}
```

---

## 🔌 API Endpoints

### Base URL
```
http://localhost:8000/api
```

### Users Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|-------|-------------|
| `POST` | `/users/register/` | ❌ | Register new account |
| `POST` | `/users/login/` | ❌ | Login and get JWT token |
| `GET` | `/users/profile/` | ✅ | Get current user profile |
| `PUT` | `/users/profile/` | ✅ | Update user profile |
| `GET` | `/users/{user_id}/` | ❌ | Get public user info |
| `POST` | `/users/verify/` | ✅ | Submit verification image |
| `GET` | `/users/verify/status/` | ✅ | Check verification status |

### Questions Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|-------|-------------|
| `GET` | `/questions/` | ❌ | List all questions (with search, filter, pagination) |
| `POST` | `/questions/` | ✅ | Create new question |
| `GET` | `/questions/{id}/` | ❌ | Get question details with answers |
| `PUT` | `/questions/{id}/` | ✅ | Update question (author only) |
| `DELETE` | `/questions/{id}/` | ✅ | Delete question (author only) |
| `GET` | `/questions/tags/` | ❌ | List all available tags |

### Answers Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|-------|-------------|
| `POST` | `/answers/questions/{question_id}/` | ✅ | Create answer (verified users) |
| `PUT` | `/answers/{answer_id}/` | ✅ | Update answer (author only) |
| `DELETE` | `/answers/{answer_id}/` | ✅ | Delete answer (author only) |
| `GET` | `/answers/{answer_id}/` | ❌ | Get answer details |

### Votes Endpoints

| Method | Endpoint | Auth Required | Description |
|--------|----------|-------|-------------|
| `POST` | `/votes/questions/{question_id}/` | ✅ | Toggle upvote on question |
| `POST` | `/votes/answers/{answer_id}/` | ✅ | Toggle upvote on answer |
| `GET` | `/votes/stats/` | ❌ | Get voting statistics |

---

## 🔐 Authentication & JWT

### Overview

The API uses **JWT (JSON Web Tokens)** for stateless authentication:
- **No sessions** stored on server
- **Tokens sent in requests** via `Authorization: Bearer TOKEN`
- **Token expiration** after configured time
- **Bcrypt password hashing** for security

### JWT Token Structure

```
Header.Payload.Signature

Example:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzE1MTY5NjAwfQ.signature
```

### Authentication Flow

#### 1. Register User

```bash
curl -X POST http://localhost:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!"
  }'
```

Response (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### 2. Login

```bash
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePassword123!"
  }'
```

Response (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### 3. Use Token in Requests

```bash
curl -X GET http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Protected Routes

Routes marked with `✅` require a valid JWT token in the `Authorization` header:

```
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

### Creating Questions with Tags

```bash
curl -X POST http://localhost:8000/api/questions/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "How to learn FastAPI?",
    "body": "I want to learn FastAPI. Where should I start?",
    "tags": ["python", "fastapi", "web-development"]
  }'
```

**Response (201 Created):**
```json
{
  "id": 1,
  "title": "How to learn FastAPI?",
  "body": "I want to learn FastAPI. Where should I start?",
  "author_id": 1,
  "tags": [
    {"id": 1, "name": "python", "slug": "python"},
    {"id": 2, "name": "fastapi", "slug": "fastapi"},
    {"id": 3, "name": "web-development", "slug": "web-development"}
  ],
  "created_at": "2024-05-08T10:30:00",
  "answers_count": 0,
  "votes_count": 0
}
```

**Key Features:**
- Tags are created on-the-fly if they don't exist
- Existing tags are automatically reused
- Maximum 5 tags per question
- Tag names are normalized to lowercase slugs

---

## 💾 Database Setup

### PostgreSQL Configuration

#### Step 1: Install PostgreSQL

**Windows:**
Download from [postgresql.org](https://www.postgresql.org/download/windows/)

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### Step 2: Create Database and User

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE iubat_qa_db;

# Create user
CREATE USER iubat_user WITH PASSWORD 'secure_password_here';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE iubat_qa_db TO iubat_user;

# Exit
\q
```

#### Step 3: Update Environment Variables

```env
DB_ENGINE=postgresql
DB_NAME=iubat_qa_db
DB_USER=iubat_user
DB_PASSWORD=secure_password_here
DB_HOST=localhost
DB_PORT=5432
```

#### Step 4: Test Connection

```bash
python -c "
from sqlalchemy import create_engine
from config import settings
engine = create_engine(settings.DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('✅ Database connected successfully!')
"
```

#### Step 5: Load Sample Data (Optional)

```bash
psql -U iubat_user -d iubat_qa_db -f INSERT_DUMMY_DATA.sql
```

---

## � Troubleshooting

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Windows (PowerShell)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8000
kill -9 <PID>
```

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Database connection refused"

**Solution:**
```bash
# Test PostgreSQL service status
sudo service postgresql status

# Start PostgreSQL if not running
sudo service postgresql start

# Check .env configuration
cat .env | grep DB_

# Test connection
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://user:pass@localhost:5432/db')"
```

### Issue: "JWT token invalid or expired"

**Solution:**
```bash
# Generate new token by logging in again
curl -X POST http://localhost:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use the new token in Authorization header
```

### Issue: CORS errors in frontend

**Solution in .env:**
```env
# Add your frontend origin
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-domain.com
```

---

## 👨‍💻 Development

### Code Style

Follow PEP 8 and use type hints:

```python
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/example/{item_id}")
async def get_example(
    item_id: int,
    db: Session = Depends(get_db),
    limit: Optional[int] = None
) -> dict:
    """Get example item by ID"""
    item = db.query(Item).filter(Item.id == item_id).first()
    return {"item": item}
```

### Testing

```bash
# Install pytest
pip install pytest pytest-asyncio

# Create tests
mkdir tests

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

### Linting & Formatting

```bash
# Install tools
pip install black flake8 isort

# Format code
black .

# Check style
flake8 .

# Sort imports
isort .
```

---

## 📚 Additional Resources

- **[FastAPI Documentation](https://fastapi.tiangolo.com/)**
- **[SQLAlchemy ORM](https://docs.sqlalchemy.org/)**
- **[Pydantic Validation](https://docs.pydantic.dev/)**
- **[JWT.io](https://jwt.io/)**
- **[PostgreSQL Documentation](https://www.postgresql.org/docs/)**

---

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Guidelines
- ✅ Use meaningful commit messages
- ✅ Add type hints for all functions
- ✅ Write docstrings for complex logic
- ✅ Follow PEP 8 style guide
- ✅ Add tests for new features
- ✅ Update documentation

---

## 📄 License

This project is part of the IUBAT Q&A Platform initiative.

---

## 🆘 Support

For issues, questions, or suggestions:
- 📧 Email: support@example.com
- 🐛 GitHub Issues: [Report a bug](https://github.com/your-repo/issues)
- 💬 Discussions: [Ask a question](https://github.com/your-repo/discussions)

---

**Last Updated:** May 2026  
**Version:** 1.0.0

