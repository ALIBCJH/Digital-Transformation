# API Services Documentation

This directory contains the centralized API configuration and service layer for the Digital Transformation frontend application.

## File Structure

```
src/api/
├── config.js       # API endpoint configuration
├── client.js       # HTTP client with authentication
├── services.js     # Service layer for all API endpoints
└── index.js        # Main exports
```

## Configuration

### Environment Variables

Create a `.env` file in the frontend root directory:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

### API Config (`config.js`)

All API endpoints are defined in a centralized configuration object. This prevents code duplication and makes endpoint management easier.

## Services

### Authentication Service (`authService`)

Handles user authentication and session management.

```javascript
import { authService } from '../api/services';

// Login
const response = await authService.login('user@example.com', 'password123');
// Response: { access, refresh, user }

// Register new admin
const user = await authService.register({
  first_name: 'John',
  last_name: 'Doe',
  email_or_phone: 'john@example.com',
  altar: "St. Mary's Church",
  password: 'SecurePass123!',
  password2: 'SecurePass123!'
});

// Logout
await authService.logout(refreshToken);

// Get current user
const currentUser = authService.getCurrentUser();
```

### Superadmin Service (`superadminService`)

Manages superadmin users (regional and sub-regional).

```javascript
import { superadminService } from '../api/services';

// Create superadmin
const admin = await superadminService.create({
  first_name: 'Jane',
  last_name: 'Smith',
  email: 'jane@central.com',
  phone_number: '+254700123456',
  password: 'SecurePass123!',
  password2: 'SecurePass123!',
  admin_scope: 'CENTRAL' // or sub-region like 'NYERI'
});

// List superadmins
const admins = await superadminService.list();

// Get superadmin details
const admin = await superadminService.getDetail(adminId);
```

### Member Service (`memberService`)

Manage church members.

```javascript
import { memberService } from '../api/services';

// List members
const members = await memberService.list();

// List with filters
const filteredMembers = await memberService.list({
  altar: 'altar_id',
  status: 'active'
});

// Get member details
const member = await memberService.getDetail(memberId);

// Create member
const newMember = await memberService.create({
  first_name: 'John',
  last_name: 'Doe',
  email: 'john@example.com',
  phone_number: '+254700123456',
  altar: altarId,
  // ... other fields
});

// Update member
const updated = await memberService.update(memberId, {
  // updated fields
});

// Partial update
const patched = await memberService.partialUpdate(memberId, {
  status: 'inactive'
});

// Delete member
await memberService.delete(memberId);
```

### Altar Service (`altarService`)

Manage altars (churches/locations).

```javascript
import { altarService } from '../api/services';

// List altars
const altars = await altarService.list();

// Get altar details
const altar = await altarService.getDetail(altarId);

// Create altar
const newAltar = await altarService.create({
  name: "St. Mary's Church",
  sub_region: subRegionId,
  // ... other fields
});

// Update altar
await altarService.update(altarId, updatedData);

// Delete altar
await altarService.delete(altarId);
```

### Department Service (`departmentService`)

Manage church departments.

```javascript
import { departmentService } from '../api/services';

// List departments
const departments = await departmentService.list();

// Get department details
const dept = await departmentService.getDetail(deptId);

// Create, update, delete similar to altarService
```

### Attendance Service (`attendanceService`)

Track member attendance.

```javascript
import { attendanceService } from '../api/services';

// List attendance records
const records = await attendanceService.list({
  date: '2026-02-19',
  altar: altarId
});

// Get attendance details
const record = await attendanceService.getDetail(recordId);

// Create attendance record
await attendanceService.create({
  member: memberId,
  date: '2026-02-19',
  status: 'present',
  // ... other fields
});

// Mark attendance
await attendanceService.markAttendance({
  member_id: memberId,
  status: 'present'
});

// Get attendance report
const report = await attendanceService.getReport({
  start_date: '2026-02-01',
  end_date: '2026-02-28',
  altar: altarId
});
```

### Dashboard Service (`dashboardService`)

Get dashboard statistics and analytics.

```javascript
import { dashboardService } from '../api/services';

// Get dashboard stats
const stats = await dashboardService.getStats();

// Get analytics
const analytics = await dashboardService.getAnalytics({
  period: 'month',
  year: 2026
});
```

## Using Services in Components

### Example: Login Component

```javascript
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../api/services';

function Login() {
  const [credentials, setCredentials] = useState({
    email_or_phone: '',
    password: ''
  });
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await authService.login(
        credentials.email_or_phone,
        credentials.password
      );
      
      // Tokens are automatically stored by the service
      localStorage.setItem('user', JSON.stringify(response.user));
      
      navigate('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      {/* form fields */}
    </form>
  );
}
```

### Example: Member List Component

```javascript
import { useEffect, useState } from 'react';
import { memberService } from '../api/services';

function MemberList() {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMembers();
  }, []);

  const loadMembers = async () => {
    try {
      const data = await memberService.list();
      setMembers(data.results || data);
    } catch (error) {
      console.error('Failed to load members:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {loading ? 'Loading...' : members.map(member => (
        <div key={member.id}>
          {member.first_name} {member.last_name}
        </div>
      ))}
    </div>
  );
}
```

## Authentication Flow

The API client automatically handles:

1. **Token Management**: Access tokens are stored in localStorage
2. **Auto-refresh**: Expired tokens are automatically refreshed
3. **Error Handling**: 401 errors trigger token refresh or redirect to login
4. **Authorization Headers**: Bearer tokens are automatically added to requests

## Error Handling

All services throw errors that should be caught in components:

```javascript
try {
  await memberService.create(memberData);
} catch (error) {
  // error.message contains the error description
  console.error('Error:', error.message);
}
```

## Best Practices

1. **Import only what you need**:
   ```javascript
   import { authService, memberService } from '../api/services';
   ```

2. **Handle loading states**:
   ```javascript
   const [loading, setLoading] = useState(false);
   
   setLoading(true);
   try {
     await service.method();
   } finally {
     setLoading(false);
   }
   ```

3. **Handle errors gracefully**:
   ```javascript
   try {
     await service.method();
   } catch (error) {
     setError(error.message);
   }
   ```

4. **Use environment variables** for API URLs:
   ```javascript
   // In .env
   VITE_API_BASE_URL=https://api.production.com
   ```

## Migration from Mock Data

The following changes were made to migrate from mock data:

1. ✅ Removed `mockAuth.js` - All mock authentication removed
2. ✅ Updated `Login.jsx` - Now uses `authService.login()`
3. ✅ Updated `Signup.jsx` - Now uses `authService.register()`
4. ✅ Updated `Dashboard.jsx` - Uses `authService.getCurrentUser()`
5. ✅ Updated `AdminDashboard.jsx` - Uses `memberService.list()`
6. ✅ Added comprehensive service layer in `services.js`
7. ✅ Updated `config.js` with all Django backend endpoints

## Next Steps

To fully integrate with the backend:

1. Ensure Django backend is running on `http://127.0.0.1:8000`
2. Create a `.env` file based on `.env.example`
3. Test authentication flows (login, register, logout)
4. Implement forms for creating/updating members, altars, etc.
5. Add attendance marking functionality
6. Implement dashboard statistics display

## Support

For issues or questions about the API services, please check:
- Backend API documentation in `/apps/backend/README.md`
- API testing guide in `/apps/backend/API_TESTING.md`
- Test scripts in `/apps/backend/test_*.sh`
