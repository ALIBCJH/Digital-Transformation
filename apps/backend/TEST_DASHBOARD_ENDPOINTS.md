# Dashboard & Reports Endpoints Testing Guide

## 📊 **Regional Dashboard** (For Regional Superadmins)

### Endpoint
```
GET http://localhost:8000/api/dashboard/regional/
Authorization: Bearer <access_token>
```

### Who can access?
- **Regional Superadmin** (e.g., Senior Deputy Archbishop of Central Region)
- **Global Superadmin** (can see all regions)

### What it returns?
Shows aggregated metrics for ALL sub-regions and altars under your scope:
- Total sub-regions
- Total altars
- Total members (congregants)
- Gender breakdown (male/female)
- TODO: Total guests, attendance stats

### Example Response (Central Region Admin):
```json
{
  "scope": "Central Region",
  "report_date": "2026-02-18",
  "regions": [
    {
      "region": {
        "name": "Central Region",
        "code": "CENTRAL",
        "leader": "Not Assigned"
      },
      "summary": {
        "total_sub_regions": 6,
        "total_altars": 7,
        "total_members": 0,
        "male_members": 0,
        "female_members": 0,
        "total_guests": 0,
        "total_present_today": 0,
        "total_absent_today": 0
      },
      "sub_regions": [
        {
          "name": "Nyeri Sub-Region",
          "code": "NYERI",
          "total_altars": 2,
          "total_members": 0,
          "altars": [
            {
              "name": "St. Mary's Nyeri",
              "city": "Nyeri",
              "member_count": 0
            },
            {
              "name": "St. Joseph's Nyeri",
              "city": "Nyeri",
              "member_count": 0
            }
          ]
        },
        {
          "name": "Mweiga Sub-Region",
          "code": "MWEIGA",
          "total_altars": 1,
          "total_members": 0,
          "altars": [
            {
              "name": "Holy Family Mweiga",
              "city": "Mweiga",
              "member_count": 0
            }
          ]
        },
        ... (5 more sub-regions)
      ]
    }
  ]
}
```

---

## 🏛️ **Altar Dashboard** (For Altar Admins)

### Endpoint
```
GET http://localhost:8000/api/dashboard/altar/
Authorization: Bearer <access_token>

# Or specify altar name
GET http://localhost:8000/api/dashboard/altar/?altar=St. Mary's Nyeri
```

### Who can access?
- **Altar Admins** (see their altar only)
- **Regional Superadmins** (can specify any altar in their region)
- **Global Superadmins** (can see any altar)

### What it returns?
Shows detailed metrics for ONE specific altar:
- Total members
- Gender breakdown
- Department breakdown
- Recent members
- TODO: Guest count, attendance stats

### Example Response:
```json
{
  "altar": {
    "name": "St. Mary's Nyeri",
    "code": "NYERI_STMARY",
    "city": "Nyeri",
    "pastor": "Not Assigned",
    "parent_region": "Nyeri Sub-Region"
  },
  "summary": {
    "total_members": 15,
    "male_members": 7,
    "female_members": 8,
    "total_guests": 0,
    "present_today": 0,
    "absent_today": 0,
    "attendance_rate": 0.0
  },
  "departments": [
    { "serving_department": "Choir", "count": 5 },
    { "serving_department": "Ushering", "count": 3 },
    { "serving_department": "Sunday School", "count": 2 }
  ],
  "recent_members": [
    {
      "id": 1,
      "full_name": "Jane Wanjiku",
      "phone_number": "+254712345678",
      "gender": "F",
      "serving_department": "Choir",
      "membership_date": "2026-01-15"
    },
    ... (up to 10 recent members)
  ]
}
```

---

## 🧪 **Quick Test with cURL**

### 1. Login as Regional Admin (Central Region)
```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_phone": "central@example.com",
    "password": "admin123"
  }'
```

**Save the `access` token from response**

### 2. View Regional Dashboard
```bash
curl -X GET http://localhost:8000/api/dashboard/regional/ \
  -H "Authorization: Bearer <paste_access_token_here>"
```

### 3. View Specific Altar Dashboard
```bash
curl -X GET "http://localhost:8000/api/dashboard/altar/?altar=St.%20Mary's%20Nyeri" \
  -H "Authorization: Bearer <paste_access_token_here>"
```

---

## 📋 **Summary of Metrics**

### Regional Dashboard Shows:
- ✅ Total sub-regions (e.g., Nyeri, Mweiga, Karatina, etc.)
- ✅ Total altars across region
- ✅ Total members (congregants)
- ✅ Gender breakdown
- ✅ Per-sub-region breakdown with altar details
- ⏳ Total guests (TODO: after Guest model)
- ⏳ Attendance stats (TODO: after AttendanceLog model)

### Altar Dashboard Shows:
- ✅ Total members for specific altar
- ✅ Gender breakdown
- ✅ Department distribution
- ✅ Recent members list
- ⏳ Guest count (TODO)
- ⏳ Today's attendance (TODO)
- ⏳ Attendance rate (TODO)

---

## 🔑 **Demo Credentials**

**Regional Admin (Central Region):**
- Email: `central@example.com`
- Password: `admin123`
- Can see: ALL 6 sub-regions + 7 altars

**Sub-Regional Admin (Nyeri):**
- Email: `nyeri@example.com`
- Password: `admin123`
- Can see: Only Nyeri sub-region (2 altars)

---

## 🎯 **Next Steps**

To complete the dashboard with full metrics, we need to implement:
1. **Guest model** - Track visitors
2. **AttendanceLog model** - Track who attended each service
3. **Attendance marking endpoint** - For altar admins to mark attendance
4. Then update dashboard to show:
   - `total_guests`
   - `total_present_today`
   - `total_absent_today`
   - `attendance_rate`

Would you like me to implement these now?
