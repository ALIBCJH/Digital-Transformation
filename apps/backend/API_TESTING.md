# API Testing Guide

## Prerequisites

1. **Start the development server:**
   ```bash
   cd apps/backend
   source ../../venv/bin/activate
   python manage.py runserver
   ```
   Server will run at: `http://localhost:8000`

2. **Seed demo data (if not already done):**
   ```bash
   python manage.py seed_central_region
   ```

## Demo Credentials

| User | Email | Password | Scope | Can Manage |
|------|-------|----------|-------|------------|
| **Central Admin** | central@example.com | admin123 | Central Region | All 6 sub-regions + 8 altars |
| **Nyeri Admin** | nyeri@example.com | admin123 | Nyeri Sub-Region | Only Nyeri altars (2 altars) |

## Available Endpoints

### Authentication
- `POST /api/register/` - Register new user
- `POST /api/login/` - Login with email/phone
- `POST /api/logout/` - Logout (blacklist token)
- `POST /api/token/refresh/` - Refresh access token

### Altars
- `GET /api/altars/` - List accessible altars (filtered by admin_scope)

### Members
- `POST /api/members/create/` - Create new member
- `GET /api/members/list/` - List members (with optional `?altar=name` filter)

## Testing Methods

### Method 1: Bash Script (Recommended)

```bash
cd apps/backend
./test_endpoints.sh
```

This will test all endpoints in sequence and display formatted JSON responses.

### Method 2: Python Script

```bash
cd apps/backend
source ../../venv/bin/activate
python test_endpoints.py
```

### Method 3: Postman/Thunder Client

1. Import `postman_collection.json` into Postman or Thunder Client
2. The collection includes:
   - Pre-configured requests for all endpoints
   - Auto-save of access tokens
   - Example payloads
3. Run requests in order (Authentication → Altars → Members)

### Method 4: Manual curl Commands

#### Register New User
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email_or_phone": "johndoe@example.com",
    "altar": "Nyeri Main Altar",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
  }'
```

**Expected Response:**
```json
{
  "message": "Registration successful. Please login to continue."
}
```

#### Login
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "central@example.com",
    "password": "admin123"
  }'
```

**Expected Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "firstName": "Central",
    "lastName": "Admin",
    "role": "admin"
  }
}
```

#### Get Altars (Authenticated)
```bash
# Save the access token from login response
TOKEN="your_access_token_here"

curl -X GET http://localhost:8000/api/altars/ \
  -H "Authorization: Bearer ${TOKEN}"
```

**Expected Response (Central Admin):**
```json
{
  "count": 8,
  "altars": [
    {"id": 1, "name": "Nyeri Main Altar", "city": "Nyeri"},
    {"id": 2, "name": "Nyeri West Altar", "city": "Nyeri"},
    {"id": 3, "name": "Mweiga Altar", "city": "Mweiga"},
    ...
  ]
}
```

**Expected Response (Nyeri Admin):**
```json
{
  "count": 2,
  "altars": [
    {"id": 1, "name": "Nyeri Main Altar", "city": "Nyeri"},
    {"id": 2, "name": "Nyeri West Altar", "city": "Nyeri"}
  ]
}
```

#### Create Member
```bash
curl -X POST http://localhost:8000/api/members/create/ \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Smith",
    "phone_number": "+254712345678",
    "gender": "F",
    "serving_department": "Worship Team",
    "membership_date": "2026-02-18",
    "date_of_birth": "1990-05-15",
    "home_altar": "Nyeri Main Altar"
  }'
```

**Expected Response:**
```json
{
  "message": "Member created successfully",
  "member": {
    "id": 1,
    "full_name": "Jane Smith",
    "phone_number": "+254712345678",
    "gender": "F",
    "serving_department": "Worship Team",
    "membership_date": "2026-02-18",
    "date_of_birth": "1990-05-15",
    "is_active": true,
    "home_altar": "Nyeri Main Altar",
    "created_at": "2026-02-18T14:30:00Z"
  }
}
```

#### Get Member List
```bash
# All members (within admin scope)
curl -X GET http://localhost:8000/api/members/list/ \
  -H "Authorization: Bearer ${TOKEN}"

# Filter by altar
curl -X GET "http://localhost:8000/api/members/list/?altar=Nyeri%20Main%20Altar" \
  -H "Authorization: Bearer ${TOKEN}"
```

## Multi-Tenant Testing

### Test Scenario: Verify Admin Scope Filtering

1. **Login as Central Admin:**
   ```bash
   curl -X POST http://localhost:8000/api/login/ \
     -H "Content-Type: application/json" \
     -d '{"email_or_phone": "central@example.com", "password": "admin123"}'
   ```
   - Should see **8 altars** (all Central region altars)

2. **Login as Nyeri Admin:**
   ```bash
   curl -X POST http://localhost:8000/api/login/ \
     -H "Content-Type: application/json" \
     -d '{"email_or_phone": "nyeri@example.com", "password": "admin123"}'
   ```
   - Should see **2 altars** (only Nyeri sub-region altars)

3. **Try to create member outside scope (should fail):**
   ```bash
   # Login as Nyeri Admin, then try to create member in Mweiga Altar
   curl -X POST http://localhost:8000/api/members/create/ \
     -H "Authorization: Bearer ${NYERI_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{
       "full_name": "Test User",
       "home_altar": "Mweiga Altar",
       ...
     }'
   ```
   - Should return **403 Forbidden** error

## Database Structure

The demo data creates this hierarchy:

```
Central Region (/CENTRAL/)
├── Nyeri Sub-Region (/CENTRAL/NYERI/)
│   ├── Nyeri Main Altar
│   └── Nyeri West Altar
├── Mweiga Sub-Region (/CENTRAL/MWEIGA/)
│   └── Mweiga Altar
├── Karatina Sub-Region (/CENTRAL/KARATINA/)
│   └── Karatina Altar
├── Chaka Sub-Region (/CENTRAL/CHAKA/)
│   └── Chaka Altar
├── Mukurweini Sub-Region (/CENTRAL/MUKURWEINI/)
│   └── Mukurweini Altar
└── Kieni Sub-Region (/CENTRAL/KIENI/)
    └── Kieni Altar
```

## Troubleshooting

### Server not starting
```bash
cd apps/backend
source ../../venv/bin/activate
python manage.py check
python manage.py runserver
```

### "Authentication credentials were not provided"
- Make sure you're including the Authorization header: `Authorization: Bearer <token>`
- Token expires after a certain time, use `/api/token/refresh/` to get a new one

### "Permission denied" errors
- Check that the user has the correct `admin_scope`
- Nyeri Admin can only manage Nyeri altars
- Central Admin can manage all Central region altars

### Database issues
```bash
# Reset and reseed
python manage.py migrate
python manage.py seed_central_region
```

## Next Steps

After verifying the endpoints work:

1. **Install pg_trgm extension** (requires PostgreSQL superuser):
   ```sql
   sudo -u postgres psql -d DTA -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
   ```

2. **Run migration 0002** to add GIN index for optimized path queries

3. **Integrate with React frontend** (apps/frontend)

4. **Add additional features:**
   - Guest onboarding (requires Guest model)
   - Member transfers (requires MemberTransferHistory model)
   - Attendance tracking (requires AttendanceLog model)
