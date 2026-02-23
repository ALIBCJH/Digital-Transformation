const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api';

const apiConfig = {
  baseURL: API_BASE_URL,
  endpoints: {
    // Authentication endpoints
    auth: {
      login: '/login/',
      register: '/register/',
      logout: '/logout/',
      refresh: '/token/refresh/',
      verify: '/token/verify/',
    },
    // Superadmin endpoints  
    superadmin: {
      create: '/api/superadmin/create/',
      list: '/api/superadmin/',
      detail: (id) => `/api/superadmin/${id}/`,
    },
    // Superadmin endpoints
    superadmin: {
      create: '/api/superadmin/create/',
      list: '/api/superadmin/',
      detail: (id) => `/api/superadmin/${id}/`,
    },
    // Members endpoints
    members: {
      list: '/members/list/',
      detail: (id) => `/members/${id}/`,
      create: '/members/create/',
      update: (id) => `/members/${id}/`,
      delete: (id) => `/members/${id}/`,
      transfer: '/members/transfer/',
    },
    // Guest endpoints (using members/create for now since guests endpoint disabled)
    guests: {
      create: '/members/create/', // Using members endpoint since guests is disabled
    },
    // Altars endpoints
    altars: {
      list: '/altars/',
      detail: (id) => `/altars/${id}/`,
      create: '/altars/',
      update: (id) => `/altars/${id}/`,
      delete: (id) => `/altars/${id}/`,
    },
    // Departments endpoints
    departments: {
      list: '/departments/',
      detail: (id) => `/departments/${id}/`,
      create: '/departments/',
      update: (id) => `/departments/${id}/`,
      delete: (id) => `/departments/${id}/`,
    },
    // Attendance endpoints  
    attendance: {
      list: '/api/attendance/',
      detail: (id) => `/api/attendance/${id}/`,
      create: '/api/attendance/',
      markAttendance: '/api/attendance/mark/',
      report: '/api/attendance/report/',
      members: '/api/attendance/members/',
      record: '/api/attendance/record/',
    },
    // Dashboard endpoints
    dashboard: {
      stats: '/api/dashboard/stats/',
      analytics: '/api/dashboard/analytics/',
      superadmin: '/api/dashboard/superadmin/',
      regional: '/api/dashboard/regional/',
      altar: '/api/dashboard/altar/',
    },
  },
  headers: {
    'Content-Type': 'application/json',
  },
};

export default apiConfig;
