"""
API Testing Guide for Postman

Base URL: http://localhost:8000

=== 1. REGISTER ADMIN USER ===
POST http://localhost:8000/api/register/

Headers:
Content-Type: application/json

Body (raw JSON):
{
    "username": "admin",
    "email": "admin@example.com",
    "password": "admin12345",
    "password2": "admin12345",
    "first_name": "Admin",
    "last_name": "User"
}

Expected Response (201):
{
    "message": "Admin user created successfully",
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "is_staff": true,
        "is_superuser": true
    }
}


=== 2. LOGIN (Get Access Token) ===
POST http://localhost:8000/api/login/

Headers:
Content-Type: application/json

Body (raw JSON):
{
    "username": "admin",
    "password": "admin12345"
}

Expected Response (200):
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}


=== 3. REFRESH TOKEN ===
POST http://localhost:8000/api/token/refresh/

Headers:
Content-Type: application/json

Body (raw JSON):
{
    "refresh": "YOUR_REFRESH_TOKEN_HERE"
}

Expected Response (200):
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}


=== 4. PROTECTED ENDPOINT (Example) ===
GET http://localhost:8000/api/protected-endpoint/

Headers:
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json

"""
