# Superadmin API Testing Guide

## Available Endpoints

### 1. Create Regional/Sub-Regional Superadmin
**Endpoint:** `POST /api/superadmin/create/`

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/superadmin/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@central.com",
    "phone_number": "+254700123456",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "admin_scope": "CENTRAL"
  }'
```

**Available Scopes:**
- `CENTRAL` (Regional Superadmin - sees all 6 sub-regions)
- `NYERI` (Sub-Regional Superadmin - sees only Nyeri altars)
- `MWEIGA` (Sub-Regional Superadmin - sees only Mweiga altar)
- `KARATINA` (Sub-Regional Superadmin - sees only Karatina altar)
- `CHAKA` (Sub-Regional Superadmin - sees only Chaka altar)
- `MUKURWEINI` (Sub-Regional Superadmin - sees only Mukurweini altar)
- `KIENI` (Sub-Regional Superadmin - sees only Kieni altar)

**Expected Response:**
```json
{
    "message": "Regional superadmin created successfully",
    "user": {
        "id": 1,
        "username": "john.doe",
        "email": "john.doe@central.com",
        "firstName": "John",
        "lastName": "Doe",
        "adminScope": "CENTRAL",
        "role": "superadmin",
        "accessibleAltars": 8
    }
}
```

---

### 2. Login (Superadmin or Regular Admin)
**Endpoint:** `POST /api/login/`

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "john.doe@central.com",
    "password": "SecurePass123!"
  }'
```

**Expected Response:**
```json
{
    "access": "eyJhbGc...",
    "refresh": "eyJhbGc...",
    "user": {
        "firstName": "John",
        "lastName": "Doe",
        "role": "superadmin"
    }
}
```

**Role Types:**
- `superadmin` - Regional/Sub-Regional superadmin (has admin_scope)
- `admin` - Regular altar admin (is_staff=true, no admin_scope)

---

### 3. List Accessible Altars (Authenticated)
**Endpoint:** `GET /api/altars/`

**Request:**
```bash
curl -X GET http://127.0.0.1:8000/api/altars/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Expected Response (Regional Superadmin):**
```json
{
    "count": 8,
    "altars": [
        {"id": 1, "name": "St. Mary's Nyeri", "city": "Nyeri"},
        {"id": 2, "name": "St. Joseph's Ruring'u", "city": "Nyeri"},
        {"id": 3, "name": "St. Peter's Mweiga", "city": "Mweiga"},
        ...
    ]
}
```

**Expected Response (Regular Admin - St. Mary's Nyeri):**
```json
{
    "count": 0,
    "altars": []
}
```
*Note: Regular admins don't have admin_scope, so they can't see other altars via this endpoint*

---

### 4. Create Regular Altar Admin
**Endpoint:** `POST /api/register/`

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alice",
    "last_name": "Wanjiru",
    "email_or_phone": "alice@nyeri.com",
    "altar": "St. Mary'\''s Nyeri",
    "password": "AdminPass123!",
    "password2": "AdminPass123!"
  }'
```

**Expected Response:**
```json
{
    "message": "Registration successful. You are now an altar admin. Please login to continue."
}
```

---

### 5. Logout (Blacklist Refresh Token)
**Endpoint:** `POST /api/logout/`

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/logout/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

**Expected Response:**
```json
{
    "message": "Successfully logged out"
}
```

---

## Quick Test Script

Run the automated test script:
```bash
cd /home/simonjuma/Desktop/projects_254/DT/apps/backend
./test_superadmin.sh
```

This will test:
1. ✅ Regional Superadmin Creation (CENTRAL)
2. ✅ Sub-Regional Superadmin Creation (NYERI)
3. ✅ Superadmin Login
4. ✅ List Accessible Altars
5. ✅ Logout & Token Blacklisting
6. ✅ Regular Admin Signup
7. ✅ Regular Admin Login

---

## User Roles Summary

| Role | Description | Admin Scope | Can See |
|------|-------------|-------------|---------|
| **Regional Superadmin** | Manages entire region | `CENTRAL` | All 8 altars in Central Region |
| **Sub-Regional Superadmin** | Manages sub-region | `NYERI`, `MWEIGA`, etc. | Altars in their sub-region only |
| **Altar Admin** | Manages single altar | None | Only their own altar's members |

---

## Demo Users (From Seed)

Already created by `seed_central_region` command:

1. **Regional Superadmin:**
   - Email: `central@example.com`
   - Password: `admin123`
   - Scope: CENTRAL (sees all 8 altars)

2. **Sub-Regional Superadmin:**
   - Email: `nyeri@example.com`
   - Password: `admin123`
   - Scope: NYERI (sees 2 Nyeri altars)

Test login:
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "central@example.com",
    "password": "admin123"
  }'
```
