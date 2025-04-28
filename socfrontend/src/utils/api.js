// src/utils/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://socb.tech-iitb.org/',
  // withCredentials: true,  // This is crucial for sending cookies
  // headers: {
  //   'Content-Type': 'application/json',
  // }
});

// Add request interceptor to include token from localStorage
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

export default api;
