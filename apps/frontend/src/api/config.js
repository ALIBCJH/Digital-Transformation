const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const apiConfig = {
  baseURL: API_BASE_URL,
  endpoints: {
    auth: {
      login: '/auth/login/',
      signup: '/auth/signup/',
      logout: '/auth/logout/',
      refresh: '/auth/token/refresh/',
      verify: '/auth/token/verify/',
    },
    members: {
      list: '/members/',
      detail: (id) => `/members/${id}/`,
      create: '/members/',
      update: (id) => `/members/${id}/`,
      delete: (id) => `/members/${id}/`,
    },
    altars: {
      list: '/altars/',
      detail: (id) => `/altars/${id}/`,
    },
    departments: {
      list: '/departments/',
      detail: (id) => `/departments/${id}/`,
    },
  },
  headers: {
    'Content-Type': 'application/json',
  },
};

export default apiConfig;
