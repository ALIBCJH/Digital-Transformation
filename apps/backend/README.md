# Django Backend Application

This is the backend API for the Digital Transformation project.

## Structure

```
backend/
├── config/          # Django project settings
├── core/            # Main application
├── manage.py        # Django management script
├── requirements.txt # Python dependencies
├── Dockerfile       # Docker configuration
└── .dockerignore    # Docker ignore patterns
```

## Setup

### Local Development

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run development server:
```bash
python manage.py runserver
```

### Docker Deployment

Build and run with Docker:
```bash
docker build -t digital-transformation-backend .
docker run -p 8000:8000 digital-transformation-backend
```

## Environment Variables

Create a `.env` file based on `.env.example`:
- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (True/False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `DB_ENGINE` - Database engine
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host
- `DB_PORT` - Database port

## API Documentation

The API is built with Django REST Framework and includes:
- User authentication with JWT
- Member management
- Guest management
- Attendance tracking
- Organizational unit management

Access the API at: `http://localhost:8000/api/`
