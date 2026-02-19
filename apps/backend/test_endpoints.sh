#!/bin/bash
# API Endpoint Test Script using curl
# Make sure the server is running: python manage.py runserver

BASE_URL="http://localhost:8000/api"

echo "============================================"
echo "  Backend API Endpoint Tests"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================
# TEST 1: Register New User
# ============================================
echo -e "${BLUE}TEST 1: Register New User${NC}"
curl -X POST "${BASE_URL}/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email_or_phone": "johndoe@example.com",
    "altar": "Nyeri Main Altar",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }' | jq '.'
echo -e "\n"

# ============================================
# TEST 2: Login with Email
# ============================================
echo -e "${BLUE}TEST 2: Login with Email${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "johndoe@example.com",
    "password": "SecurePass123!"
  }')
echo "$LOGIN_RESPONSE" | jq '.'

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access')
echo -e "\n"

# ============================================
# TEST 3: Login as Central Admin
# ============================================
echo -e "${BLUE}TEST 3: Login as Central Admin${NC}"
ADMIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "central@example.com",
    "password": "admin123"
  }')
echo "$ADMIN_RESPONSE" | jq '.'

ADMIN_TOKEN=$(echo "$ADMIN_RESPONSE" | jq -r '.access')
echo -e "\n"

# ============================================
# TEST 4: Get Altar List
# ============================================
echo -e "${BLUE}TEST 4: Get Altar List (Central Admin)${NC}"
curl -X GET "${BASE_URL}/altars/" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | jq '.'
echo -e "\n"

# ============================================
# TEST 5: Create New Member
# ============================================
echo -e "${BLUE}TEST 5: Create New Member${NC}"
curl -X POST "${BASE_URL}/members/create/" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Smith",
    "phone_number": "+254712345678",
    "gender": "F",
    "serving_department": "Worship Team",
    "membership_date": "2026-02-18",
    "date_of_birth": "1990-05-15",
    "home_altar": "Nyeri Main Altar"
  }' | jq '.'
echo -e "\n"

# ============================================
# TEST 6: Get Member List
# ============================================
echo -e "${BLUE}TEST 6: Get Member List${NC}"
curl -X GET "${BASE_URL}/members/list/" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | jq '.'
echo -e "\n"

# ============================================
# TEST 7: Filter Members by Altar
# ============================================
echo -e "${BLUE}TEST 7: Filter Members by Altar${NC}"
curl -X GET "${BASE_URL}/members/list/?altar=Nyeri%20Main%20Altar" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | jq '.'
echo -e "\n"

# ============================================
# TEST 8: Login as Nyeri Admin (Scoped Access)
# ============================================
echo -e "${BLUE}TEST 8: Login as Nyeri Sub-Region Admin${NC}"
NYERI_RESPONSE=$(curl -s -X POST "${BASE_URL}/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "nyeri@example.com",
    "password": "admin123"
  }')
echo "$NYERI_RESPONSE" | jq '.'

NYERI_TOKEN=$(echo "$NYERI_RESPONSE" | jq -r '.access')
echo -e "\n"

# ============================================
# TEST 9: Nyeri Admin - Get Altars (Should be scoped)
# ============================================
echo -e "${BLUE}TEST 9: Get Altars (Nyeri Admin - Should Only See Nyeri Altars)${NC}"
curl -X GET "${BASE_URL}/altars/" \
  -H "Authorization: Bearer ${NYERI_TOKEN}" | jq '.'
echo -e "\n"

# ============================================
# TEST 10: Token Refresh
# ============================================
echo -e "${BLUE}TEST 10: Refresh Access Token${NC}"
REFRESH_TOKEN=$(echo "$ADMIN_RESPONSE" | jq -r '.refresh')
curl -X POST "${BASE_URL}/token/refresh/" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"${REFRESH_TOKEN}\"}" | jq '.'
echo -e "\n"

# ============================================
# Summary
# ============================================
echo -e "${GREEN}✅ All Tests Completed!${NC}"
echo ""
echo "Available Endpoints:"
echo "  POST   /api/register/          - Register new user"
echo "  POST   /api/login/             - Login with email/phone"
echo "  POST   /api/logout/            - Logout (blacklist token)"
echo "  POST   /api/token/refresh/     - Refresh access token"
echo "  GET    /api/altars/            - List accessible altars"
echo "  POST   /api/members/create/    - Create new member"
echo "  GET    /api/members/list/      - List members (with ?altar=name filter)"
echo ""
echo "Demo Credentials:"
echo "  Central Admin: central@example.com / admin123"
echo "  Nyeri Admin:   nyeri@example.com / admin123"
echo ""
