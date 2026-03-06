# Super Admin "Global Pipe" Architecture

## 🌍 Overview

The Digital Transformation platform implements a **hierarchical Super Admin system** that provides 3 authorized administrators with a **master nationwide view** of all data, while regular altar secretaries only see their local members.

## 🏗️ Architecture Components

### 1. The "Global Pipe" - Master Data View

Super Admins see ALL data across the entire organization through the Django Admin interface (`/admin/`):

- **All Members** from every altar nationwide
- **All Altars** organized by region/sub-region  
- **All Attendance Records** with regional filtering
- **All Organizational Nodes** (Continents → Countries → Regions → Sub-Regions)
- **Aggregated Statistics** across the entire nation

### 2. Regional Categorization

Data is automatically categorized and filterable by:

```
📊 Hierarchical Structure:
    └─ Continent (e.g., Africa)
        └─ Country (e.g., Kenya)
            └─ Region (e.g., Central)
                └─ Sub-Region (e.g., Nyeri)
                    └─ Altar (e.g., Nyeri Main Altar)
                        └─ Members (Individual church members)
```

### 3. Three-Tier Access Model

| Role | Access Level | View Scope | Interface |
|------|-------------|-----------|-----------|
| **Super Admin** | Full nationwide access | All regions, all altars, all members | Django Admin `/admin/` |
| **Regional Admin** | Regional scope | All altars in their region via OrganizationNode | React Dashboard `/admin` |
| **Altar Secretary** | Altar-level | Only their own altar's members | React Dashboard `/admin` |

## 🔐 Security & Access Control

### Hardcoded Super Admin List

Only **3 specific email addresses** can access the Django Admin:

```python
# Located in: core/admin.py, core/middleware.py, core/management/commands/setup_superadmins.py
ALLOWED_SUPERADMIN_EMAILS = [
    "superadmin1@example.com",  # Replace with actual email
    "superadmin2@example.com",  # Replace with actual email
    "superadmin3@example.com",  # Replace with actual email
]
```

### Multi-Layer Security

1. **Middleware Protection** (`SuperAdminAccessMiddleware`)
   - Intercepts all `/admin/` requests
   - Checks user email against allowed list
   - Returns 403 Forbidden for unauthorized users
   - Works even before Django Admin loads

2. **ModelAdmin Mixin** (`SuperAdminAccessMixin`)
   - Applied to every admin class
   - Controls view, add, change, delete permissions
   - Double-checks authorization at model level

3. **No Staff Access Flag**
   - Regular users have `is_staff=False`
   - Even if someone sets `is_staff=True`, middleware blocks them
   - Only hardcoded emails can proceed

### Access Flow Diagram

```
User tries to access /admin/
        ↓
SuperAdminAccessMiddleware checks email
        ↓
    ┌── Email in ALLOWED_SUPERADMIN_EMAILS? ───┐
    │                                           │
   YES                                          NO
    │                                           │
    ↓                                           ↓
Allow access                            403 Forbidden
    ↓                                   (Pretty error page)
SuperAdminAccessMixin
double-checks permissions
    ↓
Grant full CRUD access to all models
```

## 🛠️ Setup Instructions

### Step 1: Update Super Admin Emails

**Replace the placeholder emails** in these 3 files with actual email addresses:

1. `apps/backend/core/admin.py` → Line 15-19
2. `apps/backend/core/middleware.py` → Line 9-13
3. `apps/backend/core/management/commands/setup_superadmins.py` → Line 16-20

```python
ALLOWED_SUPERADMIN_EMAILS = [
    "john.doe@diocese.org",
    "jane.smith@diocese.org",
    "admin@diocese.org",
]
```

### Step 2: Create Super Admin Accounts

Run the management command to create the 3 accounts:

```bash
cd apps/backend
python manage.py setup_superadmins
```

**Output:**
```
======================================================================
SUPER ADMIN SETUP
======================================================================

✅ Created: john.doe@diocese.org
   Username: john.doe
   Password: SuperAdmin2026!#1
   ⚠️  IMPORTANT: Change this password immediately after first login!

✅ Created: jane.smith@diocese.org
   Username: jane.smith
   Password: SuperAdmin2026!#2
   ⚠️  IMPORTANT: Change this password immediately after first login!

✅ Created: admin@diocese.org
   Username: admin
   Password: SuperAdmin2026!#3
   ⚠️  IMPORTANT: Change this password immediately after first login!

======================================================================
SUMMARY
======================================================================
✅ Created: 3
🔄 Updated: 0
⏭️  Skipped: 0
📊 Total authorized: 3

⚠️  SECURITY REMINDER:
All new accounts have default passwords shown above.
These MUST be changed immediately after first login!

✅ Super Admin setup completed successfully!
```

### Step 3: Test Access

1. **Log in as Super Admin:**
   - Go to: `http://your-domain.com/admin/`
   - Use email and default password
   - **Immediately change the password!**

2. **Verify regional filtering:**
   - Click "Members"
   - Use filters on the right: "Home altar parent node" (Region)
   - Search by name, phone, altar name

3. **Test blocked access:**
   - Try logging in with a non-authorized email
   - Should see pretty 403 Forbidden error page

## 📊 Master View Features

### Member Admin - The Global Pipe

**Location:** Django Admin → Members

**Features:**
- ✅ Filter by **Region/Sub-Region** (dropdown on right sidebar)
- ✅ Filter by **Specific Altar**
- ✅ Filter by **Status** (Active/Inactive)
- ✅ Filter by **Gender**
- ✅ Filter by **Membership Date**
- ✅ **Global Search** - Find any member by:
  - Name
  - Phone number
  - Email
  - Altar name
  - Region name

**Visual Indicators:**
- 👨/👩 Gender icons
- ● Green = Active, ○ Red = Inactive
- Region displayed next to altar name
- Attendance summary for each member

### Altar Admin - Regional Organization

**Location:** Django Admin → Altars

**Features:**
- ✅ Filter by **Parent Node** (Region/Sub-Region)
- ✅ Filter by **City**
- ✅ Filter by **Status**
- ✅ Search by altar name, code, city, region

**Display:**
- Shows which region/sub-region each altar belongs to
- Member count per altar
- Pastor assignment
- Geographic coordinates

### Attendance Log Admin - Service Analytics

**Location:** Django Admin → Attendance logs

**Features:**
- ✅ Filter by **Service Type** (Sunday, Midweek, Special, etc.)
- ✅ Filter by **Date** (date hierarchy at top)
- ✅ Filter by **Region** via altar
- ✅ Search by attendee name, altar name

### Organization Node Admin - Hierarchy Management

**Location:** Django Admin → Organization nodes

**Features:**
- Visual depth indicators showing tree structure
- Cached statistics (total_altars, total_members)
- Path-based querying for efficient tree traversal
- Leader assignment

## 🚀 Deployment

### Include in Migration Script

Add this to your deployment workflow (after database migrations):

```bash
echo "Setting up Super Admin accounts..."
python manage.py setup_superadmins --skip-existing

echo "✅ Super Admin setup complete"
```

### AWS RDS Deployment

The super admin accounts are created directly in your RDS database:

```yaml
# In .github/workflows/infrastructure-and-deploy.yml
# After "Run Database Migrations" step:

- name: Setup Super Admin Accounts
  run: |
    docker exec backend python manage.py setup_superadmins --skip-existing
    echo "✅ Super Admin accounts ready"
```

## 🔧 Customization

### Adding More Super Admins

If you need to add a 4th or 5th super admin:

1. Update `ALLOWED_SUPERADMIN_EMAILS` in all 3 files
2. Add to `DEFAULT_PASSWORDS` dict in `setup_superadmins.py`
3. Run `python manage.py setup_superadmins`

### Custom Filters

To add more filtering options, edit `core/admin.py`:

```python
@admin.register(Member)
class MemberAdmin(SuperAdminAccessMixin, admin.ModelAdmin):
    list_filter = [
        "is_active",
        "home_altar__parent_node",  # Existing
        "home_altar",  # Existing
        "gender",  # Existing
        "membership_date",  # Existing
        "date_of_birth",  # ADD NEW FILTER
    ]
```

## 📈 Statistics & Reporting

The admin interface provides real-time statistics:

- **Total Members** (across all altars)
- **Members by Region** (use filters)
- **Attendance Trends** (date hierarchy)
- **Altar Growth** (member_count field)
- **Transfer History** (between altars and regions)

## 🛡️ Security Best Practices

1. **Change Default Passwords** - Immediately after first login
2. **Use Strong Passwords** - Minimum 12 characters, mixed case, numbers, symbols
3. **Enable 2FA** (if available in Django)
4. **Monitor Access Logs** - Check who's logging into admin
5. **Regular Audits** - Review super admin list quarterly
6. **Principle of Least Privilege** - Only 3 accounts should have this access

## 🆘 Troubleshooting

### "Access Denied" when trying to access /admin/

**Cause:** Your email is not in `ALLOWED_SUPERADMIN_EMAILS`

**Solution:**
1. Verify your account email matches exactly (case-sensitive)
2. Check all 3 files have the same list
3. Restart Django server after changes

### Super Admin can't see any data

**Cause:** Permissions not set correctly

**Solution:**
```bash
python manage.py setup_superadmins  # Re-run setup (will update existing)
```

### Middleware blocking login page

**Check:** Middleware should allow `/admin/login/` and `/admin/logout/` paths

## 📞 Support

For issues:
1. Check Django logs: `docker logs backend`
2. Verify database: `python manage.py shell` → `User.objects.filter(is_superuser=True)`
3. Test middleware: Try accessing `/admin/` with different accounts

---

**Last Updated:** March 2026  
**Version:** 1.0.0  
**Maintained by:** Digital Transformation Team
