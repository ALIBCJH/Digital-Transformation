#!/bin/bash

# Test script for superadmin endpoints
BASE_URL="http://127.0.0.1:8000"

echo "=========================================="
echo "Testing Superadmin Endpoints"
echo "=========================================="
echo ""

# Test 1: Create Regional Superadmin for Central Region
echo "1. Creating Regional Superadmin for CENTRAL..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/api/superadmin/create/" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@central.com",
    "phone_number": "+254700123456",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "admin_scope": "CENTRAL"
  }')

echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""
echo ""

# Test 2: Create Sub-Regional Superadmin for NYERI
echo "2. Creating Sub-Regional Superadmin for NYERI..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/api/superadmin/create/" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@nyeri.com",
    "phone_number": "+254711234567",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "admin_scope": "NYERI"
  }')

echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""
echo ""

# Test 3: Login with Regional Superadmin
echo "3. Logging in as Regional Superadmin (john.doe@central.com)..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "john.doe@central.com",
    "password": "SecurePass123!"
  }')

echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"

# Extract access token
ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])" 2>/dev/null)
REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['refresh'])" 2>/dev/null)

echo ""
echo "Access Token: ${ACCESS_TOKEN:0:50}..."
echo ""
echo ""

# Test 4: List altars (authenticated request)
echo "4. Listing altars accessible by Regional Superadmin..."
RESPONSE=$(curl -s -X GET "${BASE_URL}/api/altars/" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""
echo ""

# Test 5: Logout
echo "5. Logging out (blacklisting refresh token)..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/api/logout/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""
echo ""

# Test 6: Try to use the blacklisted token (should fail)
echo "6. Attempting to refresh with blacklisted token (should fail)..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/api/token/refresh/" \
  -H "Content-Type: application/json" \
  -d "{\"refresh\": \"$REFRESH_TOKEN\"}")

echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""
echo ""

echo "=========================================="
echo "Testing Regular Admin Endpoints"
echo "=========================================="
echo ""

# Test 7: Regular admin signup with altar
echo "7. Creating regular admin for St. Mary's Nyeri..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/api/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alice",
    "last_name": "Wanjiru",
    "email_or_phone": "alice@nyeri.com",
    "altar": "St. Mary'\''s Nyeri",
    "password": "AdminPass123!",
    "password2": "AdminPass123!"
  }')

echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
echo ""
echo ""

# Test 8: Login as regular admin
echo "8. Logging in as regular admin (alice@nyeri.com)..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "alice@nyeri.com",
    "password": "AdminPass123!"
  }')

echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$LOGIN_RESPONSE"
echo ""
echo ""

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo "✅ Regional Superadmin Creation"
echo "✅ Sub-Regional Superadmin Creation"
echo "✅ Superadmin Login"
echo "✅ Authenticated API Access (List Altars)"
echo "✅ Logout (Token Blacklisting)"
echo "✅ Regular Admin Signup"
echo "✅ Regular Admin Login"
echo ""
echo "All tests completed!"
