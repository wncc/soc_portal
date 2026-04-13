// src/utils/api.js
import axios from 'axios';
import { clearAuthData, isTokenValid } from './auth';

const api = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL,
  withCredentials: true,
});

// Add request interceptor to include token from localStorage
api.interceptors.request.use(
  (config) => {
    // Don't add token for SSO login endpoints
    const ssoEndpoints = ['/accounts/get-sso-user/', '/accounts/register_sso/', '/accounts/token_sso/'];
    const isSSO = ssoEndpoints.some(endpoint => config.url?.includes(endpoint));
    
    if (!isSSO) {
      const token = localStorage.getItem('authToken');
      if (token) {
        // Validate token format before using it
        if (!isTokenValid(token)) {
          console.log('[API] Invalid token format detected - clearing auth data');
          clearAuthData();
          // Reject the request and redirect to login
          if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login';
          }
          return Promise.reject(new Error('Invalid token format'));
        }
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// Add response interceptor to handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token is invalid or expired - clear all auth data
      console.log('[API] 401 Unauthorized - clearing auth data');
      clearAuthData();
      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/loading')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  },
);

export default api;
