import axios from 'axios';
import { getAuthToken, clearAuthData } from './auth';

// Read the base URL from environment variables.
// Fallback to localhost for local development.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  // Construct the full API URL
  baseURL: `${API_BASE_URL}/api/`,
});

// Automatically attach token
api.interceptors.request.use(
  (config) => {
    const token = getAuthToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle authentication errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth data and redirect to login
      clearAuthData()
      
      // Redirect to login if we're in a browser environment
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error);
  }
);

export default api;
