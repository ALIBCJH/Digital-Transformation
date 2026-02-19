#!/usr/bin/env python
"""
Test script for the redesigned backend API endpoints.
Tests: Register, Login, Altar List, Member Create, Member List
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_response(response):
    """Pretty print response"""
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception:
        print(f"Response: {response.text}")
    print()


# ============================================
# TEST 1: REGISTER NEW USER
# ============================================
print_section("TEST 1: Register New User")

register_data = {
    "first_name": "John",
    "last_name": "Doe",
    "email_or_phone": "johndoe@example.com",
    "altar": "Nyeri Main Altar",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
}

response = requests.post(f"{BASE_URL}/register/", json=register_data)
print_response(response)

# ============================================
# TEST 2: LOGIN WITH EMAIL
# ============================================
print_section("TEST 2: Login with Email")

login_data = {
    "email_or_phone": "johndoe@example.com",
    "password": "SecurePass123!"
}

response = requests.post(f"{BASE_URL}/login/", json=login_data)
print_response(response)

if response.status_code == 200:
    tokens = response.json()
    access_token = tokens.get('access')
    headers = {"Authorization": f"Bearer {access_token}"}
else:
    print("❌ Login failed, cannot proceed with authenticated tests")
    headers = {}

# ============================================
# TEST 3: LOGIN WITH DEMO ADMIN (Central)
# ============================================
print_section("TEST 3: Login as Central Admin")

admin_login_data = {
    "email_or_phone": "central@example.com",
    "password": "admin123"
}

response = requests.post(f"{BASE_URL}/login/", json=admin_login_data)
print_response(response)

if response.status_code == 200:
    admin_tokens = response.json()
    admin_access_token = admin_tokens.get('access')
    admin_headers = {"Authorization": f"Bearer {admin_access_token}"}
else:
    print("❌ Admin login failed")
    admin_headers = {}

# ============================================
# TEST 4: GET ALTAR LIST (Authenticated)
# ============================================
print_section("TEST 4: Get Altar List (as Central Admin)")

if admin_headers:
    response = requests.get(f"{BASE_URL}/altars/", headers=admin_headers)
    print_response(response)
else:
    print("⚠️ Skipped - no admin token")

# ============================================
# TEST 5: CREATE NEW MEMBER
# ============================================
print_section("TEST 5: Create New Member (as Central Admin)")

member_data = {
    "full_name": "Jane Smith",
    "phone_number": "+254712345678",
    "gender": "F",
    "serving_department": "Worship Team",
    "membership_date": datetime.now().date().isoformat(),
    "date_of_birth": "1990-05-15",
    "home_altar": "Nyeri Main Altar"
}

if admin_headers:
    response = requests.post(f"{BASE_URL}/members/create/", json=member_data, headers=admin_headers)
    print_response(response)
else:
    print("⚠️ Skipped - no admin token")

# ============================================
# TEST 6: GET MEMBER LIST
# ============================================
print_section("TEST 6: Get Member List (as Central Admin)")

if admin_headers:
    response = requests.get(f"{BASE_URL}/members/list/", headers=admin_headers)
    print_response(response)
else:
    print("⚠️ Skipped - no admin token")

# ============================================
# TEST 7: FILTER MEMBERS BY ALTAR
# ============================================
print_section("TEST 7: Filter Members by Altar")

if admin_headers:
    response = requests.get(f"{BASE_URL}/members/list/?altar=Nyeri Main Altar", headers=admin_headers)
    print_response(response)
else:
    print("⚠️ Skipped - no admin token")

# ============================================
# TEST 8: LOGIN AS NYERI ADMIN (Sub-Region Scope)
# ============================================
print_section("TEST 8: Login as Nyeri Sub-Region Admin")

nyeri_login_data = {
    "email_or_phone": "nyeri@example.com",
    "password": "admin123"
}

response = requests.post(f"{BASE_URL}/login/", json=nyeri_login_data)
print_response(response)

if response.status_code == 200:
    nyeri_tokens = response.json()
    nyeri_access_token = nyeri_tokens.get('access')
    nyeri_headers = {"Authorization": f"Bearer {nyeri_access_token}"}
    
    # Test Nyeri admin's altar access (should only see Nyeri altars)
    print_section("TEST 9: Get Altars (as Nyeri Admin - should be scoped)")
    response = requests.get(f"{BASE_URL}/altars/", headers=nyeri_headers)
    print_response(response)

# ============================================
# TEST 10: TOKEN REFRESH
# ============================================
print_section("TEST 10: Token Refresh")

if admin_tokens:
    refresh_data = {
        "refresh": admin_tokens.get('refresh')
    }
    response = requests.post(f"{BASE_URL}/token/refresh/", json=refresh_data)
    print_response(response)

# ============================================
# TEST 11: LOGOUT
# ============================================
print_section("TEST 11: Logout")

if admin_tokens and admin_headers:
    logout_data = {
        "refresh_token": admin_tokens.get('refresh')
    }
    response = requests.post(f"{BASE_URL}/logout/", json=logout_data, headers=admin_headers)
    print_response(response)

print_section("✅ All Tests Completed!")
print("\nAvailable Endpoints:")
print("  POST   /api/register/          - Register new user")
print("  POST   /api/login/             - Login with email/phone")
print("  POST   /api/logout/            - Logout (blacklist token)")
print("  POST   /api/token/refresh/     - Refresh access token")
print("  GET    /api/altars/            - List accessible altars")
print("  POST   /api/members/create/    - Create new member")
print("  GET    /api/members/list/      - List members (with ?altar=name filter)")
print("\nDemo Credentials:")
print("  Central Admin: central@example.com / admin123")
print("  Nyeri Admin:   nyeri@example.com / admin123")
print()
