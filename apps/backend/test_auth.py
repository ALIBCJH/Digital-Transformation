"""
Test script for the new simplified authentication endpoints
Run with: python test_auth.py
"""

print(
    """
==============================================
SIMPLIFIED AUTHENTICATION TEST GUIDE
==============================================

1. REGISTER A NEW USER
POST http://localhost:8000/api/register/

Request Body (JSON):
{
  "first_name": "John",
  "last_name": "Kamau",
  "email_or_phone": "john.kamau@example.com",  // OR "0712345678"
  "altar": "Altar 1",
  "password": "securepass123",
  "password2": "securepass123"
}

Expected Response:
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john.kamau",
    "first_name": "John",
    "last_name": "Kamau",
    "email": "john.kamau@example.com",
    "phone_number": "",
    "altar": "Altar 1"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}

==============================================

2. LOGIN WITH EMAIL OR PHONE
POST http://localhost:8000/api/login/

Request Body (JSON) - Option 1 (Email):
{
  "email_or_phone": "john.kamau@example.com",
  "password": "securepass123"
}

Request Body (JSON) - Option 2 (Phone):
{
  "email_or_phone": "0712345678",
  "password": "securepass123"
}

Expected Response:
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "john.kamau",
    "first_name": "John",
    "last_name": "Kamau",
    "email": "john.kamau@example.com",
    "phone_number": "",
    "altar": "Altar 1",
    "is_staff": false,
    "is_superuser": false
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}

==============================================

3. USE THE ACCESS TOKEN
For authenticated requests, include the token in headers:

Authorization: Bearer <access_token>

Example:
GET http://localhost:8000/api/members/list/
Headers:
  Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

==============================================

CURL EXAMPLES:

# Register
curl -X POST http://localhost:8000/api/register/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "first_name": "John",
    "last_name": "Kamau",
    "email_or_phone": "john@example.com",
    "altar": "Altar 1",
    "password": "securepass123",
    "password2": "securepass123"
  }'

# Login
curl -X POST http://localhost:8000/api/login/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "email_or_phone": "john@example.com",
    "password": "securepass123"
  }'

==============================================

VALIDATION NOTES:
- First name and last name are required
- Email or phone number must be unique
- Password must be at least 8 characters
- Altar name must match an existing active altar in the database
- Username is auto-generated from first and last name (e.g., "john.kamau")

==============================================
"""
)
