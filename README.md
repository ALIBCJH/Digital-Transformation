# DT - Django Attendance Tracking System

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip and virtualenv

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DT
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and update with your settings:
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
