import apiConfig from './config';

class ApiClient {
  constructor() {
    this.baseURL = apiConfig.baseURL;
  }

  getAuthToken() {
    return localStorage.getItem('access_token');
  }

  setAuthToken(token) {
    localStorage.setItem('access_token', token);
  }

  removeAuthToken() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const token = this.getAuthToken();

    const headers = {
      ...apiConfig.headers,
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired, try to refresh
          const refreshed = await this.refreshToken();
          if (refreshed) {
            // Retry the original request
            headers['Authorization'] = `Bearer ${this.getAuthToken()}`;
            const retryResponse = await fetch(url, { ...config, headers });
            return await this.handleResponse(retryResponse);
          } else {
            this.removeAuthToken();
            // Only redirect to login if we're not already on login/signup pages
            const currentPath = window.location.pathname;
            if (currentPath !== '/login' && currentPath !== '/signup') {
              window.location.href = '/login';
            }
            throw new Error('Session expired. Please login again.');
          }
        }
        const error = await response.json();
        console.error('API Error Response:', error);
        // Handle different error response formats
        let errorMessage;
        if (error.non_field_errors) {
          errorMessage = error.non_field_errors[0] || error.non_field_errors.join(', ');
        } else if (error.detail) {
          errorMessage = error.detail;
        } else if (error.message) {
          errorMessage = error.message;
        } else if (error.error) {
          errorMessage = error.error;
        } else {
          // Handle field-specific errors
          const firstError = Object.values(error)[0];
          errorMessage = Array.isArray(firstError) ? firstError[0] : JSON.stringify(error);
        }
        throw new Error(errorMessage);
      }

      return await this.handleResponse(response);
    } catch (error) {
      console.error('API Request Error:', error);
      throw error;
    }
  }

  async handleResponse(response) {
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    return await response.text();
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${this.baseURL}${apiConfig.endpoints.auth.refresh}`, {
        method: 'POST',
        headers: apiConfig.headers,
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        this.setAuthToken(data.access);
        return true;
      }
      return false;
    } catch (error) {
      console.error('Token refresh error:', error);
      return false;
    }
  }

  // Auth methods
  async login(credentials) {
    const response = await this.request(apiConfig.endpoints.auth.login, {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    if (response.access) {
      this.setAuthToken(response.access);
      localStorage.setItem('refresh_token', response.refresh);
    }

    return response;
  }

  async signup(userData) {
    const response = await this.request(apiConfig.endpoints.auth.signup, {
      method: 'POST',
      body: JSON.stringify(userData),
    });

    if (response.access) {
      this.setAuthToken(response.access);
      localStorage.setItem('refresh_token', response.refresh);
    }

    return response;
  }

  async logout() {
    this.removeAuthToken();
    return true;
  }

  // Generic CRUD methods
  async get(endpoint) {
    return await this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint, data) {
    return await this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data) {
    return await this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async patch(endpoint, data) {
    return await this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return await this.request(endpoint, { method: 'DELETE' });
  }
}

export default new ApiClient();
