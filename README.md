# Digital Transformation - Modular Application

A modular church management system with separate backend (Django API) and frontend applications.

## Project Structure

```
DT/
├── apps/
│   ├── backend/          # Django REST API
│   │   ├── config/       # Django settings
│   │   ├── core/         # Main application
│   │   ├── manage.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── frontend/         # Frontend application (to be implemented)
├── Infra/                # Infrastructure configuration
├── .github/              # GitHub Actions workflows
└── venv/                 # Python virtual environment
```

## Quick Start

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd apps/backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv ../../venv
   source ../../venv/bin/activate  # On Windows: ..\..\venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp ../../.env.example ../../.env
   ```
   
   Edit `.env` at the root and update with your settings:
   - `SECRET_KEY`: Your Django secret key
   - `DB_PASSWORD`: Your PostgreSQL password
   - Other settings as needed

5. **Set up PostgreSQL database**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE DTA;
   CREATE USER postgres WITH PASSWORD 'your-password';
   GRANT ALL PRIVILEGES ON DATABASE DTA TO postgres;
   \q
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
DT/
├── config/          # Django project settings
│   ├── settings.py  # Database, JWT, REST config
│   └── urls.py      # API route definitions
├── core/            # Main app
│   ├── models.py    # Database schema
│   ├── serializers.py  # Data validation & transformation
│   ├── views.py     # API endpoints
│   └── admin.py     # Django admin interface
└── members/         # Members app
```

## API Endpoints

- `/register/` - User registration
- `/api/login/` - JWT authentication login
- `/api/token/refresh/` - Refresh JWT token

## Security Notes

- Never commit `.env` file to version control
- Always use environment variables for sensitive data
- Keep `SECRET_KEY` secret and unique per environment
- Set `DEBUG=False` in production
- Update `ALLOWED_HOSTS` for production deployment
