import apiClient from './client';
import apiConfig from './config';

/**
 * API Service Layer
 * Centralized service for all API endpoints
 */

// ==================== Authentication Services ====================
export const authService = {
  /**
   * Login user with email/phone and password
   * @param {string} email_or_phone - Email or phone number
   * @param {string} password - User password
   */
  login: async (email_or_phone, password) => {
    return await apiClient.post(apiConfig.endpoints.auth.login, {
      email_or_phone,
      password,
    });
  },

  /**
   * Register new regular admin user
   * @param {Object} userData - User registration data
   */
  register: async (userData) => {
    return await apiClient.post(apiConfig.endpoints.auth.register, userData);
  },

  /**
   * Logout user and blacklist refresh token
   * @param {string} refreshToken - Refresh token to blacklist
   */
  logout: async (refreshToken) => {
    return await apiClient.post(apiConfig.endpoints.auth.logout, {
      refresh_token: refreshToken,
    });
  },

  /**
   * Refresh access token
   * @param {string} refreshToken - Refresh token
   */
  refreshToken: async (refreshToken) => {
    return await apiClient.post(apiConfig.endpoints.auth.refresh, {
      refresh: refreshToken,
    });
  },

  /**
   * Verify token validity
   * @param {string} token - Token to verify
   */
  verifyToken: async (token) => {
    return await apiClient.post(apiConfig.endpoints.auth.verify, {
      token,
    });
  },

  /**
   * Get current user info from token
   */
  getCurrentUser: () => {
    const token = localStorage.getItem('access_token');
    const userStr = localStorage.getItem('user');
    if (token && userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  },
};

// ==================== Superadmin Services ====================
export const superadminService = {
  /**
   * Create new superadmin (regional or sub-regional)
   * @param {Object} adminData - Superadmin data
   */
  create: async (adminData) => {
    return await apiClient.post(apiConfig.endpoints.superadmin.create, adminData);
  },

  /**
   * List all superadmins
   */
  list: async () => {
    return await apiClient.get(apiConfig.endpoints.superadmin.list);
  },

  /**
   * Get superadmin details
   * @param {number} id - Superadmin ID
   */
  getDetail: async (id) => {
    return await apiClient.get(apiConfig.endpoints.superadmin.detail(id));
  },
};

// ==================== Member Services ====================
export const memberService = {
  /**
   * List all members (filtered by user's scope)
   * @param {Object} params - Query parameters
   */
  list: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString 
      ? `${apiConfig.endpoints.members.list}?${queryString}` 
      : apiConfig.endpoints.members.list;
    return await apiClient.get(endpoint);
  },

  /**
   * Get member details
   * @param {number} id - Member ID
   */
  getDetail: async (id) => {
    return await apiClient.get(apiConfig.endpoints.members.detail(id));
  },

  /**
   * Create new member
   * @param {Object} memberData - Member data
   */
  create: async (memberData) => {
    return await apiClient.post(apiConfig.endpoints.members.create, memberData);
  },

  /**
   * Update member
   * @param {number} id - Member ID
   * @param {Object} memberData - Updated member data
   */
  update: async (id, memberData) => {
    return await apiClient.put(apiConfig.endpoints.members.update(id), memberData);
  },

  /**
   * Partially update member
   * @param {number} id - Member ID
   * @param {Object} memberData - Partial member data
   */
  partialUpdate: async (id, memberData) => {
    return await apiClient.patch(apiConfig.endpoints.members.update(id), memberData);
  },

  /**
   * Delete member
   * @param {number} id - Member ID
   */
  delete: async (id) => {
    return await apiClient.delete(apiConfig.endpoints.members.delete(id));
  },

  /**
   * Transfer member to another altar or offboard
   * @param {Object} transferData - Transfer data (member_id, to_altar_id, reason, notes)
   */
  transfer: async (transferData) => {
    return await apiClient.post(apiConfig.endpoints.members.transfer, transferData);
  },
};

// ==================== Guest Services ====================
export const guestService = {
  /**
   * Register new guest/visitor
   * @param {Object} guestData - Guest data
   */
  create: async (guestData) => {
    return await apiClient.post(apiConfig.endpoints.guests.create, guestData);
  },
};

// ==================== Altar Services ====================
export const altarService = {
  /**
   * List all altars (filtered by user's scope)
   * @param {Object} params - Query parameters
   */
  list: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString 
      ? `${apiConfig.endpoints.altars.list}?${queryString}` 
      : apiConfig.endpoints.altars.list;
    return await apiClient.get(endpoint);
  },

  /**
   * Get altar details
   * @param {number} id - Altar ID
   */
  getDetail: async (id) => {
    return await apiClient.get(apiConfig.endpoints.altars.detail(id));
  },

  /**
   * Create new altar
   * @param {Object} altarData - Altar data
   */
  create: async (altarData) => {
    return await apiClient.post(apiConfig.endpoints.altars.create, altarData);
  },

  /**
   * Update altar
   * @param {number} id - Altar ID
   * @param {Object} altarData - Updated altar data
   */
  update: async (id, altarData) => {
    return await apiClient.put(apiConfig.endpoints.altars.update(id), altarData);
  },

  /**
   * Delete altar
   * @param {number} id - Altar ID
   */
  delete: async (id) => {
    return await apiClient.delete(apiConfig.endpoints.altars.delete(id));
  },
};

// ==================== Department Services ====================
export const departmentService = {
  /**
   * List all departments
   * @param {Object} params - Query parameters
   */
  list: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString 
      ? `${apiConfig.endpoints.departments.list}?${queryString}` 
      : apiConfig.endpoints.departments.list;
    return await apiClient.get(endpoint);
  },

  /**
   * Get department details
   * @param {number} id - Department ID
   */
  getDetail: async (id) => {
    return await apiClient.get(apiConfig.endpoints.departments.detail(id));
  },

  /**
   * Create new department
   * @param {Object} departmentData - Department data
   */
  create: async (departmentData) => {
    return await apiClient.post(apiConfig.endpoints.departments.create, departmentData);
  },

  /**
   * Update department
   * @param {number} id - Department ID
   * @param {Object} departmentData - Updated department data
   */
  update: async (id, departmentData) => {
    return await apiClient.put(apiConfig.endpoints.departments.update(id), departmentData);
  },

  /**
   * Delete department
   * @param {number} id - Department ID
   */
  delete: async (id) => {
    return await apiClient.delete(apiConfig.endpoints.departments.delete(id));
  },
};

// ==================== Attendance Services ====================
export const attendanceService = {
  /**
   * List attendance records
   * @param {Object} params - Query parameters (date, altar, etc.)
   */
  list: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString 
      ? `${apiConfig.endpoints.attendance.list}?${queryString}` 
      : apiConfig.endpoints.attendance.list;
    return await apiClient.get(endpoint);
  },

  /**
   * Get attendance record details
   * @param {number} id - Attendance record ID
   */
  getDetail: async (id) => {
    return await apiClient.get(apiConfig.endpoints.attendance.detail(id));
  },

  /**
   * Create attendance record
   * @param {Object} attendanceData - Attendance data
   */
  create: async (attendanceData) => {
    return await apiClient.post(apiConfig.endpoints.attendance.create, attendanceData);
  },

  /**
   * Mark attendance for member
   * @param {Object} attendanceData - Attendance marking data
   */
  markAttendance: async (attendanceData) => {
    return await apiClient.post(apiConfig.endpoints.attendance.markAttendance, attendanceData);
  },

  /**
   * Get attendance report
   * @param {Object} params - Report parameters (date range, altar, etc.)
   */
  getReport: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString 
      ? `${apiConfig.endpoints.attendance.report}?${queryString}` 
      : apiConfig.endpoints.attendance.report;
    return await apiClient.get(endpoint);
  },
};

// ==================== Dashboard Services ====================
export const dashboardService = {
  /**
   * Get dashboard statistics
   */
  getStats: async () => {
    return await apiClient.get(apiConfig.endpoints.dashboard.stats);
  },

  /**
   * Get dashboard analytics
   * @param {Object} params - Analytics parameters
   */
  getAnalytics: async (params = {}) => {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString 
      ? `${apiConfig.endpoints.dashboard.analytics}?${queryString}` 
      : apiConfig.endpoints.dashboard.analytics;
    return await apiClient.get(endpoint);
  },
};

// Export all services as a single object
export default {
  auth: authService,
  superadmin: superadminService,
  members: memberService,
  guests: guestService,
  altars: altarService,
  departments: departmentService,
  attendance: attendanceService,
  dashboard: dashboardService,
};
