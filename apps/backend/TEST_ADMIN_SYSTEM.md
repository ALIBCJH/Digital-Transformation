# Admin System Testing Guide

## Understanding the Admin Hierarchy

**All users are admins** - this system is designed for church administrators only. There are no "member" login accounts.

### Admin Levels:
1. **Superadmin (is_superuser=True)** - Sees all data across all regions globally
2. **Regional Admin** - Manages an entire region (e.g., Central Region) and all its sub-regions and altars
3. **Sub-Regional Admin** - Manages a sub-region (e.g., Nyeri) and all altars within it
4. **Altar Admin** - Manages a single altar (e.g., Nyeri Main Altar)

## Endpoints

### 1. Register Altar Admin (Public)
**Endpoint:** `POST /api/register/`

Creates an admin for a specific altar. This admin can manage members at their altar.

```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Simon",
    "last_name": "Kamau",
    "email_or_phone": "simon.kamau@example.com",
    "altar": "Nyeri Main Altar",
    "password": "admin123",
    "password2": "admin123"
  }'
```

**Response:**
```json
{
  "message": "Admin account created successfully. Please login to continue."
}
```

**What happens:**
- User is created with `is_staff=True` (admin role)
- `admin_scope` is set to the altar's parent node (e.g., NYERI sub-region)
- Can now manage members at their altar

---

### 2. Create Regional Admin (Superuser Only)
**Endpoint:** `POST /api/admin/create-regional/`

Creates an admin who can manage an entire region or sub-region. **Only superusers can access this.**

```bash
# First, get superuser token
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "admin@example.com",
    "password": "admin123"
  }'

# Then create regional admin (use the access token from above)
curl -X POST http://localhost:8000/api/admin/create-regional/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "first_name": "John",
    "last_name": "Mwangi",
    "email_or_phone": "john.central@example.com",
    "scope_code": "CENTRAL",
    "password": "admin123"
  }'
```

**Scope Codes Available:**
- `CENTRAL` - Central Region (manages all 6 sub-regions)
- `NYERI` - Nyeri Sub-Region (manages 2 altars)
- `MWEIGA` - Mweiga Sub-Region (manages 1 altar)
- `KARATINA` - Karatina Sub-Region (manages 1 altar)
- `CHAKA` - Chaka Sub-Region (manages 1 altar)
- `MUKURWEINI` - Mukurweini Sub-Region (manages 1 altar)
- `KIENI` - Kieni Sub-Region (manages 1 altar)

**Response:**
```json
{
  "message": "Regional admin created successfully for Central Region",
  "admin": {
    "username": "john.mwangi",
    "firstName": "John",
    "lastName": "Mwangi",
    "scope": "CENTRAL",
    "scopeName": "Central Region",
    "scopeDepth": 0
  }
}
```

---

### 3. Login (All Admins)
**Endpoint:** `POST /api/login/`

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "simon.kamau@example.com",
    "password": "admin123"
  }'
```

**Response (Altar Admin):**
```json
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci...",
  "user": {
    "firstName": "Simon",
    "lastName": "Kamau",
    "role": "admin",
    "scope": "NYERI",
    "scopeName": "Nyeri Sub-Region",
    "homeAltar": "Nyeri Main Altar"
  }
}
```

**Response (Regional Admin):**
```json
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci...",
  "user": {
    "firstName": "John",
    "lastName": "Mwangi",
    "role": "admin",
    "scope": "CENTRAL",
    "scopeName": "Central Region",
    "homeAltar": null
  }
}
```

**Response (Superadmin):**
```json
{
  "access": "eyJhbGci...",
  "refresh": "eyJhbGci...",
  "user": {
    "firstName": "Super",
    "lastName": "Admin",
    "role": "superadmin",
    "scope": "global",
    "scopeName": "All Regions",
    "homeAltar": null
  }
}
```

---

## Testing Workflow

### Step 1: Login as Superadmin
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "admin@example.com",
    "password": "admin123"
  }'
```

Save the `access` token.

### Step 2: Create Central Region Admin
```bash
curl -X POST http://localhost:8000/api/admin/create-regional/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <SUPERADMIN_TOKEN>" \
  -d '{
    "first_name": "Central",
    "last_name": "Admin",
    "email_or_phone": "central@example.com",
    "scope_code": "CENTRAL",
    "password": "admin123"
  }'
```

### Step 3: Create Nyeri Sub-Region Admin
```bash
curl -X POST http://localhost:8000/api/admin/create-regional/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <SUPERADMIN_TOKEN>" \
  -d '{
    "first_name": "Nyeri",
    "last_name": "Admin",
    "email_or_phone": "nyeri@example.com",
    "scope_code": "NYERI",
    "password": "admin123"
  }'
```

### Step 4: Register Altar Admin (Public - No Token Needed)
```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Altar",
    "last_name": "Admin",
    "email_or_phone": "altar.nyeri@example.com",
    "altar": "Nyeri Main Altar",
    "password": "admin123",
    "password2": "admin123"
  }'
```

### Step 5: Test Each Admin's Access

**Central Admin (sees all 6 sub-regions + 8 altars):**
```bash
# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email_or_phone": "central@example.com", "password": "admin123"}'

# List altars (should see all 8 altars)
curl -X GET http://localhost:8000/api/altars/ \
  -H "Authorization: Bearer <CENTRAL_ADMIN_TOKEN>"
```

**Nyeri Admin (sees only Nyeri's 2 altars):**
```bash
# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email_or_phone": "nyeri@example.com", "password": "admin123"}'

# List altars (should see only 2 altars: Nyeri Main + Nyeri Branch)
curl -X GET http://localhost:8000/api/altars/ \
  -H "Authorization: Bearer <NYERI_ADMIN_TOKEN>"
```

**Altar Admin (sees only their altar):**
```bash
# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email_or_phone": "altar.nyeri@example.com", "password": "admin123"}'

# List altars (should see only 1 altar: Nyeri Main Altar)
curl -X GET http://localhost:8000/api/altars/ \
  -H "Authorization: Bearer <ALTAR_ADMIN_TOKEN>"
```

---

## Summary

✅ **All users are admins** - No "member" role exists  
✅ **3 Admin Levels:**
- Superadmin (global access)
- Regional/Sub-Regional Admin (region/sub-region scope)
- Altar Admin (single altar scope)

✅ **2 Signup Methods:**
- `/api/register/` - Public, creates altar-level admin
- `/api/admin/create-regional/` - Superuser only, creates regional admin

✅ **Login Response includes:**
- `role`: "superadmin" or "admin"
- `scope`: Organization code (e.g., "CENTRAL", "NYERI") or "global"
- `scopeName`: Human-readable scope name
- `homeAltar`: Altar name (for altar admins) or null

